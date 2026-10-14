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
   example carries the fields its canonical guide marks required, and every ``AC:`` criterion
   parses with ``ac_grammar`` from ``living-doc-utilities`` - the grammar the collectors read it
   with. Every warning it raises (``MALFORMED_AC``, ``UNPARSED_AC_LINE``, ...) is a finding. A
   keyword's spelling - one lowercase kebab-case name, the same in the AC text and the bullet - is
   checked here, on the line as written: ``ac_grammar`` folds case, ``-``, ``_`` and space.
2. **Cross-corpus identifier consistency** — the corpus declares exactly ``US-001`` /
   ``FEAT-001`` / ``FUNC-001``; every parent link and every ``@AC:`` scenario tag
   resolves to something declared. A tag carries at most one ``/<param>:<value>`` segment, whose
   ``<param>`` is the AC's variant name (``aspect`` or its named keyword) and ``<value>`` one of
   its declared values; a bare ``@AC:<id>`` covers the whole AC. The name is read from the tag as
   written: the parsed link the pipeline builds keeps none.
3. **Coverage-pair invariant** — across the two feature files at least one declared AC is
   covered by a scenario and at least one is left uncovered.
4. **Canonical form** (``NON_CANONICAL_FORM``) — the corpus is canonical-only: no line of an
   entity file is one ``normalize`` from ``living-doc-utilities`` would rewrite (dashes, bullet
   markers, state case, version form, title separators). Non-canonical variants are test data
   for that normalisation layer, not corpus content.
5. **Form parity** (``PAIR_MISMATCH``) — the two authored forms of an entity (issue body and
   source-code header) agree on required content and on their AC set as ``ac_grammar`` parses
   it, and no single file carries more than one optional field extension per level. An ``API``
   Feature is the one entity with a single authored form: its contract anchor carries no
   living-doc header yet.
6. **Feature dependencies** — ``feature_dependencies`` is authored on a Feature only, as
   comma-separated ``FEAT-`` ids with no ``none`` value; every target resolves to a corpus
   entity, is not the declaring Feature itself, is an ``API`` Feature, and is not being retired.
7. **Indentation levels** — every ``.feature`` header, PageObject header and issue body uses the
   canonical levels, spaces only. Each line's indent is compared with the template level for its
   line kind; an item's kind is set by the key or ``AC:`` above it, and wrapped text is measured
   against the last ``- ``. No stack of open items is kept - that is the parsers' job in
   ``living-doc-utilities``. Valid non-canonical layouts, the flat one among them, are test data
   there, not corpus content.

Canonical references:
  docs/guides/living-doc-header-types.md
  docs/guides/living-doc-glossary.md
  docs/examples/README.md  (GitHub issue-body layout)

The script depends on the standard library, PyYAML and the authoring layer of
``living-doc-utilities`` (``normalize``, ``ac_grammar``, ``identity``), pinned in
``tools/requirements-examples-check.txt``. It has no import-time dependency on ``collector-gh``
or ``toolkit``. It exits non-zero on any violation and prints, per finding, the file, the line
(where known), the failed rule and a fix hint.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml
from living_doc_utilities.authoring import ac_grammar, normalize
from living_doc_utilities.authoring.identity import derive_entity_id, extract_living_doc_title
from living_doc_utilities.authoring.normalize import SourceFormat
from living_doc_utilities.contracts.common import AcceptanceCriterion

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
# docs/guides/living-doc-glossary.md#feature
SURFACE_TYPES = ["UI", "API"]

# The entity type `living-doc-utilities` parses each kind of entity as.
ENTITY_TYPES = {"US": "DocumentedUserStory", "FEAT": "DocumentedFeature",
                "FUNC": "DocumentedFunctionality"}

# docs/guides/living-doc-glossary.md#acceptance-criterion-ac - the AC header grammar, its states,
# version rule and id shape are `ac_grammar`'s; this script holds no copy of them.
# AC variants — header types "AC variants": the AC text names a keyword as `{<name>}`, and an
# AC-level `- <name>: <values>` bullet declares its values. `Aspect:` is the default keyword.
# `ac_grammar` folds a name's case, `-`, `_` and space; the canon's one spelling is checked here.
VARIANT_NAME_RE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
AC_PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")
AC_KEYWORD_BULLET_RE = re.compile(r"-\s*(?P<name>[A-Za-z][A-Za-z0-9 _-]*?):\s*(?P<values>\S.*)$")
# @AC:<id>[/<param>:<value>] scenario tag — glossary "Tag format". <param> is `aspect` or the AC's
# keyword name, lowercase kebab-case. A tag is matched whole, so a second `/<param>:<value>` fails;
# <id> is then checked with `ac_grammar.is_valid_ac_id`.
AC_TAG_RE = re.compile(rf"@AC:(?P<id>[^/\s]+)"
                       rf"(?:/(?P<param>{VARIANT_NAME_RE.pattern}):(?P<value>[A-Za-z0-9-]+))?")
