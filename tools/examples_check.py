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
   ``AC:<id> (v<version> - <state>)`` / ``AC:<id> (planned)`` line matches the glossary
   grammar.
2. **Cross-corpus identifier consistency** — the corpus declares exactly ``US-001`` /
   ``FEAT-001`` / ``FUNC-001``; every parent link and every ``@AC:`` scenario tag
   (including the ``@AC:<id>/aspect:<value>`` form) resolves to something declared.
3. **Coverage-pair invariant** — across the two feature files at least one declared AC is
   covered by a scenario and at least one is left uncovered.
4. **Canonical form** (``NON_CANONICAL_FORM``) — the corpus is canonical-only: structural
   positions use ``-`` (hyphen-minus), never an en or em dash. Non-canonical variants are
   test data for the normalisation layer in ``living-doc-utilities``, not corpus content.
5. **Form parity** (``PAIR_MISMATCH``) — the two authored forms of an entity (issue body and
   source-code header) agree on required content and on their AC set, and no single file
   carries more than one optional field extension.

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
#   AC:<parent-id>-<nn> (v<version> - <state>)          e.g. AC:US-001-01 (v1.0.0 - active)
#   AC:<parent-id>-<nn> (planned)                       backlog: no target version
#   AC:<parent-id>-<nn> (v<version> - deprecated - removal planned v<version>)
# The version group is optional in the pattern so a version-less non-`planned` AC is reported
# as the specific rule it breaks, not as a generic grammar failure.
AC_HEADER_RE = re.compile(
    r"^AC:(?P<id>[A-Z]+-\d+-\d+)\s+\("
    r"(?:v(?P<version>\d+\.\d+\.\d+)\s*-\s*)?(?P<state>[a-z_]+)"
    r"(?P<removal>\s*-\s*removal planned v\d+\.\d+\.\d+)?\)$"
)
ENTITY_ID_RE = re.compile(r"\b((?:US|FEAT|FUNC)-\d+)\b")
# @AC:<id>[/param:value] scenario tag — glossary "Tag format"
AC_TAG_RE = re.compile(r"@AC:(?P<id>[A-Z]+-\d+-\d+)(?:/(?P<param>[a-z_]+):(?P<value>[A-Za-z0-9-]+))?")

CANONICAL_ENTITIES = {"US-001", "FEAT-001", "FUNC-001"}

# docs/examples/README.md — GitHub issue-body layout table
# `## Status` is required for US and FUNC and has no place on a Feature: a Feature's state is
# derived from its Functionalities (docs/guides/living-doc-glossary.md#feature).
DEPRECATION_HEADINGS = ["Deprecated At", "Deprecation Reason", "Superseded By"]
ISSUE_HEADINGS = {
    "US": {
        "required": ["Description", "Status", "Business Value", "Acceptance Criteria"],
        "optional": ["Preconditions", "Not In Scope", *DEPRECATION_HEADINGS],
    },
    "FEAT": {
        "required": [
            "Description",
            "Surface Type",
            "Owners",
            "User Stories",
            "Functionalities",
        ],
        "optional": ["External Dependencies", *DEPRECATION_HEADINGS],
    },
    "FUNC": {
        "required": [
            "Description",
            "Status",
            "Parent Feature",
            "Func Type",
            "Acceptance Criteria",
        ],
        "optional": ["Rationale", "Preconditions", "Not In Scope", *DEPRECATION_HEADINGS],
    },
}
# `## Status` on a Feature gets its own message rather than the generic "unknown heading" one.
FORBIDDEN_ISSUE_HEADINGS = {"FEAT": {"Status"}}

# docs/guides/living-doc-glossary.md — "Canonical form and normalisation". Structural positions
# use `-` (hyphen-minus); an en or em dash there is an autocorrect defect, not an input variant.
_DASHES = "–—"  # en dash, em dash
NON_CANONICAL_PATTERNS = [
    (re.compile(rf"AC:.*[{_DASHES}]"),
     "en/em dash on an 'AC:' line (AC header, '### AC:' sub-heading or '# AC:' comment)"),
    (re.compile(rf"^\s*(#\s*)?[{_DASHES}] "),
     "en/em dash used as a bullet marker"),
    (re.compile(rf"(US|FEAT|FUNC)-\d+ · .*[{_DASHES}]"),
     "en/em dash inside an entity name following its id"),
    (re.compile(rf"^\s*Feature:.*[{_DASHES}]"),
     "en/em dash inside the entity name on a Gherkin 'Feature:' line"),
]

