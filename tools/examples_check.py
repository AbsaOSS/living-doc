#!/usr/bin/env python3
#
# Copyright 2026 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Validate the ``docs/examples/`` corpus against the canonical living-doc formats.

This is the *grammar + cross-reference* gate for the copyable input corpus:

1. **Header-block grammar** — every feature-file / PageObject / issue-body / project-profile
   example carries the fields its canonical guide marks required, and every
   ``AC:<id> (v<version> - <state>)`` line matches the glossary grammar.
2. **Cross-corpus identifier consistency** — the corpus declares exactly ``US-001`` /
   ``FEAT-001`` / ``FUNC-001``; every parent link and every ``@AC:`` scenario tag
   (including the ``@AC:<id>/aspect:<value>`` form) resolves to something declared.
3. **Coverage-pair invariant** — across the two feature files at least one declared AC is
   covered by a scenario and at least one is left uncovered.

Canonical references:
  docs/guides/living-doc-header-types.md
  docs/guides/living-doc-glossary.md
  docs/examples/README.md  (GitHub issue-body layout)

The script depends only on the standard library plus PyYAML. It has no import-time
dependency on ``collector-gh`` or ``toolkit``. It exits non-zero on any violation and
prints, per finding, the file, the line (where known), the failed rule and a fix hint.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# --- vocabularies, mirrored from the canonical guides -------------------------------------
# docs/guides/living-doc-header-types.md#project-profile-config-driven-conventions
AC_STATES = ["planned", "in_review", "active", "deprecated"]
PAGEOBJECT_STATUSES = ["planned", "candidate", "active", "deprecated"]
# docs/guides/living-doc-header-types.md#3-functionality-in-a-gherkin-feature-file
FUNC_TYPES = [
    "component_state",
    "component_action",
    "button_action",
    "field_validation",
    "calculation",
    "visibility",
    "navigation_rule",
]
# docs/guides/living-doc-header-types.md#required-fields (PageObject)
SURFACE_TYPES = ["UI", "API", "Service", "Worker", "Module", "Library"]

# docs/guides/living-doc-glossary.md#acceptance-criterion-ac
#   AC:<parent-id>-<nn> (v<version> - <State>)          e.g. AC:US-001-01 (v1.0.0 - active)
#   AC:<parent-id>-<nn> (v<version> - deprecated - removal planned v<version>)
AC_HEADER_RE = re.compile(
    r"^AC:(?P<id>[A-Z]+-\d+-\d+)\s+\("
    r"v(?P<version>\d+\.\d+\.\d+)\s*-\s*(?P<state>[a-z_]+)"
    r"(?P<removal>\s*-\s*removal planned v\d+\.\d+\.\d+)?\)$"
)
ENTITY_ID_RE = re.compile(r"\b((?:US|FEAT|FUNC)-\d+)\b")
# @AC:<id>[/param:value] scenario tag — glossary "Tag format"
AC_TAG_RE = re.compile(r"@AC:(?P<id>[A-Z]+-\d+-\d+)(?:/(?P<param>[a-z_]+):(?P<value>[A-Za-z0-9-]+))?")

CANONICAL_ENTITIES = {"US-001", "FEAT-001", "FUNC-001"}

# docs/examples/README.md — GitHub issue-body layout table
ISSUE_HEADINGS = {
    "US": {
        "required": ["Description", "Business Value", "Acceptance Criteria"],
        "optional": ["Preconditions", "Not In Scope"],
    },
    "FEAT": {
        "required": [
            "Description",
            "Surface Type",
            "Owners",
            "Status",
            "User Stories",
            "Functionalities",
        ],
        "optional": ["External Dependencies"],
    },
    "FUNC": {
        "required": ["Description", "Parent Feature", "Func Type", "Acceptance Criteria"],
        "optional": ["Rationale", "Preconditions", "Not In Scope"],
    },
}
LABEL_TO_TYPE = {
    "DocumentedUserStory": "US",
    "DocumentedFeature": "FEAT",
    "DocumentedFunctionality": "FUNC",
}