# The fix hint for each warning `ac_grammar` raises on a criterion.
GRAMMAR_HINTS = {
    "MALFORMED_AC": "write 'AC:<id> (v<major.minor.patch> - <state>)', or 'AC:<id> (planned)' for a "
                    "backlog AC, with one variant declaration at most "
                    "(living-doc-glossary.md#acceptance-criterion-ac)",
    "UNPARSED_AC_LINE": "an AC-level bullet is the description, '- Aspect:', '- Rationale:' or the "
                        "one keyword the AC text names as '{<name>}' "
                        "(living-doc-header-types.md#ac-variants)",
    "MISINDENTED_LINE": "use the template levels (living-doc-header-types.md#indentation)",
}
GRAMMAR_HINT = ("fix the criterion this line belongs to - the pipeline drops a criterion it cannot "
                "read (living-doc-glossary.md#acceptance-criterion-ac)")

# `FEAT-003` declares a `feature_dependencies` edge to `FEAT-002`, the `API` Feature the corpus
# needs as a resolvable target (docs/examples/README.md, "The dependency pair").
CANONICAL_ENTITIES = {"US-001", "FEAT-001", "FEAT-002", "FEAT-003", "FUNC-001", "FUNC-002"}

# docs/examples/README.md — GitHub issue-body layout table. Why `## Status` and `## Deprecated At`
# have no FEAT row: docs/guides/living-doc-glossary.md#feature; the fix hints below say it to the
# author.
DEPRECATION_HEADINGS = ["Deprecated At", "Deprecation Reason", "Superseded By"]
FEAT_DEPRECATION_HEADINGS = ["Deprecation Reason", "Superseded By"]
# `## Notes` — entity-level human context, optional on every entity type
# (docs/guides/living-doc-glossary.md#core-entities).
NOTES_HEADING = "Notes"
# `## Feature Dependencies` — authored on the Feature only
# (docs/guides/living-doc-glossary.md#feature).
FEATURE_DEPS_HEADING = "Feature Dependencies"
FEATURE_DEPS_KEY = "feature_dependencies"
# Headings whose section holds ids, never a nested list item
# (docs/guides/living-doc-header-types.md#indentation).
ID_LIST_HEADINGS = ["User Stories", "Functionalities", FEATURE_DEPS_HEADING, "Parent Feature",
                    "Superseded By"]
ISSUE_HEADINGS = {
    "US": {
        "required": ["Description", "Status", "Business Value", "Acceptance Criteria"],
        "optional": ["Preconditions", "Not In Scope", *DEPRECATION_HEADINGS, NOTES_HEADING],
    },
    "FEAT": {
        "required": [
            "Description",
            "Surface Type",
            "Owners",
            "User Stories",
            "Functionalities",
        ],
        "optional": ["External Dependencies", FEATURE_DEPS_HEADING, *FEAT_DEPRECATION_HEADINGS,
                     NOTES_HEADING],
    },
    "FUNC": {
        "required": [
            "Description",
            "Status",
            "Parent Feature",
            "Func Type",
            "Acceptance Criteria",
        ],
        "optional": ["Rationale", "Preconditions", "Not In Scope", *DEPRECATION_HEADINGS,
                     NOTES_HEADING],
    },
}
# A heading a derived field would author gets its own message rather than the generic
# "unknown heading" one: heading -> the fix hint explaining why it has no home.
FORBIDDEN_ISSUE_HEADINGS = {
    "FEAT": {
        "Status": "a Feature has no authored status - its state is derived from its "
                  "Functionalities (living-doc-glossary.md#feature); remove the heading",
        "Deprecated At": "a Feature has no deprecation date "
                         "(living-doc-glossary.md#feature); keep '## Deprecation Reason' / "
                         "'## Superseded By' if the surface is being retired",
    },
    "FUNC": {
        FEATURE_DEPS_HEADING:
            "move it to the parent Feature's issue body - a dependency is declared by the Feature "
            "that makes the call (living-doc-glossary.md#feature)",
    },
    "US": {
        FEATURE_DEPS_HEADING:
            "a User Story has no dependencies - a dependency is declared by the Feature that "
            "makes the call (living-doc-glossary.md#feature)",
    },
}

# The two authored forms of one entity must agree on required content. Each row maps an
# issue-body heading to the key carrying the same fact in the source-code header form.
PAIR_FIELD_MAP = {
    "US": {"Description": "narrative", "Status": "status", "Business Value": "business_value"},
    "FUNC": {"Description": "narrative", "Status": "status",
             "Parent Feature": "parent", "Func Type": "func_type"},
    "FEAT": {"Description": "purpose", "Surface Type": "surface_type", "Owners": "owners",
             "User Stories": "user_stories", "Functionalities": "functionalities"},
}
# Optional extensions a `.feature` / PageObject header may carry, beyond the required keys.
# `notes:` is deliberately absent from both: it is available on every entity and counts as no
# file's one optional extension (see `NOTES_HEADING`).
OPTIONAL_FEATURE_KEYS = ["source", "rationale", "preconditions", "not_in_scope",
                         "deprecated_at", "deprecation_reason", "superseded_by"]