# The two authored forms of one entity must agree on required content. Each row maps an
# issue-body heading to the key carrying the same fact in the source-code header form.
PAIR_FIELD_MAP = {
    "US": {"Description": "narrative", "Status": "status", "Business Value": "business_value"},
    "FUNC": {"Description": "narrative", "Status": "status",
             "Parent Feature": "parent", "Func Type": "func_type"},
    "FEAT": {"Description": "purpose", "Surface Type": "surface_type", "Owners": "owners",
             "User Stories": "user_stories", "Functionalities": "functionalities"},
}
# Optional extensions a `.feature` header may carry, beyond the required keys.
OPTIONAL_FEATURE_KEYS = ["source", "rationale", "preconditions", "not_in_scope",
                         "deprecated_at", "deprecation_reason", "superseded_by"]
OPTIONAL_PO_KEYS = ["wizard-steps", "stub-reason"]
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
        # entity id -> form name -> {"file", "fields", "acs", "optional"} (PAIR_MISMATCH pass)
        self.forms: dict[str, dict[str, dict]] = {}

    def declare_form(self, entity_id: str, form: str, file: str, fields: dict[str, str],
                     acs: dict[str, str], optional: list[str]) -> None:
        self.forms.setdefault(entity_id, {})[form] = {
            "file": file, "fields": fields, "acs": acs, "optional": optional,
        }

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


def _collapse(value: str) -> str:
    """Whitespace-collapse a value so a wrapped bullet compares equal to a one-line one."""
    return " ".join(value.split())


def _is_banner(text: str) -> bool:
    t = text.strip()
    return t == "" or t.startswith("=") or t.startswith("LIVING DOC")


def _validate_ac_header(m: "re.Match[str]", corpus: Corpus, rel: str, lineno: int,
                        parent_id: str, states: list[str]) -> None:
    """Apply the glossary's state / version / removal-note rules to one matched AC header."""
    ac_id, state = m.group("id"), m.group("state")
    if state not in states:
        corpus.fail(rel, lineno, f"AC state '{state}' is not a documented state",
                    f"use one of {states} (project-profile ac_states)")
    if not ac_id.startswith(parent_id + "-"):
        corpus.fail(rel, lineno, f"AC id '{ac_id}' does not belong to entity '{parent_id}'",
                    f"AC ids under {parent_id} must read '{parent_id}-<nn>'")
    if m.group("version") is None and state != "planned":
        corpus.fail(rel, lineno, f"AC in state '{state}' carries no version",
                    "a version is required in every state except 'planned'; write "
                    "'AC:<id> (v<major.minor.patch> - <state>)', or '(planned)' for a backlog AC")
    has_removal = m.group("removal") is not None
    if state == "deprecated" and not has_removal:
        corpus.fail(rel, lineno,
                    "deprecated AC is missing the 'removal planned v<version>' note",
                    "write 'AC:<id> (v<version> - deprecated - removal planned v<version>)' "
                    "(see living-doc-glossary.md#acceptance-criterion-ac)")
    if state != "deprecated" and has_removal:
        corpus.fail(rel, lineno,
                    f"non-deprecated AC (state '{state}') carries a 'removal planned' note",
                    "the removal note is only valid on a 'deprecated' AC")


