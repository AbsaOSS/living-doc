#!/usr/bin/env python3
"""
Documented-command tests for every SKILL.md in this layer.

A skill's body is the only instruction an author or a model gets, so a command printed there
has to resolve as written. Two ways it silently does not, both found by the iteration-1 baseline
eval run across seven of the twelve skills:

  * `python scripts/x.py` reads as relative to the author's working directory, where no
    `scripts/` exists — the real file sits inside the skill's own directory.
  * `python skills/<other>/scripts/x.py` and `python agentic/skills/<other>/scripts/x.py` are
    paths that only exist in this repository's checkout. A skill installs as a self-contained
    directory alongside its siblings (`npx skills add … --skill <name>`, see agentic/README.md),
    so neither prefix survives installation.

The form that holds in both layouts is the one this test enforces: a skill's own script as
`scripts/x.py`, another installed skill's as `../<skill-name>/scripts/x.py`. Both resolve
relative to the skill directory in a checkout and after an install.

No eval assertion can cover this — it is a fact about the text, not about a model's answer —
so it is checked here instead.
"""
__test__ = False  # pytest: ignore this helper script

import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent
OWN = re.compile(r"(?<![\w./-])scripts/([a-z0-9_]+\.py)")
SIBLING = re.compile(r"\.\./([a-z0-9-]+)/scripts/([a-z0-9_]+\.py)")
# Prefixes that resolve only inside this checkout, or nowhere at all.
REPO_BOUND = re.compile(r"(?<![\w./-])(?:agentic/)?skills/[a-z0-9-]+/scripts/[a-z0-9_]+\.py")


def _skill_docs():
    docs = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    assert docs, f"no SKILL.md found under {SKILLS_DIR}"
    return docs


def test_no_repo_bound_script_paths():
    """A `skills/…` or `agentic/skills/…` path breaks as soon as the skill is installed."""
    offenders = []
    for doc in _skill_docs():
        for line_no, line in enumerate(doc.read_text().splitlines(), 1):
            for m in REPO_BOUND.finditer(line):
                offenders.append(f"{doc.parent.name}/SKILL.md:{line_no}: {m.group(0)}")
    assert not offenders, (
        "repository-bound script path(s) — use `scripts/x.py` for the skill's own script and "
        "`../<skill-name>/scripts/x.py` for another skill's:\n  " + "\n  ".join(offenders)
    )
    print(f"✓ No repository-bound script paths in {len(_skill_docs())} SKILL.md file(s)")


def test_own_script_paths_exist():
    """`scripts/x.py` must name a file inside that same skill's directory."""
    missing, checked = [], 0
    for doc in _skill_docs():
        for line_no, line in enumerate(doc.read_text().splitlines(), 1):
            for m in OWN.finditer(line):
                checked += 1
                if not (doc.parent / "scripts" / m.group(1)).is_file():
                    missing.append(f"{doc.parent.name}/SKILL.md:{line_no}: scripts/{m.group(1)}")
    assert not missing, "documented script does not exist in its own skill:\n  " + "\n  ".join(missing)
    print(f"✓ All {checked} own-skill script reference(s) resolve")


def test_sibling_script_paths_exist():
    """`../<skill>/scripts/x.py` must name a real script in a real sibling skill."""
    missing, checked = [], 0
    for doc in _skill_docs():
        for line_no, line in enumerate(doc.read_text().splitlines(), 1):
            for m in SIBLING.finditer(line):
                checked += 1
                target = SKILLS_DIR / m.group(1) / "scripts" / m.group(2)
                if not target.is_file():
                    missing.append(
                        f"{doc.parent.name}/SKILL.md:{line_no}: ../{m.group(1)}/scripts/{m.group(2)}"
                    )
    assert not missing, "documented sibling script does not exist:\n  " + "\n  ".join(missing)
    print(f"✓ All {checked} sibling-skill script reference(s) resolve")


def test_skill_with_commands_states_the_path_convention():
    """`scripts/x.py` is ambiguous on its own, so each such skill says what it is relative to."""
    silent = []
    for doc in _skill_docs():
        text = doc.read_text()
        if not (OWN.search(text) or SIBLING.search(text)):
            continue
        if "Script paths are relative to this skill" not in text:
            silent.append(doc.parent.name)
    assert not silent, (
        "skill documents a script path but never says it is relative to the skill's own "
        "directory: " + ", ".join(silent)
    )
    print("✓ Every skill documenting a script states the path convention")


def test_no_flag_documented_that_the_script_rejects():
    """A documented flag the script's parser does not accept dies on argument parsing.

    Kept narrow on purpose: it checks the long options named in a SKILL.md command for a script
    that lives in this layer, against the `add_argument` calls in that script. `scan_ac_links.py`
    was documented with a `--catalog` option it never had and `manifest_diff.py` with
    `--pages-dir` / `--diff`, so in both cases the printed command could not run.

    A script that only forwards to the shared library (`next_id.py` → `living_doc_id.cli_main`)
    declares no arguments of its own, so its flags are read from the module it delegates to. When
    neither the script nor a resolvable delegate declares any argument, the script is skipped
    rather than guessed at — a check that cannot see the parser must not invent a verdict.
    """
    def accepted_flags(script: Path) -> set[str] | None:
        text = script.read_text()
        flags = set(re.findall(r"add_argument\(\s*[\"'](--[a-z0-9-]+)", text))
        if flags:
            return flags
        for mod in re.findall(r"from\s+([a-z0-9_]+)\s+import\s+[\w,\s]*cli_main", text):
            delegate = SKILLS_DIR / "shared" / "lib" / f"{mod}.py"
            if delegate.is_file():
                d = set(re.findall(r"add_argument\(\s*[\"'](--[a-z0-9-]+)", delegate.read_text()))
                if d:
                    return d
        return None  # no parser visible — not checkable

    offenders, skipped = [], set()
    for doc in _skill_docs():
        text = doc.read_text()
        for m in re.finditer(
            r"(?:\.\./([a-z0-9-]+)/)?scripts/([a-z0-9_]+\.py)((?:[^\n`]|\\\n)*)", text
        ):
            skill_dir = SKILLS_DIR / (m.group(1) or doc.parent.name)
            script = skill_dir / "scripts" / m.group(2)
            if not script.is_file():
                continue
            accepted = accepted_flags(script)
            if accepted is None:
                skipped.add(m.group(2))
                continue
            for flag in set(re.findall(r"(--[a-z][a-z0-9-]+)", m.group(3))):
                if flag not in accepted:
                    offenders.append(f"{doc.parent.name}/SKILL.md: {m.group(2)} {flag}")
    assert not offenders, (
        "documented flag that the script's parser does not accept:\n  " + "\n  ".join(sorted(set(offenders)))
    )
    note = f" ({len(skipped)} script(s) skipped: no visible parser)" if skipped else ""
    print(f"✓ No SKILL.md documents a flag its script rejects{note}")


if __name__ == "__main__":
    try:
        test_no_repo_bound_script_paths()
        test_own_script_paths_exist()
        test_sibling_script_paths_exist()
        test_skill_with_commands_states_the_path_convention()
        test_no_flag_documented_that_the_script_rejects()
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