OPTIONAL_PO_KEYS = ["wizard-steps", "stub-reason", FEATURE_DEPS_KEY]
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
        self.declared_acs: dict[str, set[str]] = {}       # ac id -> declared variant values
        self.declared_variants: dict[str, str] = {}       # ac id -> 'aspect' or its keyword name
        self.feature_file_acs: set[str] = set()           # ACs declared in the two .feature headers
        self.feature_file_covered: set[str] = set()       # ACs carrying a scenario in a .feature file
        self.entity_refs: list[tuple[str, str, int]] = [] # (referenced id, file, line)
        self.pending_ac_tags: list[tuple[str, str | None, str | None, str, int]] = []
        # entity id -> form name -> {"file", "fields", "acs", "optional"} (PAIR_MISMATCH pass)
        self.forms: dict[str, dict[str, dict]] = {}
        self.surface_types: dict[str, str] = {}           # FEAT id -> declared surface type
        self.retiring_features: dict[str, str] = {}       # FEAT id -> the field that says so
        # (declaring FEAT id, target FEAT id, file, line)
        self.feature_deps: list[tuple[str, str, str, int]] = []

    def declare_form(self, entity_id: str, form: str, file: str, fields: dict[str, str],
                     acs: dict[str, str], optional: list[str]) -> None:
        self.forms.setdefault(entity_id, {})[form] = {
            "file": file, "fields": fields, "acs": acs, "optional": optional,
        }

    def fail(self, file: str, line: int | None, rule: str, hint: str) -> None:
        self.findings.append(Finding(file, line, rule, hint))

    def declare_ac(self, ac_id: str, values: set[str], variant: str | None = None) -> None:
        self.declared_acs.setdefault(ac_id, set()).update(values)
        if variant is not None:
            self.declared_variants[ac_id] = variant


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


def _declare_feature_deps(value: str, declaring: str, corpus: Corpus, rel: str,
                          lineno: int) -> None:
    """Parse a Feature's ``feature_dependencies`` value - ``FEAT-`` ids, comma-separated."""
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items or [i.lower() for i in items] == ["none"]:
        corpus.fail(rel, lineno, "feature_dependencies has no 'none' value",
                    "omit the field when the Feature calls nothing "
                    "(living-doc-glossary.md#feature)")
        return
    for item in items:
        if derive_entity_id(item)[0] != item or not item.startswith("FEAT-"):
            corpus.fail(rel, lineno, f"feature_dependencies entry '{item}' is not a Feature id",
                        "list 'FEAT-<nnn>' ids, comma-separated on one line "
                        "(living-doc-glossary.md#feature)")
            continue
        corpus.feature_deps.append((declaring, item, rel, lineno))


def _entity_ids(value: str) -> list[str]:
    """The entity ids a list value names, e.g. 'FUNC-001, FUNC-002'; 'none' names none."""
    return [eid for eid in (derive_entity_id(token)[0] for token in re.split(r"[,\s]+", value))
            if eid is not None]


# --- living-doc-utilities: canonical form and the criterion grammar ----------------------

def _report_rewrites(changes: list[normalize.Change], corpus: Corpus, rel: str) -> None:
    """NON_CANONICAL_FORM for every line ``normalize`` rewrites."""
    for change in changes:
        # A rule may record a line it leaves as written (an inline '# AC:' comment's description
        # does); only a line whose text changes is non-canonical.
        if change.before == change.after:
            continue
        corpus.fail(rel, change.line,
                    f"NON_CANONICAL_FORM: normalize rewrites this line ({change.rule})",
                    f"write it as {change.after.strip()!r} - '-' (hyphen-minus) in structural "
                    "positions, lowercase states, full versions "
                    "(living-doc-glossary.md#acceptance-criterion-ac)")


def _normalized(text: str, fmt: SourceFormat, kind: str, corpus: Corpus, rel: str
                ) -> "normalize.Frame":
    """``normalize``'s frame of ``text``, its rewrites reported as NON_CANONICAL_FORM."""
    source, frame = normalize.normalize_framed(text, fmt, ENTITY_TYPES[kind])
    _report_rewrites(source.changes, corpus, rel)
    return frame


def _criteria(frame: "normalize.Frame", entity_id: str, corpus: Corpus, rel: str
              ) -> list[AcceptanceCriterion]:
    """The criteria ``ac_grammar`` reads from ``frame``; each warning it raises is a finding."""
    acs, warnings = ac_grammar.parse_frame_criteria(frame, entity_id)
    for warning in warnings:
        subject = f"{warning.ac_id}: " if warning.ac_id else ""
        corpus.fail(rel, warning.line_no, f"{warning.code}: {subject}{warning.message}",
                    GRAMMAR_HINTS.get(warning.code, GRAMMAR_HINT))
    header_lines: dict[str, int] = {}
    for number, ac_id in sorted(ac_grammar.criterion_ids(frame).items()):
        header_lines.setdefault(ac_id, number)
    for ac in acs:
        # `ac_grammar` never checks ownership: that rule lives on the entity.
        if not ac.id.startswith(entity_id + "-"):
            corpus.fail(rel, header_lines.get(ac.id),
                        f"AC id '{ac.id}' does not belong to entity '{entity_id}'",
                        f"AC ids under {entity_id} must read '{entity_id}-<nn>'")
    return acs