def _parse_ac_block(header: list[tuple[int, str]], corpus: Corpus, rel: str,
                    parent_id: str, states: list[str],
                    headers: dict[str, str] | None = None,
                    extensions: set[str] | None = None) -> dict[str, set[str]]:
    """Walk a de-commented header, validating every ``AC:`` line, collecting aspects.

    ``headers`` collects the canonical ``AC:<id> (...)`` text per AC (the PAIR_MISMATCH pass
    compares AC sets by it); ``extensions`` collects the AC-level optional extensions used.
    """
    acs: dict[str, set[str]] = {}
    current: str | None = None
    for lineno, text in header:
        stripped = _strip_annotation(text.strip())
        if stripped.startswith("AC:"):
            current = None
            m = AC_HEADER_RE.match(stripped)
            if m is None:
                corpus.fail(rel, lineno, "AC line does not match the glossary grammar",
                            "use exactly 'AC:<id> (v<major.minor.patch> - <state>)', or "
                            "'AC:<id> (planned)' for a backlog AC "
                            "(see living-doc-glossary.md#acceptance-criterion-ac)")
                continue
            current = m.group("id")
            acs.setdefault(current, set())
            if headers is not None:
                headers[current] = stripped
            _validate_ac_header(m, corpus, rel, lineno, parent_id, states)
        elif current is not None:
            am = re.match(r"-?\s*Aspect:\s*(.+)$", stripped)
            if am:
                acs[current].update(v.strip() for v in am.group(1).split(",") if v.strip())
                if extensions is not None:
                    extensions.add("AC-level Aspect:")
            elif extensions is not None:
                sub = re.match(r"(preconditions|not_in_scope):$", stripped)
                if sub:
                    extensions.add(f"AC-level {sub.group(1)}:")
    return acs


# --- feature files --------------------------------------------------------------------

FEATURE_STRIP_RE = re.compile(r"^\s*#\s?(.*)$")
FEATURE_STOP_RE = re.compile(r"^\s*@")

REQUIRED_FEATURE_KEYS = {
    "US": ["status", "business_value", "acceptance_criteria"],
    "FUNC": ["status", "parent", "func_type", "acceptance_criteria"],
}


def _feature_narrative(raw: list[str]) -> str:
    """The prose under ``Feature:`` - the same fact the issue body puts under ``## Description``."""
    narrative: list[str] = []
    in_feature = False
    for line in raw:
        stripped = line.strip()
        if not in_feature:
            if stripped.startswith("Feature:"):
                in_feature = True
            continue
        if not stripped or stripped.startswith(("Scenario", "Background", "Rule:", "@", "#")):
            break
        narrative.append(stripped)
    return _collapse(" ".join(narrative))


def _feature_bullets(header: list[tuple[int, str]], start: int) -> str:
    """Join the bullet section opened at ``start``, unwrapping continuation lines."""
    items: list[str] = []
    collecting = False
    for lineno, text in header:
        if lineno == start:
            collecting = True
            continue
        if not collecting:
            continue
        stripped = text.strip()
        if not stripped:
            break
        if not text.startswith((" ", "\t")):
            break
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif items:
            items[-1] = f"{items[-1]} {stripped}"
    return _collapse(" ".join(items))


def _feature_pair_fields(header: list[tuple[int, str]], top_keys: dict[str, int],
                         raw: list[str], kind: str) -> dict[str, str]:
    """Required-content values of a ``.feature`` header, keyed as in ``PAIR_FIELD_MAP``."""
    fields: dict[str, str] = {"narrative": _feature_narrative(raw)}
    for key in PAIR_FIELD_MAP[kind].values():
        if key in ("narrative", "business_value") or key not in top_keys:
            continue
        line = next(t for ln, t in header if ln == top_keys[key])
        fields[key] = _collapse(_strip_annotation(line.split(":", 1)[1]))
    if "business_value" in top_keys:
        fields["business_value"] = _feature_bullets(header, top_keys["business_value"])
    return fields


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

    ac_headers: dict[str, str] = {}
    extensions: set[str] = set()
    acs = _parse_ac_block(header, corpus, rel, parent_for_ac, AC_STATES, ac_headers, extensions)
    if "acceptance_criteria" in top_keys and not acs:
        corpus.fail(rel, top_keys["acceptance_criteria"],
                    "acceptance_criteria block declares no AC lines",
                    "add at least one 'AC:<id> (v<version> - <state>)' line")
    for ac_id, aspects in acs.items():
        corpus.declare_ac(ac_id, aspects)
        corpus.feature_file_acs.add(ac_id)

    if entity_id is not None:
        fields = _feature_pair_fields(header, top_keys, raw, kind)
        extensions.update(f"{key}:" for key in OPTIONAL_FEATURE_KEYS if key in top_keys)
        corpus.declare_form(entity_id, "feature-file header", rel, fields,
                            ac_headers, sorted(extensions))

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

