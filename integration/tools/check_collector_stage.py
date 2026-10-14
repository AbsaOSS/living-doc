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
"""The collector stage's first-stage assertions over the ``docs/examples/`` corpus.

Re-reads each artifact ``living-doc-collector-gh`` wrote with ``read_artifact``, which validates
it against its contract, then asserts that what the corpus's source-code chain (``gherkin/`` +
``pageobject/``) authors comes through:

- every entity, with its authored state on a User Story and a Functionality and a derived
  state on a Feature;
- every acceptance criterion, the deprecated, target-version and backlog forms among them, and
  the extensions the chain authors (AC-level ``preconditions``, feature-level ``not_in_scope``,
  ``feature_dependencies``);
- the keyword AC ``AC:FUNC-001-03``: its three declared values as ``aspect``, and its one
  covering scenario linked as ``aspect: minimum-length``;
- none of the warnings a canonical corpus must never raise.

Runs in the ``collector-gh`` venv that ``integration/collector-gh.sh`` builds: it imports
nothing but ``living-doc-utilities``, which that venv holds through the collector's own
``requirements.txt``. The normalized snapshot cannot be re-read this way - its volatile values
are placeholders - so the artifact is validated before it is normalized, and the snapshot diff
ties the committed file to it.

Usage:
    python integration/tools/check_collector_stage.py <output-root>   # the collector's output-path
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from living_doc_utilities.contracts.codes import ContractError
from living_doc_utilities.contracts.io import read_artifact

# A canonical corpus raises none of these: each one means an authored line was dropped or misread.
FORBIDDEN_WARNINGS = ["MALFORMED_AC", "UNPARSED_AC_LINE", "UNKNOWN_SECTION", "MISSING_ENTITY_ID",
                      "MISSING_STATUS"]

# entity id -> (state, state_origin), as the source-code chain authors it or the pipeline derives it.
ENTITIES = {
    "US-001": ("active", "authored"),
    "FEAT-001": ("active", "derived"),     # from FUNC-001 (active) and FUNC-002 (planned)
    "FEAT-003": ("planned", "derived"),    # documented at surface level: no Functionality yet
    "FUNC-001": ("active", "authored"),
    "FUNC-002": ("planned", "authored"),
}
# AC id -> (state, version, removal_planned): every AC the chain declares, each AC state form once.
ACCEPTANCE_CRITERIA = {
    "US-001-01": ("active", "1.0.0", None),
    "US-001-02": ("active", "1.0.0", None),
    "US-001-03": ("planned", "1.1.0", None),           # planned, with a target version
    "US-001-04": ("deprecated", "1.0.0", "2.0.0"),     # deprecated, with its removal note
    "FUNC-001-01": ("active", "1.0.0", None),
    "FUNC-001-02": ("active", "1.0.0", None),
    "FUNC-001-03": ("active", "1.0.0", None),
    "FUNC-002-01": ("planned", None, None),            # the version-less backlog form
}
KEYWORD_AC = "FUNC-001-03"
KEYWORD = "rule"
KEYWORD_VALUES = ["minimum-length", "character-classes", "no-username"]
KEYWORD_COVERED_VALUE = "minimum-length"


def _warnings(name: str, result, failures: list[str]) -> None:
    for warning in result.warnings:
        if warning.code in FORBIDDEN_WARNINGS:
            where = warning.path or warning.context or "-"
            if warning.line_no is not None:
                where = f"{where}:{warning.line_no}"
            subject = "/".join(part for part in (warning.entity_id, warning.ac_id) if part)
            failures.append(f"{name}: {warning.code} at {where} {subject}: {warning.message}")


def check_doc_source(result, failures: list[str]) -> None:
    entities = {e.entity_id: e for e in [*result.user_stories, *result.features,
                                         *result.functionalities]}
    for entity_id, (state, origin) in ENTITIES.items():
        entity = entities.get(entity_id)
        if entity is None:
            failures.append(f"doc-source: {entity_id} is missing")
        elif (entity.state, entity.state_origin) != (state, origin):
            failures.append(f"doc-source: {entity_id} is {entity.state} ({entity.state_origin}), "
                            f"expected {state} ({origin})")

    acs = {ac.id: ac for entity in entities.values() for ac in entity.acceptance_criteria}
    for ac_id, expected in ACCEPTANCE_CRITERIA.items():
        ac = acs.get(ac_id)
        if ac is None:
            failures.append(f"doc-source: AC:{ac_id} is missing")
        elif (ac.state, ac.version, ac.removal_planned) != expected:
            failures.append(f"doc-source: AC:{ac_id} reads {ac.canonical_header()!r}, expected "
                            f"state/version/removal {expected}")

    if "US-001-01" in acs and not acs["US-001-01"].preconditions:
        failures.append("doc-source: AC:US-001-01 lost its AC-level preconditions")
    if "FUNC-002" in entities and not entities["FUNC-002"].not_in_scope:
        failures.append("doc-source: FUNC-002 lost its not_in_scope")
    if "FEAT-003" in entities and entities["FEAT-003"].feature_dependencies != ["FEAT-002"]:
        failures.append(f"doc-source: FEAT-003 feature_dependencies is "
                        f"{entities['FEAT-003'].feature_dependencies}, expected ['FEAT-002']")

    keyword_ac = acs.get(KEYWORD_AC)
    if keyword_ac is not None:
        if keyword_ac.aspect != KEYWORD_VALUES:
            failures.append(f"doc-source: AC:{KEYWORD_AC} aspect is {keyword_ac.aspect}, "
                            f"expected its '{KEYWORD}' values {KEYWORD_VALUES}")
        if keyword_ac.placeholder_values != {KEYWORD: KEYWORD_VALUES}:
            failures.append(f"doc-source: AC:{KEYWORD_AC} placeholder_values is "
                            f"{keyword_ac.placeholder_values}, expected {{{KEYWORD!r}: {KEYWORD_VALUES}}}")
    _warnings("doc-source", result, failures)


def check_ui_tests(result, failures: list[str]) -> None:
    links = [link for scenario in result.scenarios for link in scenario.acceptance_criteria
             if link.id == KEYWORD_AC]
    if [link.aspect for link in links] != [KEYWORD_COVERED_VALUE]:
        failures.append(f"ui-tests: AC:{KEYWORD_AC} is linked as "
                        f"{[f'aspect: {link.aspect}' for link in links]}, expected exactly one "
                        f"scenario as 'aspect: {KEYWORD_COVERED_VALUE}'")
    _warnings("ui-tests", result, failures)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: check_collector_stage.py <output-root>", file=sys.stderr)
        return 2
    root = Path(argv[0])
    failures: list[str] = []
    for mode, check in (("doc-source", check_doc_source), ("ui-tests", check_ui_tests)):
        path = root / mode / f"{mode}.json"
        try:
            result = read_artifact(path, mode)
        except (ContractError, OSError, ValueError) as exc:
            failures.append(f"{mode}: {path} does not validate against its contract: {exc}")
            continue
        codes = Counter(warning.code for warning in result.warnings)
        print(f"  {mode}: valid ({result.schema_version}); warnings: "
              f"{', '.join(f'{code}={n}' for code, n in sorted(codes.items())) or 'none'}")
        check(result, failures)

    if failures:
        print(f"collector stage: {len(failures)} assertion(s) failed")
        for failure in failures:
            print(f"  FAIL {failure}")
        return 1
    print(f"  OK: {len(ENTITIES)} entities, {len(ACCEPTANCE_CRITERIA)} acceptance criteria, the keyword "
          f"AC and no {'/'.join(FORBIDDEN_WARNINGS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