# --- indentation levels -----------------------------------------------------------------
# docs/guides/living-doc-header-types.md#indentation. The corpus requires the canonical levels,
# not the relative rule the parsers in `living-doc-utilities` apply: the flat layout stays valid
# for authors, but, like a NON_CANONICAL_FORM variant, it is normalisation test data.

INDENT_REF = "living-doc-header-types.md#indentation"
_LEVEL_KEY_RE = re.compile(r"[a-z_][a-z0-9_-]*:(?:\s|$)")
_PO_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*:\s")
_FEATURE_INDENT_RE = re.compile(r"\s*#([ \t ]*)")
_PO_INDENT_RE = re.compile(r"\s*(?:/\*+|\*+)?([ \t ]*)")
_ISSUE_INDENT_RE = re.compile(r"([ \t ]*)")
_FEATURE_ITEM_KINDS = {0: "entity field item", 2: "criterion item", 4: "sub-key item"}


def _indent(text: str) -> int:
    return len(text) - len(text.lstrip(" "))


def _spaces_only(corpus: Corpus, rel: str, lineno: int, lead: str) -> bool:
    """Report a tab or no-break space in an indent; True when the indent is spaces only."""
    if "\t" in lead or " " in lead:
        corpus.fail(rel, lineno, "tab or no-break space in an indent",
                    f"indent with spaces only ({INDENT_REF})")
        return False
    return True


def _item_level(corpus: Corpus, rel: str, lineno: int, kind: str, n: int, first: int,
                prev_item: int | None) -> None:
    """An item sits at ``first``, or one step deeper than the item above it (a nested item)."""
    deepest = first if prev_item is None else max(first, prev_item + 2)
    if n < first or n > deepest or (n - first) % 2:
        nested = f", or {first + 2}..{deepest} for a nested item" if deepest > first else ""
        corpus.fail(rel, lineno, f"{kind} at indent {n}, expected {first}{nested}",
                    f"use the template levels ({INDENT_REF})")


def check_feature_levels(header: list[tuple[int, str]], raw: list[str], corpus: Corpus,
                         rel: str) -> None:
    """Template levels of a ``.feature`` header, counted after ``# ``.

    Entity keys and ``acceptance_criteria:`` at 0, their items at 2; ``AC:`` at 2, criterion
    items and sub-keys at 4; sub-key items at 6; wrapped text deeper than its ``- ``.
    """
    seen_ac = False
    marker = 0                  # template level of the key or ``AC:`` the next item sits under
    item: int | None = None     # indent of the last ``- `` under that marker
    for lineno, text in header:
        if _is_banner(text):
            continue
        lead = _FEATURE_INDENT_RE.match(raw[lineno - 1])
        if not _spaces_only(corpus, rel, lineno, lead.group(1) if lead else ""):
            continue
        n, body = _indent(text), text.strip()
        if body.startswith("- "):
            _item_level(corpus, rel, lineno, _FEATURE_ITEM_KINDS.get(marker, "item"), n,
                        marker + 2, item)
            item = n
        elif body.startswith("AC:"):
            seen_ac, marker, item = True, 2, None
            if n != 2:
                corpus.fail(rel, lineno, f"criterion header 'AC:' at indent {n}, expected 2",
                            f"use the template levels ({INDENT_REF})")
        elif item is not None and n > item:
            continue            # wrapped text of the item above
        elif _LEVEL_KEY_RE.match(body):
            marker, item = (4 if seen_ac else 0), None
            if n != marker:
                what = "criterion sub-key" if seen_ac else "entity key"
                corpus.fail(rel, lineno, f"{what} '{body.split(':')[0]}:' at indent {n}, "
                            f"expected {marker}", f"use the template levels ({INDENT_REF})")
        else:
            above = marker if item is None else item
            if n <= above:
                corpus.fail(rel, lineno, f"wrapped text at indent {n}, expected deeper than "
                            f"{above}", f"indent a wrapped line past its '- ' or key ({INDENT_REF})")


def check_pageobject_levels(header: list[tuple[int, str]], raw: list[str], corpus: Corpus,
                            rel: str) -> None:
    """Keys at the banner's base level; items and wrapped lines deeper than their key."""
    seen_key = False
    for lineno, text in header:
        if _is_banner(text):
            continue
        lead = _PO_INDENT_RE.match(raw[lineno - 1])
        if not _spaces_only(corpus, rel, lineno, lead.group(1) if lead else ""):
            continue
        n = _indent(text)
        if n == 0 and _PO_KEY_RE.match(text):
            seen_key = True
        elif seen_key and n == 0:
            what = "item" if text.startswith("- ") else "wrapped line"
            corpus.fail(rel, lineno, f"{what} at indent 0, expected deeper than its key at 0",
                        f"indent it under its key, e.g. to the value column ({INDENT_REF})")