@dataclass
class Finding:
    file: str
    line: int | None
    rule: str
    hint: str

    def __str__(self) -> str:
        where = f"{self.file}:{self.line}" if self.line else self.file
        return f"  {where}\n      rule: {self.rule}\n      fix:  {self.hint}"


class Corpus:
    """Accumulates what the whole corpus declares, for the cross-reference pass."""

    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.declared_entities: set[str] = set()          # from feature tags / PO + issue titles
        self.declared_acs: dict[str, set[str]] = {}       # ac id -> declared aspect values
        self.feature_file_acs: set[str] = set()           # ACs declared in the two .feature headers
        self.feature_file_covered: set[str] = set()       # ACs carrying a scenario in a .feature file
        self.entity_refs: list[tuple[str, str, int]] = [] # (referenced id, file, line)
        self.pending_ac_tags: list[tuple[str, str | None, str | None, str, int]] = []

    def fail(self, file: str, line: int | None, rule: str, hint: str) -> None:
        self.findings.append(Finding(file, line, rule, hint))

    def declare_ac(self, ac_id: str, aspects: set[str]) -> None:
        self.declared_acs.setdefault(ac_id, set()).update(aspects)


# --- shared helpers ---------------------------------------------------------------------

def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _decomment_block(raw_lines: list[str], strip_re: re.Pattern[str], stop_re: re.Pattern[str]
                     ) -> list[tuple[int, str]]:
    """Return ``(lineno, text)`` for the leading comment banner, de-commented, indent kept."""
    out: list[tuple[int, str]] = []
    for i, line in enumerate(raw_lines, 1):
        if stop_re.match(line):
            break
        m = strip_re.match(line)
        if m is None:
            if line.strip() == "":
                if out:
                    break
                continue
            break
        out.append((i, m.group(1)))
    return out


def _strip_annotation(text: str) -> str:
    """Drop the teaching annotations the corpus/guides append with a left-arrow marker."""
    return re.split(r"\s*(?:←|<-)\s", text, maxsplit=1)[0].strip()


def _is_banner(text: str) -> bool:
    t = text.strip()
    return t == "" or t.startswith("=") or t.startswith("LIVING DOC")


def _parse_ac_block(header: list[tuple[int, str]], corpus: Corpus, rel: str,
                    parent_id: str, states: list[str]) -> dict[str, set[str]]:
    """Walk a de-commented header, validating every ``AC:`` line, collecting aspects."""
    acs: dict[str, set[str]] = {}
    current: str | None = None
    for lineno, text in header:
        stripped = _strip_annotation(text.strip())
        if stripped.startswith("AC:"):
            current = None
            m = AC_HEADER_RE.match(stripped)
            if m is None:
                corpus.fail(rel, lineno, "AC line does not match the glossary grammar",
                            "use exactly 'AC:<id> (v<major.minor.patch> - <state>)' "
                            "(see living-doc-glossary.md#acceptance-criterion-ac)")
                continue
            current = m.group("id")
            acs.setdefault(current, set())
            if m.group("state") not in states:
                corpus.fail(rel, lineno,
                            f"AC state '{m.group('state')}' is not a documented state",
                            f"use one of {states} (project-profile ac_states)")
            if not current.startswith(parent_id + "-"):
                corpus.fail(rel, lineno,
                            f"AC id '{current}' does not belong to entity '{parent_id}'",
                            f"AC ids under {parent_id} must read '{parent_id}-<nn>'")
            has_removal = m.group("removal") is not None
            if m.group("state") == "deprecated" and not has_removal:
                corpus.fail(rel, lineno,
                            "deprecated AC is missing the 'removal planned v<version>' note",
                            "write 'AC:<id> (v<version> - deprecated - removal planned v<version>)' "
                            "(see living-doc-glossary.md#acceptance-criterion-ac)")
            if m.group("state") != "deprecated" and has_removal:
                corpus.fail(rel, lineno,
                            f"non-deprecated AC (state '{m.group('state')}') carries a "
                            "'removal planned' note",
                            "the removal note is only valid on a 'deprecated' AC")
        elif current is not None:
            am = re.match(r"-?\s*Aspect:\s*(.+)$", stripped)
            if am:
                acs[current].update(v.strip() for v in am.group(1).split(",") if v.strip())
    return acs


