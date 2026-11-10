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
"""The toolkit stage's invariants over the testbed's ``core``, read at its ``master``.

``core`` follows the canon 100 %, so any warning over it is a defect, and it is read at ``master``,
so its content is never written down here: every value this checker compares comes from the
artifacts at run time. It re-reads each artifact the toolkit wrote, and the two the collector wrote,
with ``read_artifact``, which validates it against its contract, and asserts:

- no toolkit artifact carries a warning;
- the inner ``generator-ready`` view holds every entity and criterion of ``doc-source``, each with
  its state;
- the release view holds exactly the records of ``doc-source`` that are not ``planned`` or
  ``in_review``, each with its state;
- the matrix has one row per ``active`` or ``deprecated`` criterion, and each row's verdict equals
  the one ``doc-source``'s declared values and ``ui-tests``' links give: with no declared value, a
  link covers the criterion; with declared values, a linked value is covered, a bare link covers
  every value;
- ``core`` holds at least one ``partially_covered`` criterion in each matrix and one record the
  release view drops, so neither comparison passes on nothing.

``FIELD_LOSS`` needs no assertion: a transform exits non-zero on it, and the script that ran the
toolkit reads that.

Two layouts. ``tests/testbed/run-testbed-stage.sh`` writes one tree, ``gh-headers/`` and ``tests/``,
with one matrix and one catalog. ``tests/integration/local-integration.sh`` (``--runner``) writes
each view's three outputs under ``<view>/toolkit/<command>/`` of its output root; each view's matrix
gets the matrix assertions, and each view's catalog is checked as an artifact.

Runs in a venv that holds the toolkit's own ``requirements.txt``: the one ``tests/collector/toolkit.sh``
builds for the testbed stage, or the one the toolkit's ``local-integration.sh`` builds in the local
integration runner's clone. It imports nothing but the standard library and ``living-doc-utilities``.

Usage:
    python tests/testbed/check_testbed_toolkit_stage.py <toolkit-output-root> <doc-source.json> <ui-tests.json>
    python tests/testbed/check_testbed_toolkit_stage.py --runner <runner-output-root> <doc-source.json> <ui-tests.json>
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from living_doc_utilities.contracts.codes import ContractError
from living_doc_utilities.contracts.io import read_artifact

COUNTED_STATES = ("active", "deprecated")
RELEASE_DROPS = ("planned", "in_review")
VIEWS = ("inner", "release")
# A toolkit command, the artifact it writes, and that artifact's contract.
COMMANDS = (("normalize-docs", "generator-ready"), ("coverage-matrix", "coverage-matrix"),
            ("normalize-tests", "ui-test-catalog"))


def layout(root: Path, runner: bool) -> dict[str, tuple[Path, str]]:
    """Each toolkit artifact under an output root, by the name the checks report it under: its path and contract."""
    if not runner:
        headers = root / "gh-headers"
        return {
            "generator-ready.inner": (headers / "generator-ready.inner.json", "generator-ready"),
            "generator-ready.release": (headers / "generator-ready.release.json", "generator-ready"),
            "coverage-matrix": (headers / "coverage-matrix.json", "coverage-matrix"),
            "ui-test-catalog": (root / "tests" / "ui-test-catalog.json", "ui-test-catalog"),
        }
    return {f"{artifact}.{view}": (root / view / "toolkit" / command / f"{artifact}.json", artifact)
            for command, artifact in COMMANDS for view in VIEWS}


def _read(name: str, path: Path, contract: str, failures: list[str]):
    try:
        return read_artifact(path, contract)
    except (ContractError, OSError, ValueError) as exc:
        failures.append(f"{name}: does not validate against {contract}: {exc}")
        return None


def _entities(doc_source) -> list:
    return [*doc_source.user_stories, *doc_source.features, *doc_source.functionalities]


def _records(entities: list) -> tuple[list[tuple], list[tuple]]:
    """Each entity's and each criterion's id and state, each list sorted."""
    return (sorted((entity.entity_id, entity.state) for entity in entities),
            sorted((ac.id, ac.state) for entity in entities for ac in entity.acceptance_criteria))


def check_views(inner, release, doc_source, failures: list[str]) -> int:
    """Asserts both views against `doc-source`; returns how many records the release view drops."""
    entities = _entities(doc_source)
    if _records(inner.content.entities) != _records(entities):
        failures.append(f"generator-ready.inner: holds {_records(inner.content.entities)}, "
                        f"doc-source holds {_records(entities)}")

    kept_entities, kept_acs = _records([entity for entity in entities if entity.state not in RELEASE_DROPS])
    expected = (kept_entities, [(ac_id, state) for ac_id, state in kept_acs if state not in RELEASE_DROPS])
    got = _records(release.content.entities)
    if got != expected:
        failures.append(f"generator-ready.release: holds {got}, expected the records not in {RELEASE_DROPS}: "
                        f"{expected}")
    selection = release.document.selection_summary
    return selection.excluded_entities + selection.excluded_acceptance_criteria


def _verdict(declared: list[str], linked: set) -> tuple[str, dict[str, str]]:
    """A criterion's status and per-aspect statuses from its declared values and its links' values."""
    if not declared:
        return ("covered" if linked else "not_covered"), {}
    aspects = {value: "covered" if value in linked or None in linked else "not_covered" for value in declared}
    covered = sum(1 for status in aspects.values() if status == "covered")
    if covered == len(declared):
        return "covered", aspects
    return ("partially_covered" if covered else "not_covered"), aspects


def check_matrix(name: str, matrix, doc_source, ui_tests, failures: list[str]) -> Counter:
    """Asserts every counted criterion's verdict in the matrix `name` against the two inputs; returns the statuses."""
    links: dict[str, set] = {}
    for scenario in ui_tests.scenarios:
        for link in scenario.acceptance_criteria:
            links.setdefault(link.id, set()).add(link.aspect)
    counted = {ac.id: ac for entity in _entities(doc_source) for ac in entity.acceptance_criteria
               if ac.state in COUNTED_STATES}
    rows = {row.ac_id: row for entity in matrix.entities for row in entity.acceptance_criteria}
    if sorted(rows) != sorted(counted):
        failures.append(f"{name}: rows are {sorted(rows)}, the counted criteria are {sorted(counted)}")
    statuses: Counter = Counter()
    for ac_id in sorted(set(rows) & set(counted)):
        row = rows[ac_id]
        statuses[row.status] += 1
        expected = _verdict(counted[ac_id].aspect, links.get(ac_id, set()))
        got = (row.status, {aspect.aspect: aspect.status for aspect in row.aspects})
        if got != expected:
            failures.append(f"{name}: AC:{ac_id} is {got}, doc-source and ui-tests give {expected}")
    return statuses