def check_issue_body_levels(lines: list[str], corpus: Corpus, rel: str) -> None:
    """Top-level items at column 0; nested items only outside the id-list headings."""
    section: str | None = None
    item: int | None = None     # indent of the last ``- `` in the current list
    after_blank = False
    in_comment = False
    for i, line in enumerate(lines, 1):
        if in_comment or line.lstrip().startswith("<!--"):
            in_comment = "-->" not in line
            continue
        if not line.strip():
            after_blank = True
            continue
        if line.startswith("#"):
            h2 = re.match(r"##\s+(.+?)\s*$", line)
            if h2 and not line.startswith("###"):
                section = h2.group(1)
            item, after_blank = None, False
            continue
        if not _spaces_only(corpus, rel, i, _ISSUE_INDENT_RE.match(line).group(1)):
            continue
        n, body = _indent(line), line.strip()
        if body.startswith("- "):
            if n > 0 and item is not None and section in ID_LIST_HEADINGS:
                corpus.fail(rel, i, f"nested item under '## {section}', expected 0",
                            "an id-list section holds ids only; nest items under a bullet-list "
                            f"heading ({INDENT_REF})")
            else:
                _item_level(corpus, rel, i, "list item", n, 0, item)
            item = n
        elif item is not None and not after_blank and n <= item:
            corpus.fail(rel, i, f"wrapped text at indent {n}, expected deeper than {item}",
                        f"indent a wrapped line past its '- ' ({INDENT_REF})")
        elif n == 0:
            item = None         # a paragraph ends the list
        after_blank = False


def _variant_key(name: str) -> str:
    """A variant name as the canon compares it: case-insensitive, with `-`, `_` and space equal."""
    return re.sub(r"[-_ ]+", "-", name.strip().lower())


def _parse_ac_block(header: list[tuple[int, str]], corpus: Corpus, rel: str,
                    acs: list[AcceptanceCriterion], line_ids: dict[int, str]) -> dict[str, str]:
    """Each parsed AC's variant name: ``aspect``, or its keyword as written on its bullet.

    ``ac_grammar`` reads the header and every AC-level bullet, and reports two variant
    declarations, ``aspect`` as a keyword name and a bullet the AC text does not name. It folds a
    keyword's case, ``-``, ``_`` and space, so it takes ``- User_Role:`` under ``{User_Role}``
    without a warning: the canon's one spelling - lowercase kebab-case, the same in the AC text,
    the bullet and the tag - is checked here, on the bullet as written. Only a name spelled so is
    declared, for ``cross_reference`` to compare a tag's name with. ``line_ids`` maps each line of
    a criterion block to its AC (``ac_grammar.criterion_ids``).
    """
    by_id = {ac.id: ac for ac in acs}
    variants = {ac.id: "aspect" for ac in acs if ac.aspect and not ac.placeholder_values}
    bullet_indent: dict[str, int] = {}  # the description bullet's indent; AC-level bullets share it
    for lineno, text in header:
        ac = by_id.get(line_ids.get(lineno, ""))
        stripped = _strip_annotation(text.strip())
        if ac is None or not stripped.startswith("- "):
            continue
        indent = len(text) - len(text.lstrip())
        if bullet_indent.setdefault(ac.id, indent) != indent or not ac.placeholder_values:
            continue
        km = AC_KEYWORD_BULLET_RE.match(stripped)
        key = _variant_key(next(iter(ac.placeholder_values)))
        if km is None or _variant_key(km.group("name")) != key:
            continue
        name = km.group("name")
        placeholders = {_variant_key(p): p for p in AC_PLACEHOLDER_RE.findall(ac.description)}
        if not VARIANT_NAME_RE.fullmatch(name) or placeholders.get(key) != name:
            corpus.fail(rel, lineno,
                        f"keyword '{name}' of {ac.id} is not one lowercase kebab-case name",
                        f"write it the same in the AC text, the bullet and the tag: "
                        f"'{{{key}}}', '- {key}:', '@AC:{ac.id}/{key}:<value>'")
        else:
            variants[ac.id] = name
    return variants