# docs/guides/living-doc-header-types.md#required-fields (Feature in a PageObject File)
REQUIRED_PO_KEYS_FULL = [
    "surface_type", "route", "owners", "purpose",
    "user_stories", "functionalities", "external_dependencies", "page-object",
]
# docs/guides/living-doc-header-types.md — Cross-reference header required fields
REQUIRED_PO_KEYS_XREF = ["parent-feat", "route", "owners", "purpose", "page-object"]


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

    is_xref = "parent-feat" in keys or any("[cross-reference]" in t for _, t in header)
    required = REQUIRED_PO_KEYS_XREF if is_xref else REQUIRED_PO_KEYS_FULL
    for key in required:
        if key not in keys:
            kind_note = "Cross-reference header" if is_xref else "Feature in a PageObject File"
            corpus.fail(rel, 1, f"required PageObject header field '{key}:' missing",
                        f"see living-doc-header-types.md#required-fields ({kind_note})")

    if "surface_type" in keys and keys["surface_type"][1] not in SURFACE_TYPES:
        corpus.fail(rel, keys["surface_type"][0],
                    f"surface_type '{keys['surface_type'][1]}' is not documented",
                    f"use one of {SURFACE_TYPES}")

    if "status" in keys:
        corpus.fail(rel, keys["status"][0], "PageObject header carries a 'status:' field",
                    "remove it - a surface has no status and a Feature's state is derived from "
                    "its Functionalities; an uninstrumented surface says so with 'stub-reason:' "
                    "(see living-doc-header-types.md#2-feature-in-a-pageobject-file)")

    entity_id: str | None = None
    for _, banner in header:
        bm = re.search(r"LIVING DOC\s+[—-]\s+(FEAT-\d+)", banner)
        if bm:
            entity_id = bm.group(1)
            corpus.declared_entities.add(entity_id)
            break
    if entity_id is not None and not is_xref:
        fields = {key: _collapse(keys[key][1]) for key in PAIR_FIELD_MAP["FEAT"].values()
                  if key in keys}
        corpus.declare_form(entity_id, "PageObject header", rel, fields, {},
                            [f"{key}:" for key in OPTIONAL_PO_KEYS if key in keys])

    for key in ("user_stories", "functionalities", "parent-feat"):
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
    forbidden = FORBIDDEN_ISSUE_HEADINGS.get(etype, set())
    present = {h for _, h in headings}
    for i, h in headings:
        if h in forbidden:
            corpus.fail(rel, i, f"'## {h}' has no place in the {etype} issue-body layout",
                        "a Feature has no authored status - its state is derived from its "
                        "Functionalities (living-doc-glossary.md#feature); remove the heading")
        elif h not in allowed:
            corpus.fail(rel, i, f"'## {h}' is not a heading in the {etype} issue-body layout",
                        f"allowed headings: {sorted(allowed)} (docs/examples/README.md)")
    for req in spec["required"]:
        if req not in present:
            corpus.fail(rel, 1, f"required '## {req}' heading missing for a {etype} issue body",
                        "see the GitHub issue-body layout table in docs/examples/README.md")

    sections = _issue_sections(lines)
    if "Status" in sections and sections["Status"] not in AC_STATES:
        corpus.fail(rel, 1, f"'## Status' value '{sections['Status']}' is not a documented state",
                    f"use one of {AC_STATES} (project-profile ac_states)")

    # AC sub-headings share the glossary grammar
    ac_headers: dict[str, str] = {}
    parent_id = title_m.group(1) if title_m else etype + "-000"
    if "Acceptance Criteria" in present:
        for i, sub in sub_headings:
            m = AC_HEADER_RE.match(sub.strip())
            if m is None:
                corpus.fail(rel, i, f"AC sub-heading '### {sub}' does not match the glossary grammar",
                            "use '### AC:<id> (v<version> - <state>)', or '### AC:<id> (planned)' "
                            "for a backlog AC")
                continue
            ac_headers[m.group("id")] = sub.strip()
            corpus.declare_ac(m.group("id"), set())
            _validate_ac_header(m, corpus, rel, i, parent_id, AC_STATES)

    if title_m:
        fields = {key: sections[heading]
                  for heading, key in PAIR_FIELD_MAP[etype].items() if heading in sections}
        corpus.declare_form(title_m.group(1), "issue body", rel, fields, ac_headers,
                            [f"## {h}" for h in spec["optional"] if h in present])

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