USAGE = "usage: check_testbed_toolkit_stage.py [--runner] <output-root> <doc-source.json> <ui-tests.json>"


def main(argv: list[str]) -> int:
    runner = argv[:1] == ["--runner"]
    if runner:
        argv = argv[1:]
    if len(argv) != 3:
        print(USAGE, file=sys.stderr)
        return 2
    failures: list[str] = []
    doc_source = _read("doc-source", Path(argv[1]), "doc-source", failures)
    ui_tests = _read("ui-tests", Path(argv[2]), "ui-tests", failures)
    results = {name: _read(name, path, contract, failures)
               for name, (path, contract) in layout(Path(argv[0]), runner).items()}

    for name, result in results.items():
        if result is not None:
            print(f"  {name}: valid ({result.schema_version}); warnings: {len(result.warnings) or 'none'}")
            failures.extend(f"{name}: warning {warning.code} entity={warning.entity_id or '-'}: {warning.message}"
                            for warning in result.warnings)

    dropped = 0
    inner, release = results["generator-ready.inner"], results["generator-ready.release"]
    if inner is not None and release is not None and doc_source is not None:
        dropped = check_views(inner, release, doc_source, failures)
    statuses: dict[str, Counter] = {}
    for name, matrix in results.items():
        if name.startswith("coverage-matrix"):
            statuses[name] = Counter()
            if matrix is not None and doc_source is not None and ui_tests is not None:
                statuses[name] = check_matrix(name, matrix, doc_source, ui_tests, failures)

    # A floor, not core's counts, which are read at run time: both sides empty would pass every comparison above.
    floors = [(f"partially_covered criterion in {name}", counter["partially_covered"])
              for name, counter in statuses.items()]
    for construct, count in (*floors, ("record the release view drops", dropped)):
        if count == 0:
            failures.append(f"nothing to assert: the artifacts have no {construct}")

    if failures:
        print(f"testbed core, toolkit: {len(failures)} invariant(s) failed")
        for failure in failures:
            print(f"  FAIL {failure}")
        return 1

    for name, counter in statuses.items():
        print(f"  OK: {name}: {sum(counter.values())} counted criteria, each verdict equal to what doc-source and "
              f"ui-tests give: {counter['covered']} covered, {counter['partially_covered']} partially covered, "
              f"{counter['not_covered']} not covered")
    print(f"      the inner view holds every record of doc-source; the release view drops {dropped}, "
          f"none left in {RELEASE_DROPS}")
    print("      warnings: none")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