def _ac_extensions(acs: list[AcceptanceCriterion]) -> set[str]:
    """The AC-level optional extensions the parsed criteria carry, named as the conventions do."""
    extensions: set[str] = set()
    for ac in acs:
        if ac.aspect:
            extensions.add("AC-level Aspect:")   # a named keyword is its second spelling
        for key in ("preconditions", "not_in_scope"):
            if getattr(ac, key):
                extensions.add(f"AC-level {key}:")
    return extensions


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
    text = path.read_text(encoding="utf-8")
    raw = text.splitlines()
    kind = "US" if "/liv_doc_us/" in rel or "us-" in path.name else "FUNC"

    # Both formats a `.feature` file holds: the header, and the `# AC:` comments over its scenarios.
    frame = _normalized(text, SourceFormat.FEATURE_HEADER, kind, corpus, rel)
    _report_rewrites(normalize.normalize(text, SourceFormat.SCENARIO_FILE, ENTITY_TYPES[kind]).changes,
                     corpus, rel)

    header = _decomment_block(raw, FEATURE_STRIP_RE, FEATURE_STOP_RE)
    if not header:
        corpus.fail(rel, 1, "no leading '# ' living-doc header block",
                    "add the '# LIVING DOC — ...' comment banner from living-doc-header-types.md")
        return
    check_feature_levels(header, raw, corpus, rel)

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
    for token in (token for line in raw for token in line.split()):
        value = token[len(id_tag) + 2:]
        if token.startswith(f"@{id_tag}:") and derive_entity_id(value)[0] == value:
            entity_id = value
            break
    if entity_id is None:
        corpus.fail(rel, 1, f"missing feature-level '@{id_tag}:<id>' tag",
                    f"add '@{id_tag}:{kind}-<nnn>' immediately above 'Feature:'")
        parent_for_ac = kind + "-000"
    else:
        corpus.declared_entities.add(entity_id)
        parent_for_ac = entity_id

    acs = _criteria(frame, parent_for_ac, corpus, rel)
    variants = _parse_ac_block(header, corpus, rel, acs, ac_grammar.criterion_ids(frame))
    if "acceptance_criteria" in top_keys and not acs:
        corpus.fail(rel, top_keys["acceptance_criteria"],
                    "acceptance_criteria block declares no AC lines",
                    "add at least one 'AC:<id> (v<version> - <state>)' line")
    for ac in acs:
        # A tag can name only a variant whose spelling passed: an unchecked name declares no values.
        corpus.declare_ac(ac.id, set(ac.aspect) if ac.id in variants else set(),
                          variants.get(ac.id))
        if ac.state != "planned":
            corpus.feature_file_acs.add(ac.id)

    if entity_id is not None:
        fields = _feature_pair_fields(header, top_keys, raw, kind)
        extensions = _ac_extensions(acs)
        extensions.update(f"{key}:" for key in OPTIONAL_FEATURE_KEYS if key in top_keys)
        corpus.declare_form(entity_id, "feature-file header", rel, fields,
                            {ac.id: ac.canonical_header() for ac in acs}, sorted(extensions))

    if FEATURE_DEPS_KEY in top_keys:
        entity = "User Story" if kind == "US" else "Functionality"
        corpus.fail(rel, top_keys[FEATURE_DEPS_KEY],
                    f"{entity} header carries a '{FEATURE_DEPS_KEY}:' field",
                    "move it to the parent Feature's PageObject full header as "
                    "'feature_dependencies:' - a dependency is declared by the Feature that makes "
                    "the call (living-doc-glossary.md#feature)" if kind == "FUNC" else
                    "remove it - a dependency is declared by the Feature that makes the call "
                    "(living-doc-glossary.md#feature)")

    # scenario tags
    for i, line in enumerate(raw, 1):
        s = line.strip()
        if not s.startswith("@"):
            continue
        for token in s.split():
            if not token.startswith("@AC:"):
                continue
            m = AC_TAG_RE.fullmatch(token)
            if m is None or not ac_grammar.is_valid_ac_id(m.group("id")):
                if token.count("/") > 1:
                    corpus.fail(rel, i, f"scenario tag '{token}' carries more than one variant parameter",
                                "keep one '/<param>:<value>' - a scenario covers one value; tag one "
                                "scenario per value (living-doc-glossary.md#acceptance-criterion-ac)")
                else:
                    corpus.fail(rel, i, f"scenario tag '{token}' does not match the glossary tag format",
                                "use '@AC:<parent-id>-<nn>[/<param>:<value>]' with a US- or FUNC- "
                                "parent id (living-doc-glossary.md#acceptance-criterion-ac)")
                continue
            corpus.feature_file_covered.add(m.group("id"))
            corpus.pending_ac_tags.append(
                (m.group("id"), m.group("param"), m.group("value"), rel, i))

    if entity_id == "FUNC-001" or kind == "FUNC":
        for i, line in enumerate(raw, 1):
            pm = re.match(r"#\s?parent:(.*)$", line.strip())
            if pm:
                corpus.entity_refs.extend((rid, rel, i) for rid in _entity_ids(pm.group(1))[:1])


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
    text = path.read_text(encoding="utf-8")
    raw = text.splitlines()
    _report_rewrites(normalize.normalize(text, SourceFormat.PAGE_OBJECT, ENTITY_TYPES["FEAT"]).changes,
                     corpus, rel)

    header: list[tuple[int, str]] = []
    for i, line in enumerate(raw, 1):
        header.append((i, re.sub(r"^\s*(?:/\*+|\*+/?)?\s?", "", line).rstrip()))
        if "*/" in line:
            break
    if not any("LIVING DOC" in t for _, t in header):
        corpus.fail(rel, 1, "no leading '/* ... */' living-doc header banner",
                    "open the file with the '/* LIVING DOC — FEAT-<nnn> ... */' block")
        return
    check_pageobject_levels(header, raw, corpus, rel)

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

    if "surface_type" in keys and keys["surface_type"][1] != "UI":
        corpus.fail(rel, keys["surface_type"][0],
                    f"surface_type '{keys['surface_type'][1]}' is not 'UI'",
                    "a PageObject is the test abstraction for a UI surface only; an API surface "
                    "has no PageObject and carries no header here "
                    "(see living-doc-header-types.md#required-fields)")

    if "status" in keys:
        corpus.fail(rel, keys["status"][0], "PageObject header carries a 'status:' field",
                    "remove it - a surface has no status and a Feature's state is derived from "
                    "its Functionalities; an uninstrumented surface says so with 'stub-reason:' "
                    "(see living-doc-header-types.md#2-feature-in-a-pageobject-file)")

    if is_xref and FEATURE_DEPS_KEY in keys:
        corpus.fail(rel, keys[FEATURE_DEPS_KEY][0],
                    f"cross-reference header carries a '{FEATURE_DEPS_KEY}:' field",
                    "move it to the primary Feature file's full header - the field belongs only "
                    "there (see living-doc-header-types.md#2-feature-in-a-pageobject-file)")

    if "deprecated_at" in keys:
        corpus.fail(rel, keys["deprecated_at"][0],
                    "PageObject header carries a 'deprecated_at:' field",
                    "remove it - a Feature has no deprecation date; "
                    "keep 'deprecation_reason:' / 'superseded_by:' if "
                    "the surface is being retired "
                    "(see living-doc-header-types.md#2-feature-in-a-pageobject-file)")

    # The banner's `LIVING DOC — FEAT-<nnn> · <name>` title, read as the PageObject parser reads it.
    entity_id = derive_entity_id(extract_living_doc_title([t for _, t in header]) or "")[0]
    if entity_id is not None and not entity_id.startswith("FEAT-"):
        entity_id = None
    if entity_id is not None:
        corpus.declared_entities.add(entity_id)
    if entity_id is not None and not is_xref:
        fields = {key: _collapse(keys[key][1]) for key in PAIR_FIELD_MAP["FEAT"].values()
                  if key in keys}
        corpus.declare_form(entity_id, "PageObject header", rel, fields, {},
                            [f"{key}:" for key in OPTIONAL_PO_KEYS if key in keys])
        if "surface_type" in keys:
            corpus.surface_types[entity_id] = keys["surface_type"][1]
        for key in ("deprecation_reason", "superseded_by"):
            if key in keys:
                corpus.retiring_features.setdefault(entity_id, f"{key}:")
        if FEATURE_DEPS_KEY in keys:
            lineno, value = keys[FEATURE_DEPS_KEY]
            _declare_feature_deps(value, entity_id, corpus, rel, lineno)

    for key in ("user_stories", "functionalities", "parent-feat"):
        if key in keys:
            lineno, value = keys[key]
            for rid in _entity_ids(value):
                corpus.entity_refs.append((rid, rel, lineno))