def _issue_sections(lines: list[str]) -> dict[str, str]:
    """Map each ``##`` heading to its body text, bullet markers stripped and whitespace collapsed."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        h2 = re.match(r"##\s+(.+?)\s*$", line)
        if h2:
            current = h2.group(1)
            sections.setdefault(current, [])
            continue
        if line.startswith("###"):
            current = None
            continue
        if current is not None and line.strip():
            sections[current].append(re.sub(r"^\s*-\s+", "", line).strip())
    return {name: _collapse(" ".join(body)) for name, body in sections.items()}


# --- project profile ---------------------------------------------------------------

REQUIRED_PROFILE_KEYS = [
    "test_id_attribute",
    "feature_dirs",
    "paths",
    "ac_states",
    "scenario_conventions",
    "manifest_shape",
]
# Retired with the PageObject `status:` field - a surface has no status vocabulary.
FORBIDDEN_PROFILE_KEYS = ["pageobject_statuses"]


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
    for key in FORBIDDEN_PROFILE_KEYS:
        if key in data:
            corpus.fail(rel, 1, f"project-profile key '{key}' is retired",
                        "remove it - a PageObject header carries no 'status:' field "
                        "(see living-doc-header-types.md#2-feature-in-a-pageobject-file)")
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


def check_canonical_form(path: Path, root: Path, corpus: Corpus) -> None:
    """NON_CANONICAL_FORM - the corpus is canonical-only.

    An en or em dash in a structural position is what the normalisation layer rewrites on
    input; the variants themselves are test data for ``living-doc-utilities``, never corpus
    content (docs/guides/living-doc-glossary.md - "Canonical form and normalisation").
    """
    rel = _rel(path, root)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return
    for i, line in enumerate(lines, 1):
        for pattern, what in NON_CANONICAL_PATTERNS:
            if pattern.search(line):
                corpus.fail(rel, i, f"NON_CANONICAL_FORM: {what}",
                            "use '-' (hyphen-minus) in structural positions - AC headers, AC "
                            "bullets, entity names and the '# AC:' separator "
                            "(see living-doc-glossary.md#acceptance-criterion-ac)")
                break


def form_parity(corpus: Corpus) -> None:
    """PAIR_MISMATCH - the two authored forms of an entity must say the same thing."""
    for entity_id, forms in sorted(corpus.forms.items()):
        for form in forms.values():
            if len(form["optional"]) > 1:
                corpus.fail(form["file"], None,
                            "PAIR_MISMATCH: file carries more than one optional field extension "
                            f"({', '.join(form['optional'])})",
                            "the corpus shows each extension once, in isolation - move the extra "
                            "one to the file the conventions table assigns it to "
                            "(docs/examples/README.md#conventions-used-by-this-corpus)")
        if len(forms) < 2:
            continue
        (name_a, a), (name_b, b) = sorted(forms.items())
        for field in sorted(set(a["fields"]) & set(b["fields"])):
            if a["fields"][field] != b["fields"][field]:
                corpus.fail(b["file"], None,
                            f"PAIR_MISMATCH: {entity_id} required content '{field}' differs "
                            f"between its two forms",
                            f"{name_a} ({a['file']}) says {a['fields'][field]!r}; "
                            f"{name_b} says {b['fields'][field]!r} - make them identical")
        if a["acs"] != b["acs"]:
            only_a = sorted(set(a["acs"].items()) - set(b["acs"].items()))
            only_b = sorted(set(b["acs"].items()) - set(a["acs"].items()))
            corpus.fail(b["file"], None,
                        f"PAIR_MISMATCH: {entity_id} declares a different AC set in its two forms",
                        f"only in {name_a} ({a['file']}): {[h for _, h in only_a] or 'none'}; "
                        f"only in {name_b}: {[h for _, h in only_b] or 'none'}")


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

    for any_file in sorted(examples_dir.rglob("*")):
        if any_file.is_file():
            check_canonical_form(any_file, root, corpus)

    cross_reference(corpus)
    form_parity(corpus)
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