# --- feature files --------------------------------------------------------------------

FEATURE_STRIP_RE = re.compile(r"^\s*#\s?(.*)$")
FEATURE_STOP_RE = re.compile(r"^\s*@")

REQUIRED_FEATURE_KEYS = {
    "US": ["status", "business_value", "acceptance_criteria"],
    "FUNC": ["status", "parent", "func_type", "acceptance_criteria"],
}


def check_feature_file(path: Path, root: Path, corpus: Corpus) -> None:
    rel = _rel(path, root)
    raw = path.read_text(encoding="utf-8").splitlines()
    kind = "US" if "/liv_doc_us/" in rel or "us-" in path.name else "FUNC"

    header = _decomment_block(raw, FEATURE_STRIP_RE, FEATURE_STOP_RE)
    if not header:
        corpus.fail(rel, 1, "no leading '# ' living-doc header block",
                    "add the '# LIVING DOC — ...' comment banner from living-doc-header-types.md")
        return

    top_keys: dict[str, int] = {}
    for lineno, text in header:
        if _is_banner(text) or text[:1] in (" ", "\t"):
            continue
        km = re.match(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", text)
        if km:
            top_keys.setdefault(km.group(1), lineno)

    for key in REQUIRED_FEATURE_KEYS[kind]:
        if key not in top_keys:
            corpus.fail(rel, 1, f"required header field '{key}:' missing for a {kind} entity",
                        f"add '# {key}:' — see living-doc-header-types.md "
                        f"({'User Story' if kind == 'US' else 'Functionality'} header fields)")

    if "status" in top_keys:
        status_line = next(t for ln, t in header if ln == top_keys["status"])
        value = _strip_annotation(status_line.split(":", 1)[1])
        if value and value not in AC_STATES:
            corpus.fail(rel, top_keys["status"], f"status '{value}' is not a documented state",
                        f"use one of {AC_STATES}")
    if kind == "FUNC" and "func_type" in top_keys:
        ft_line = next(t for ln, t in header if ln == top_keys["func_type"])
        value = _strip_annotation(ft_line.split(":", 1)[1])
        if value and value not in FUNC_TYPES:
            corpus.fail(rel, top_keys["func_type"], f"func_type '{value}' is not documented",
                        f"use one of {FUNC_TYPES}")

    # feature-level id tag: @US_ID:US-001 / @FUNC_ID:FUNC-001
    id_tag = "US_ID" if kind == "US" else "FUNC_ID"
    entity_id: str | None = None
    for i, line in enumerate(raw, 1):
        m = re.match(rf"@{id_tag}:((?:US|FEAT|FUNC)-\d+)\b", line.strip())
        if m:
            entity_id = m.group(1)
            break
    if entity_id is None:
        corpus.fail(rel, 1, f"missing feature-level '@{id_tag}:<id>' tag",
                    f"add '@{id_tag}:{kind}-<nnn>' immediately above 'Feature:'")
        parent_for_ac = kind + "-000"
    else:
        corpus.declared_entities.add(entity_id)
        parent_for_ac = entity_id

    acs = _parse_ac_block(header, corpus, rel, parent_for_ac, AC_STATES)
    if "acceptance_criteria" in top_keys and not acs:
        corpus.fail(rel, top_keys["acceptance_criteria"],
                    "acceptance_criteria block declares no AC lines",
                    "add at least one 'AC:<id> (v<version> - <state>)' line")
    for ac_id, aspects in acs.items():
        corpus.declare_ac(ac_id, aspects)
        corpus.feature_file_acs.add(ac_id)

    # scenario tags
    for i, line in enumerate(raw, 1):
        s = line.strip()
        if not s.startswith("@"):
            continue
        for m in AC_TAG_RE.finditer(s):
            corpus.feature_file_covered.add(m.group("id"))
            corpus.pending_ac_tags.append(
                (m.group("id"), m.group("param"), m.group("value"), rel, i))

    if entity_id == "FUNC-001" or kind == "FUNC":
        for i, line in enumerate(raw, 1):
            pm = re.match(r"#\s?parent:\s*((?:US|FEAT|FUNC)-\d+)", line.strip())
            if pm:
                corpus.entity_refs.append((pm.group(1), rel, i))


# --- PageObject ----------------------------------------------------------------------

REQUIRED_PO_KEYS = ["surface_type", "status", "user_stories", "functionalities", "page-object"]


def check_pageobject(path: Path, root: Path, corpus: Corpus) -> None:
    rel = _rel(path, root)
    raw = path.read_text(encoding="utf-8").splitlines()

    header: list[tuple[int, str]] = []
    for i, line in enumerate(raw, 1):
        header.append((i, re.sub(r"^\s*(?:/\*+|\*+/?)?\s?", "", line).rstrip()))
        if "*/" in line:
            break
    if not any("LIVING DOC" in t for _, t in header):
        corpus.fail(rel, 1, "no leading '/* ... */' living-doc header banner",
                    "open the file with the '/* LIVING DOC — FEAT-<nnn> ... */' block")
        return

    keys: dict[str, tuple[int, str]] = {}
    for lineno, text in header:
        km = re.match(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.+?)\s*$", text)
        if km:
            keys.setdefault(km.group(1), (lineno, _strip_annotation(km.group(2))))

    for key in REQUIRED_PO_KEYS:
        if key not in keys:
            corpus.fail(rel, 1, f"required PageObject header field '{key}:' missing",
                        "see living-doc-header-types.md#required-fields "
                        "(Feature in a PageObject File)")

    if "surface_type" in keys and keys["surface_type"][1] not in SURFACE_TYPES:
        corpus.fail(rel, keys["surface_type"][0],
                    f"surface_type '{keys['surface_type'][1]}' is not documented",
                    f"use one of {SURFACE_TYPES}")

    status = keys.get("status", (1, ""))[1]
    if status and status not in PAGEOBJECT_STATUSES:
        corpus.fail(rel, keys["status"][0], f"status '{status}' is not a documented surface status",
                    f"use one of {PAGEOBJECT_STATUSES}")
    if status and status != "active" and "stub-reason" not in keys:
        corpus.fail(rel, keys.get("status", (1, ""))[0],
                    f"status '{status}' requires a 'stub-reason:' field",
                    "add a one-line 'stub-reason:' explaining why the surface is not yet active")

    for _, banner in header:
        bm = re.search(r"LIVING DOC\s+[—-]\s+(FEAT-\d+)", banner)
        if bm:
            corpus.declared_entities.add(bm.group(1))
            break

    for key in ("user_stories", "functionalities"):
        if key in keys:
            lineno, value = keys[key]
            for rid in ENTITY_ID_RE.findall(value):
                corpus.entity_refs.append((rid, rel, lineno))


# --- issue bodies -------------------------------------------------------------------

def check_issue_body(path: Path, root: Path, corpus: Corpus) -> None:
    rel = _rel(path, root)
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    label_m = re.search(r"Label:\s*(\w+)", raw)
    title_m = re.search(r"Title:\s*((?:US|FEAT|FUNC)-\d+)", raw)
    if not label_m or label_m.group(1) not in LABEL_TO_TYPE:
        corpus.fail(rel, 1, "issue header comment has no recognised 'Label:' value",
                    "add 'Label: DocumentedUserStory|DocumentedFeature|DocumentedFunctionality'")
        return
    etype = LABEL_TO_TYPE[label_m.group(1)]
    if not title_m:
        corpus.fail(rel, 1, "issue header comment has no 'Title: <ID> ...' entity id",
                    "add 'Title: <US|FEAT|FUNC>-<nnn> · <name>'")
    else:
        corpus.declared_entities.add(title_m.group(1))

    headings: list[tuple[int, str]] = []
    sub_headings: list[tuple[int, str]] = []
    for i, line in enumerate(lines, 1):
        h2 = re.match(r"##\s+(.+?)\s*$", line)
        h3 = re.match(r"###\s+(.+?)\s*$", line)
        if h3:
            sub_headings.append((i, h3.group(1)))
        elif h2:
            headings.append((i, h2.group(1)))

    spec = ISSUE_HEADINGS[etype]
    allowed = set(spec["required"]) | set(spec["optional"])
    present = {h for _, h in headings}
    for i, h in headings:
        if h not in allowed:
            corpus.fail(rel, i, f"'## {h}' is not a heading in the {etype} issue-body layout",
                        f"allowed headings: {sorted(allowed)} (docs/examples/README.md)")
    for req in spec["required"]:
        if req not in present:
            corpus.fail(rel, 1, f"required '## {req}' heading missing for a {etype} issue body",
                        "see the GitHub issue-body layout table in docs/examples/README.md")

    # AC sub-headings share the glossary grammar
    if "Acceptance Criteria" in present:
        for i, sub in sub_headings:
            if not AC_HEADER_RE.match(sub.strip()):
                corpus.fail(rel, i, f"AC sub-heading '### {sub}' does not match the glossary grammar",
                            "use '### AC:<id> (v<version> - <state>)'")
            else:
                ac_id = AC_HEADER_RE.match(sub.strip()).group("id")
                corpus.declare_ac(ac_id, set())

    # parent references carried in issue-body sections
    section = None
    for i, line in enumerate(lines, 1):
        h2 = re.match(r"##\s+(.+?)\s*$", line)
        if h2:
            section = h2.group(1)
            continue
        if section in ("Parent Feature", "User Stories", "Functionalities"):
            for rid in ENTITY_ID_RE.findall(line):
                corpus.entity_refs.append((rid, rel, i))


# --- project profile ---------------------------------------------------------------

REQUIRED_PROFILE_KEYS = [
    "test_id_attribute",
    "feature_dirs",
    "paths",
    "ac_states",
    "pageobject_statuses",
    "scenario_conventions",
    "manifest_shape",
]


def check_project_profile(path: Path, root: Path, corpus: Corpus) -> None:
    rel = _rel(path, root)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        corpus.fail(rel, getattr(getattr(exc, "problem_mark", None), "line", 0) + 1,
                    "project profile is not valid YAML", str(exc).splitlines()[0])
        return
    if not isinstance(data, dict):
        corpus.fail(rel, 1, "project profile does not parse to a YAML mapping",
                    "top level must be 'key: value' pairs")
        return
    for key in REQUIRED_PROFILE_KEYS:
        if key not in data:
            corpus.fail(rel, 1, f"project-profile key '{key}' missing",
                        "see living-doc-header-types.md#project-profile-config-driven-conventions")
    fd = data.get("feature_dirs")
    if isinstance(fd, dict):
        for sub in ("user_story", "functionality"):
            if sub not in fd:
                corpus.fail(rel, 1, f"feature_dirs.{sub} missing",
                            "feature_dirs needs both 'user_story' and 'functionality'")


def check_plain_yaml(path: Path, root: Path, corpus: Corpus) -> None:
    rel = _rel(path, root)
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        corpus.fail(rel, 1, "file is not valid YAML", str(exc).splitlines()[0])


# --- cross-corpus + coverage passes ----------------------------------------------

def cross_reference(corpus: Corpus) -> None:
    if corpus.declared_entities != CANONICAL_ENTITIES:
        extra = sorted(corpus.declared_entities - CANONICAL_ENTITIES)
        missing = sorted(CANONICAL_ENTITIES - corpus.declared_entities)
        corpus.fail("docs/examples/", None,
                    f"corpus must declare exactly {sorted(CANONICAL_ENTITIES)}",
                    f"unexpected: {extra or 'none'}; not declared: {missing or 'none'}")

    for rid, rel, line in corpus.entity_refs:
        if rid not in corpus.declared_entities:
            corpus.fail(rel, line, f"reference to '{rid}' has no matching entity in the corpus",
                        "point it at US-001 / FEAT-001 / FUNC-001, or add the entity")

    for ac_id, param, value, rel, line in corpus.pending_ac_tags:
        if ac_id not in corpus.declared_acs:
            corpus.fail(rel, line, f"@AC:{ac_id} tag names an AC that no entity declares",
                        "declare the AC in an acceptance_criteria block, or fix the tag id")
            continue
        if param == "aspect" and value not in corpus.declared_acs[ac_id]:
            corpus.fail(rel, line,
                        f"@AC:{ac_id}/aspect:{value} — '{value}' is not a declared Aspect of {ac_id}",
                        f"declared aspects: {sorted(corpus.declared_acs[ac_id]) or 'none'} "
                        "(add it to the AC's '- Aspect:' line)")


def coverage_pair(corpus: Corpus) -> None:
    covered = corpus.feature_file_acs & corpus.feature_file_covered
    uncovered = corpus.feature_file_acs - corpus.feature_file_covered
    if not covered:
        corpus.fail("docs/examples/gherkin/", None,
                    "coverage-pair invariant: no declared AC is covered by a scenario",
                    "give at least one AC a '@AC:<id>' scenario across the feature files")
    if not uncovered:
        corpus.fail("docs/examples/gherkin/", None,
                    "coverage-pair invariant: every declared AC is covered — none left uncovered",
                    "leave at least one declared AC without a scenario "
                    "(the corpus is a coverage-matrix input and must show both verdicts)")


# --- driver ----------------------------------------------------------------------

def check_corpus(examples_dir: Path) -> list[Finding]:
    root = examples_dir.parent.parent  # <repo>/docs/examples -> <repo>
    corpus = Corpus()

    if not examples_dir.is_dir():
        corpus.fail(_rel(examples_dir, root), None, "docs/examples directory not found",
                    "run from the repo root, or pass --examples-dir")
        return corpus.findings

    for feature in sorted(examples_dir.glob("gherkin/**/*.feature")):
        check_feature_file(feature, root, corpus)
    for po in sorted(examples_dir.glob("pageobject/*.ts")):
        check_pageobject(po, root, corpus)
    for issue in sorted(examples_dir.glob("gh-issues/*.md")):
        check_issue_body(issue, root, corpus)

    profile = examples_dir / "project-profile" / ".project-profile.yaml"
    if profile.is_file():
        check_project_profile(profile, root, corpus)
    else:
        corpus.fail("docs/examples/project-profile/.project-profile.yaml", None,
                    "canonical project-profile example is missing",
                    "add project-profile/.project-profile.yaml (referenced by docs/examples/README.md)")
    for extra_yaml in sorted(examples_dir.glob("project-profile/*.yaml")):
        if extra_yaml.name != ".project-profile.yaml":
            check_plain_yaml(extra_yaml, root, corpus)

    cross_reference(corpus)
    coverage_pair(corpus)
    return corpus.findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    default_dir = Path(__file__).resolve().parent.parent / "docs" / "examples"
    parser.add_argument("--examples-dir", type=Path, default=default_dir,
                        help="path to the docs/examples corpus (default: %(default)s)")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass

    findings = check_corpus(args.examples_dir.resolve())
    if not findings:
        print("docs/examples corpus: OK — grammar and cross-references validate.")
        return 0

    print(f"docs/examples corpus: {len(findings)} violation(s)\n")
    for finding in findings:
        print(finding)
        print()
    print("See docs/guides/living-doc-header-types.md and living-doc-glossary.md for the formats.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