# --- issue bodies -------------------------------------------------------------------

def check_issue_body(path: Path, root: Path, corpus: Corpus) -> None:
    rel = _rel(path, root)
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    label_m = re.search(r"Label:\s*(\w+)", raw)
    title_m = re.search(r"Title:\s*(.+?)\s*$", raw, re.MULTILINE)
    if not label_m or label_m.group(1) not in LABEL_TO_TYPE:
        corpus.fail(rel, 1, "issue header comment has no recognised 'Label:' value",
                    "add 'Label: DocumentedUserStory|DocumentedFeature|DocumentedFunctionality'")
        return
    etype = LABEL_TO_TYPE[label_m.group(1)]
    title_id = derive_entity_id(title_m.group(1))[0] if title_m else None
    if title_id is None:
        corpus.fail(rel, 1, "issue header comment has no 'Title: <ID> ...' entity id",
                    "add 'Title: <US|FEAT|FUNC>-<nnn> · <name>'")
    else:
        corpus.declared_entities.add(title_id)
    if title_m:
        # The issue title sits outside the body: `normalize_title` is the rule set for it.
        canonical, changes = normalize.normalize_title(title_m.group(1))
        rules = sorted({c.rule for c in changes if c.before != c.after})
        if rules:
            corpus.fail(rel, raw.count("\n", 0, title_m.start()) + 1,
                        f"NON_CANONICAL_FORM: normalize rewrites the issue title ({', '.join(rules)})",
                        f"write it as {canonical!r} - ' · ' after the id, '-' (hyphen-minus) in "
                        "the name (living-doc-glossary.md#acceptance-criterion-ac)")
    frame = _normalized(raw, SourceFormat.ISSUE_BODY, etype, corpus, rel)
    check_issue_body_levels(lines, corpus, rel)

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
    forbidden = FORBIDDEN_ISSUE_HEADINGS.get(etype, {})
    present = {h for _, h in headings}
    for i, h in headings:
        if h in forbidden:
            corpus.fail(rel, i, f"'## {h}' has no place in the {etype} issue-body layout",
                        forbidden[h])
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
    if "Surface Type" in sections and sections["Surface Type"] not in SURFACE_TYPES:
        corpus.fail(rel, 1,
                    f"'## Surface Type' value '{sections['Surface Type']}' is not documented",
                    f"use one of {SURFACE_TYPES} (living-doc-glossary.md#feature)")

    if etype == "FEAT" and title_id:
        if "Surface Type" in sections:
            corpus.surface_types[title_id] = sections["Surface Type"]
        for heading in FEAT_DEPRECATION_HEADINGS:
            if heading in present:
                corpus.retiring_features.setdefault(title_id, f"## {heading}")
        if FEATURE_DEPS_HEADING in sections:
            line = next((i for i, h in headings if h == FEATURE_DEPS_HEADING), 1)
            _declare_feature_deps(sections[FEATURE_DEPS_HEADING], title_id, corpus, rel, line)

    # AC sub-headings share the glossary grammar, read by `ac_grammar`
    ac_headers: dict[str, str] = {}
    if "Acceptance Criteria" in present:
        for i, sub in sub_headings:
            if not sub.startswith("AC:"):
                corpus.fail(rel, i, f"sub-heading '### {sub}' is not an 'AC:' criterion header",
                            "use '### AC:<id> (v<version> - <state>)', or '### AC:<id> (planned)' "
                            "for a backlog AC")
        for ac in _criteria(frame, title_id or etype + "-000", corpus, rel):
            ac_headers[ac.id] = ac.canonical_header()
            corpus.declare_ac(ac.id, set())

    if title_id:
        fields = {key: sections[heading]
                  for heading, key in PAIR_FIELD_MAP[etype].items() if heading in sections}
        # `NOTES_HEADING` is excluded for the reason given at `OPTIONAL_FEATURE_KEYS`.
        corpus.declare_form(title_id, "issue body", rel, fields, ac_headers,
                            [f"## {h}" for h in spec["optional"]
                             if h in present and h != NOTES_HEADING])

    # parent references carried in issue-body sections
    section = None
    for i, line in enumerate(lines, 1):
        h2 = re.match(r"##\s+(.+?)\s*$", line)
        if h2:
            section = h2.group(1)
            continue
        if section in ("Parent Feature", "User Stories", "Functionalities"):
            for rid in _entity_ids(line):
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
        if param is None:
            continue    # a bare tag covers the whole AC - every value of one with variants
        variant = corpus.declared_variants.get(ac_id)
        tag = f"@AC:{ac_id}/{param}:{value}"
        if variant is None:
            corpus.fail(rel, line, f"{tag} — {ac_id} declares no variants",
                        f"tag it '@AC:{ac_id}', or declare the values on the AC "
                        "(living-doc-header-types.md#ac-variants)")
        elif param != variant:
            corpus.fail(rel, line, f"{tag} — {ac_id} declares its values as '{variant}', not '{param}'",
                        f"use '@AC:{ac_id}/{variant}:<value>' (living-doc-header-types.md#ac-variants)")
        elif value not in corpus.declared_acs[ac_id]:
            bullet = "Aspect" if variant == "aspect" else variant
            corpus.fail(rel, line,
                        f"{tag} — '{value}' is not a declared value of '{variant}' on {ac_id}",
                        f"declared values: {sorted(corpus.declared_acs[ac_id])} "
                        f"(add it to the AC's '- {bullet}:' line; STALE_AC_REF)")


