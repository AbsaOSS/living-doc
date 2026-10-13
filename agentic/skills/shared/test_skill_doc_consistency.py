#!/usr/bin/env python3
"""
Consistency tests for statements a SKILL.md makes about itself.

Each check below guards a defect the iteration-2 baseline eval run found in a skill's own text —
an example that contradicts a rule stated a few lines above it, or an instruction that makes a
model invent a value it does not have. A model follows the example over the rule, so the text is
the defect; no eval assertion catches it reliably, because both arms read the same contradiction.

  * gherkin-step showed behave hooks as decorators and Cucumber steps with a playwright-bdd
    `async ({ fixture })` signature — both ruled out by the skill's own framework-scope note.
  * data-cy-instrument's WORK_LOG example carried a concrete-looking `issues/XXXX` link, which
    answers copied as a real issue URL.
  * Every skill that allocates IDs with next_id.py must say what to do when it cannot run, and
    must forbid claiming a run that did not happen — create-functionality withheld a whole entity
    for want of a placeholder, and create-feature reported a validation run it never made.
  * living-doc-gap-finder's taxonomy named gap types in prose while reports must use the codes
    compute_gaps.py emits.
  * bdd-maintain's REMOVE procedure deleted scenarios, steps and PageObjects in steps 2-5 and only
    asked the user to confirm the deletion list in step 7.
"""
__test__ = False  # pytest: ignore this helper script

import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent
FENCE = re.compile(r"^```(\w*)\n(.*?)^```", re.M | re.S)


def _text(skill: str) -> str:
    return (SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8")


def _blocks(text: str, *langs: str):
    for m in FENCE.finditer(text):
        if not langs or m.group(1) in langs:
            yield text[: m.start()].count("\n") + 1, m.group(2)


def test_gherkin_step_examples_match_framework_scope():
    """behave hooks are found by name; @cucumber/cucumber steps take `function (this: World)`."""
    text = _text("gherkin-step")
    offenders = []
    for line, body in _blocks(text, "python"):
        for m in re.finditer(r"^\s*@(before|after)_\w+", body, re.M):
            offenders.append(f"gherkin-step/SKILL.md:{line}: behave decorator hook `{m.group(0).strip()}`")
    for line, body in _blocks(text, "typescript", "ts"):
        if re.search(r"async\s*\(\s*\{", body):
            offenders.append(f"gherkin-step/SKILL.md:{line}: playwright-bdd `async ({{ fixture }})` signature")
    assert not offenders, "example contradicts the skill's framework scope:\n  " + "\n  ".join(offenders)
    print("✓ gherkin-step examples use behave name hooks and Cucumber `this: World` steps")


def test_no_placeholder_issue_link_in_examples():
    """An example link shaped like a real issue (`issues/XXXX`, `issues/1234`) gets copied as one."""
    offenders = []
    for doc in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        for line, body in _blocks(doc.read_text(encoding="utf-8")):
            for m in re.finditer(r"issues/(?:X{2,}|\d+)\b", body):
                offenders.append(f"{doc.parent.name}/SKILL.md:{line}: {m.group(0)}")
    assert not offenders, (
        "example carries a concrete-looking issue link — use a visible placeholder such as "
        "`<library issue URL>`:\n  " + "\n  ".join(offenders)
    )
    print("✓ No example carries a made-up issue link")


def test_id_allocating_skills_cover_the_no_catalog_case():
    """A skill that runs next_id.py names a *-PENDING placeholder and forbids claiming a fake run."""
    missing = []
    for doc in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = doc.read_text(encoding="utf-8")
        if "next_id.py" not in text:
            continue
        if not re.search(r"\b(?:US|FEAT|FUNC)-PENDING\b", text):
            missing.append(f"{doc.parent.name}: no *-PENDING placeholder for when next_id.py cannot run")
        if not re.search(r"only claim (?:a|the) (?:command|allocator) ran if it ran", text, re.I):
            missing.append(f"{doc.parent.name}: no 'only claim … ran if it ran' rule")
    assert not missing, "\n  ".join(["ID-allocating skill without its no-catalog guard:", *missing])
    print("✓ Every next_id.py skill names a placeholder and forbids claiming a fake run")


def test_create_functionality_never_withholds_for_unknown_parent():
    """An unknown parent Feature is a FEAT-PENDING placeholder, not a reason to emit no JSON."""
    text = _text("living-doc-create-functionality")
    assert '"parent_feature": "FEAT-PENDING"' in text, "no FEAT-PENDING rule for an unresolved parent"
    assert "never a reason to withhold the entity" in text, "unresolved-parent rule no longer forbids withholding"
    print("✓ create-functionality drafts with FEAT-PENDING instead of withholding the entity")


def test_gap_finder_taxonomy_names_every_script_code():
    """Every gap code compute_gaps.py emits appears in the skill's taxonomy table."""
    script = (SKILLS_DIR / "living-doc-gap-finder" / "scripts" / "compute_gaps.py").read_text(encoding="utf-8")
    codes = set(re.findall(r'"((?:UNTESTED|PARTIALLY|UNDOCUMENTED|FEATURE_WITHOUT|ORPHAN|STALE)_[A-Z_]+)"', script))
    assert codes, "found no gap codes in compute_gaps.py — the pattern needs updating"
    table = "\n".join(l for l in _text("living-doc-gap-finder").splitlines() if l.startswith("| "))
    missing = sorted(c for c in codes if f"`{c}`" not in table)
    assert not missing, "gap code missing from the taxonomy table: " + ", ".join(missing)
    print(f"✓ All {len(codes)} compute_gaps.py gap codes are named in the taxonomy table")


def test_bdd_maintain_confirms_before_it_deletes():
    """In the REMOVE procedure, the user confirms a deletion list before any file is touched."""
    text = _text("bdd-maintain")
    start, end = text.find("1. Identify the specific Feature/US/AC being removed."), text.find("8. If any child entities")
    assert 0 <= start < end, "REMOVE procedure not found — update this test with the section's new wording"
    steps = text[start:end].split("\n", 1)[1]  # step 1 only names what is being removed
    confirm = re.search(r"\bconfirm", steps, re.I)
    destroy = re.search(r"\b(remove|delete)\b", steps, re.I)
    assert confirm and destroy and confirm.start() < destroy.start(), (
        "bdd-maintain REMOVE procedure removes or deletes files before asking the user to confirm the list"
    )
    print("✓ bdd-maintain asks for confirmation before it removes or deletes anything")


if __name__ == "__main__":
    try:
        test_gherkin_step_examples_match_framework_scope()
        test_no_placeholder_issue_link_in_examples()
        test_id_allocating_skills_cover_the_no_catalog_case()
        test_create_functionality_never_withholds_for_unknown_parent()
        test_gap_finder_taxonomy_names_every_script_code()
        test_bdd_maintain_confirms_before_it_deletes()
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
