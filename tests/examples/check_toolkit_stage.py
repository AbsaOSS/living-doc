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
"""The toolkit stage's assertions over what it writes from the ``docs/examples/`` corpus.

Re-reads each artifact ``living-doc-toolkit`` wrote with ``read_artifact``, which validates it
against its contract, then asserts:

- ``generator-ready``, inner: every entity with its state, every acceptance criterion with its
  state and version, ``not_in_scope`` on ``FUNC-002``, the document's title and version, and the
  selection counts;
- ``generator-ready``, release: only the entities and criteria that view keeps, none of them
  ``planned`` or ``in_review``, and its selection counts. The total of criteria is by contract
  that of the kept entities (``SelectionSummary``), so it is smaller than the inner view's;
- ``coverage-matrix``: every counted criterion's verdict per aspect, ``AC:FUNC-001-03`` at 1 of its
  3 ``rule`` values among them, the summaries and the planned totals;
- ``ui-test-catalog``: its feature files, their grouping and the number of scenarios;
- the two warnings this corpus expects on ``FEAT-003``, in both ``generator-ready`` views and the
  matrix, and none in the catalog;
- two documentation files in one run fail with ``MULTIPLE_DOCUMENTATION_SOURCES``, a non-zero exit
  and no output file. This runs the CLI, not the action's ``main.py``: ``main.py`` takes one
  ``input``, and only ``coverage-matrix --doc-input`` may be repeated.

Runs in the ``toolkit`` venv that ``tests/collector/toolkit.sh`` builds: it imports nothing but
``living-doc-utilities``, the standard library and the corpus's values in
``check_collector_stage.py``. The normalized snapshot cannot be re-read this way - its volatile
values are placeholders - so the artifact is validated before it is normalized, and the snapshot
diff ties the committed file to it.

Usage:
    python tests/examples/check_toolkit_stage.py <toolkit-output-root> <doc-source.json> <ui-tests.json>
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from check_collector_stage import (ACCEPTANCE_CRITERIA, ENTITIES, KEYWORD, KEYWORD_AC, KEYWORD_COVERED_VALUE,
                                   KEYWORD_VALUES)
from living_doc_utilities.contracts.codes import ContractError
from living_doc_utilities.contracts.io import read_artifact

DOCUMENT_TITLE = "living-doc-examples"
DOCUMENT_VERSION = "1.0.0"

# (total, included, excluded), of entities and of acceptance criteria.
INNER_SELECTION = ((5, 5, 0), (8, 8, 0))
RELEASE_SELECTION = ((5, 3, 2), (7, 6, 1))
RELEASE_ENTITIES = ["US-001", "FEAT-001", "FUNC-001"]
RELEASE_ACS = ["US-001-01", "US-001-02", "US-001-04", "FUNC-001-01", "FUNC-001-02", "FUNC-001-03"]

# (counted, covered, partially covered, not covered, coverage %).
MATRIX_SUMMARY = (6, 3, 1, 2, 55.6)
# entity id -> coverage %; None when the entity has no counted criterion.
ENTITY_COVERAGE = {"US-001": 66.7, "FUNC-001": 44.4, "FUNC-002": None}
# AC id -> (state, status, keyword, {aspect: status}): every counted criterion.
COVERAGE = {
    "US-001-01": ("active", "covered", None, {}),
    "US-001-02": ("active", "not_covered", None, {}),
    "US-001-04": ("deprecated", "covered", None, {}),
    "FUNC-001-01": ("active", "covered", None, dict.fromkeys(KEYWORD_VALUES, "covered")),
    "FUNC-001-02": ("active", "not_covered", None, {}),
    KEYWORD_AC: ("active", "partially_covered", KEYWORD,
                 {value: "covered" if value == KEYWORD_COVERED_VALUE else "not_covered" for value in KEYWORD_VALUES}),
}
# (total, backlog, by target version).
PLANNED_SUMMARY = (2, 1, {"1.1.0": 1})

CATALOG_SCENARIOS = 6
# The entities the scenarios link to: one feature file under a User Story, one under a Functionality.
CATALOG_USER_STORIES = ["US-001"]
CATALOG_FUNCTIONALITIES = ["FUNC-001"]

# code -> what its `context` must start with: both name the documentation input they come from.
EXPECTED_WARNINGS = {
    "FEATURE_WITHOUT_FUNCTIONALITY": "source_input='doc-source-v1.0.0' entity_id='FEAT-003'",
    "UNRESOLVED_RELATION": "source_input='doc-source-v1.0.0' entity_id='FEAT-003' target='FEAT-002'",
}
EXPECTED_WARNING_ENTITY = "FEAT-003"

NEGATIVE_CODE = "MULTIPLE_DOCUMENTATION_SOURCES"


def _check_warnings(name: str, result, failures: list[str]) -> None:
    """Exactly the two warnings this corpus expects, each on its entity and naming its documentation input."""
    got = sorted(warning.code for warning in result.warnings)
    if got != sorted(EXPECTED_WARNINGS):
        failures.append(f"{name}: warnings are {got}, expected {sorted(EXPECTED_WARNINGS)}")
    for warning in result.warnings:
        context = EXPECTED_WARNINGS.get(warning.code)
        if context is None:
            continue
        if warning.entity_id != EXPECTED_WARNING_ENTITY:
            failures.append(f"{name}: {warning.code} is on {warning.entity_id}, expected {EXPECTED_WARNING_ENTITY}")
        if not (warning.context or "").startswith(context):
            failures.append(f"{name}: {warning.code} context is {warning.context!r}, expected it to start with "
                            f"{context!r}")


def _check_document(name: str, result, view: str, selection: tuple, failures: list[str]) -> None:
    document = result.document
    if (document.view, document.title, document.version) != (view, DOCUMENT_TITLE, DOCUMENT_VERSION):
        failures.append(f"{name}: document is {document.view}/{document.title}/{document.version}, expected "
                        f"{view}/{DOCUMENT_TITLE}/{DOCUMENT_VERSION}")
    summary = document.selection_summary
    got = ((summary.total_entities, summary.included_entities, summary.excluded_entities),
           (summary.total_acceptance_criteria, summary.included_acceptance_criteria,
            summary.excluded_acceptance_criteria))
    if got != selection:
        failures.append(f"{name}: selection (total, included, excluded) of entities and criteria is {got}, "
                        f"expected {selection}")


def check_inner(result, failures: list[str]) -> None:
    name = "generator-ready.inner"
    _check_document(name, result, "inner", INNER_SELECTION, failures)
    entities = {entity.entity_id: entity for entity in result.content.entities}
    if sorted(entities) != sorted(ENTITIES):
        failures.append(f"{name}: entities are {sorted(entities)}, expected {sorted(ENTITIES)}")
    for entity_id, (state, origin) in ENTITIES.items():
        entity = entities.get(entity_id)
        if entity is not None and (entity.state, entity.state_origin) != (state, origin):
            failures.append(f"{name}: {entity_id} is {entity.state} ({entity.state_origin}), "
                            f"expected {state} ({origin})")
    acs = {ac.id: ac for entity in entities.values() for ac in entity.acceptance_criteria}
    if sorted(acs) != sorted(ACCEPTANCE_CRITERIA):
        failures.append(f"{name}: criteria are {sorted(acs)}, expected {sorted(ACCEPTANCE_CRITERIA)}")
    for ac_id, expected in ACCEPTANCE_CRITERIA.items():
        ac = acs.get(ac_id)
        if ac is not None and (ac.state, ac.version, ac.removal_planned) != expected:
            got = (ac.state, ac.version, ac.removal_planned)
            failures.append(f"{name}: AC:{ac_id} state/version/removal is {got}, expected {expected}")
    if "FUNC-002" in entities and not entities["FUNC-002"].not_in_scope:
        failures.append(f"{name}: FUNC-002 lost its not_in_scope")
    _check_warnings(name, result, failures)


def check_release(result, failures: list[str]) -> None:
    name = "generator-ready.release"
    _check_document(name, result, "release", RELEASE_SELECTION, failures)
    entities = result.content.entities
    if sorted(entity.entity_id for entity in entities) != sorted(RELEASE_ENTITIES):
        failures.append(f"{name}: entities are {[entity.entity_id for entity in entities]}, "
                        f"expected {RELEASE_ENTITIES}")
    acs = [ac for entity in entities for ac in entity.acceptance_criteria]
    if sorted(ac.id for ac in acs) != sorted(RELEASE_ACS):
        failures.append(f"{name}: criteria are {[ac.id for ac in acs]}, expected {RELEASE_ACS}")
    for record, kind in [*((entity, "entity") for entity in entities), *((ac, "criterion") for ac in acs)]:
        if record.state in ("planned", "in_review"):
            failures.append(f"{name}: {kind} {getattr(record, 'entity_id', None) or record.id} is {record.state}")
    _check_warnings(name, result, failures)


def _summary(summary) -> tuple:
    return (summary.counted_acs, summary.covered_acs, summary.partially_covered_acs, summary.not_covered_acs,
            summary.coverage_pct)


def check_matrix(result, failures: list[str]) -> None:
    name = "coverage-matrix"
    if result.document.view != "inner":
        failures.append(f"{name}: document.view is {result.document.view}, expected inner")
    if _summary(result.summary) != MATRIX_SUMMARY:
        failures.append(f"{name}: summary is {_summary(result.summary)}, expected {MATRIX_SUMMARY}")
    coverage = {entity.entity_id: entity.summary.coverage_pct for entity in result.entities}
    if coverage != ENTITY_COVERAGE:
        failures.append(f"{name}: coverage per entity is {coverage}, expected {ENTITY_COVERAGE}")

    rows = {row.ac_id: row for entity in result.entities for row in entity.acceptance_criteria}
    if sorted(rows) != sorted(COVERAGE):
        failures.append(f"{name}: counted criteria are {sorted(rows)}, expected {sorted(COVERAGE)}")
    for ac_id, expected in COVERAGE.items():
        row = rows.get(ac_id)
        if row is None:
            continue
        got = (row.state, row.status, row.keyword, {aspect.aspect: aspect.status for aspect in row.aspects})
        if got != expected:
            failures.append(f"{name}: AC:{ac_id} state/status/keyword/aspects is {got}, expected {expected}")

    planned = result.planned_summary
    got_planned = (planned.total, planned.backlog, planned.by_target_version)
    if got_planned != PLANNED_SUMMARY:
        failures.append(f"{name}: planned (total, backlog, by version) is {got_planned}, expected {PLANNED_SUMMARY}")
    _check_warnings(name, result, failures)


def check_catalog(result, failures: list[str]) -> None:
    name = "ui-test-catalog"
    user_stories = [group.entity_id for file in result.feature_files for group in file.linked_to_user_story]
    functionalities = [group.entity_id for file in result.feature_files for group in file.linked_to_functionality]
    if (user_stories, functionalities) != (CATALOG_USER_STORIES, CATALOG_FUNCTIONALITIES):
        failures.append(f"{name}: groups are User Stories {user_stories} and Functionalities {functionalities}, "
                        f"expected {CATALOG_USER_STORIES} and {CATALOG_FUNCTIONALITIES}")
    if len(result.feature_files) != len(CATALOG_USER_STORIES) + len(CATALOG_FUNCTIONALITIES):
        failures.append(f"{name}: {len(result.feature_files)} feature files, expected one per group")
    scenarios = {scenario.scenario_id for file in result.feature_files
                 for group in [*file.linked_to_user_story, *file.linked_to_functionality]
                 for scenario in group.scenarios}
    scenarios |= {scenario.scenario_id for file in result.feature_files for scenario in file.unlinked}
    if len(scenarios) != CATALOG_SCENARIOS:
        failures.append(f"{name}: {len(scenarios)} scenarios, expected {CATALOG_SCENARIOS}")
    if result.warnings:
        failures.append(f"{name}: warnings {[warning.code for warning in result.warnings]}, expected none")


def check_negative_run(doc_source: Path, ui_tests: Path, failures: list[str]) -> None:
    """Two documentation files in one run: `MULTIPLE_DOCUMENTATION_SOURCES`, a non-zero exit, no output file."""
    name = "two documentation files"
    with tempfile.TemporaryDirectory() as work:
        first, second = Path(work) / "a.json", Path(work) / "b.json"
        shutil.copyfile(doc_source, first)
        shutil.copyfile(doc_source, second)
        output = Path(work) / "output.json"
        run = subprocess.run([sys.executable, "-I", "-m", "living_doc_cli.main", "coverage-matrix",
                              f"--doc-input={first}", f"--doc-input={second}", f"--tests-input={ui_tests}",
                              f"--output={output}"],
                             capture_output=True, text=True, encoding="utf-8", check=False)
        lines = [line for line in run.stderr.splitlines() if f"[{NEGATIVE_CODE}]" in line]
        if run.returncode == 0:
            failures.append(f"{name}: the run exited 0, expected a non-zero exit")
        for path in (first, second):
            if not any(f"'{path}'" in line for line in lines):
                failures.append(f"{name}: no {NEGATIVE_CODE} line names {path}; stderr: {run.stderr!r}")
        if output.exists():
            failures.append(f"{name}: the run wrote {output}, expected no output file")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: check_toolkit_stage.py <toolkit-output-root> <doc-source.json> <ui-tests.json>", file=sys.stderr)
        return 2
    root, doc_source, ui_tests = Path(argv[0]), Path(argv[1]), Path(argv[2])
    failures: list[str] = []
    for relative, contract, check in (
        ("gh-headers/generator-ready.inner.json", "generator-ready", check_inner),
        ("gh-headers/generator-ready.release.json", "generator-ready", check_release),
        ("gh-headers/coverage-matrix.json", "coverage-matrix", check_matrix),
        ("tests/ui-test-catalog.json", "ui-test-catalog", check_catalog),
    ):
        path = root / relative
        try:
            result = read_artifact(path, contract)
        except (ContractError, OSError, ValueError) as exc:
            failures.append(f"{relative}: {path} does not validate against its contract: {exc}")
            continue
        codes = Counter(warning.code for warning in result.warnings)
        print(f"  {relative}: valid ({result.schema_version}); warnings: "
              f"{', '.join(f'{code}={n}' for code, n in sorted(codes.items())) or 'none'}")
        check(result, failures)
    check_negative_run(doc_source, ui_tests, failures)

    if failures:
        print(f"toolkit stage: {len(failures)} assertion(s) failed")
        for failure in failures:
            print(f"  FAIL {failure}")
        return 1
    print(f"  OK: both views, {len(COVERAGE)} counted criteria per aspect, the catalog, the expected warnings and "
          f"{NEGATIVE_CODE} on two documentation files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