def feature_dependency_rules(corpus: Corpus) -> None:
    """The four rules a declared ``feature_dependencies`` edge must satisfy.

    These are the checks typing the field buys: a free-form
    ``external_dependencies`` name can be validated against nothing, while a
    ``FEAT-`` id can be resolved, surface-typed and lifecycle-checked
    (docs/guides/living-doc-glossary.md#feature).
    """
    for declaring, target, rel, line in corpus.feature_deps:
        if target not in corpus.declared_entities:
            corpus.fail(rel, line,
                        f"feature_dependencies target '{target}' has no matching entity "
                        "in the corpus",
                        "point it at a declared API Feature, or add the Feature the "
                        "behaviour calls")
            continue
        if target == declaring:
            corpus.fail(rel, line,
                        f"feature_dependencies target '{target}' is the declaring Feature itself",
                        "a Feature cannot depend on itself - remove the entry, or point it at "
                        "the Feature actually being called")
            continue
        surface_type = corpus.surface_types.get(target)
        if surface_type != "API":
            corpus.fail(rel, line,
                        f"feature_dependencies target '{target}' is not an 'API' Feature "
                        f"(surface type: {surface_type or 'none declared'})",
                        "only a Feature with a contract anchor can be a dependency target "
                        "(living-doc-glossary.md#feature); a system with no anchor "
                        "belongs in the caller Feature's 'external_dependencies'")
        if target in corpus.retiring_features:
            corpus.fail(rel, line,
                        f"feature_dependencies target '{target}' is being retired "
                        f"({corpus.retiring_features[target]})",
                        "do not declare a dependency on a deprecated Feature - point it at "
                        "the replacement surface")


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
        # An `API` Feature is authored once: its contract anchor carries no living-doc header
        # yet, so there is no source-code form to write (living-doc-glossary.md#feature).
        expected = 1 if corpus.surface_types.get(entity_id) == "API" else 2
        if len(forms) != expected:
            form = next(iter(forms.values()))
            corpus.fail(
                form["file"], None,
                f"PAIR_MISMATCH: {entity_id} must have exactly {expected} authored form(s) "
                f"(found {len(forms)})",
                "an API Feature is authored as an issue body only - its contract anchor carries "
                "no living-doc header yet (living-doc-glossary.md#feature)" if expected == 1
                else "restore the missing form or remove the unexpected extra form",
            )
        if len(forms) != 2:
            continue  # nothing to compare: the pair passes below only when both forms exist
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

    cross_reference(corpus)
    feature_dependency_rules(corpus)
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
