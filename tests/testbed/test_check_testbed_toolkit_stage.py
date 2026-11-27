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
"""Tests for tests/testbed/check_testbed_toolkit_stage.py: the warnings a link to a ``planned`` or ``in_review``
criterion, or a skipped scenario's link, must raise in each coverage matrix, and nothing else.

Run: ``python -m pytest tests/testbed -q`` (needs pytest and ``living-doc-utilities``, which
``tests/examples/requirements-examples-check.txt`` installs). Each case copies a real testbed run's committed
outputs (``tests/testbed/fixtures/testbed-core-run/``, the runner's layout, warning-free), skips one scenario as today's
``core`` does (``skip_scenario``), adds links to ``ui-tests.json`` and warnings to the views' ``coverage-matrix.json``,
and runs the check with ``--runner``. A warning carries the code,
criterion and context the pinned toolkit writes, and is counted in the matrix's stats, so no case needs the toolkit.
The stage's layout differs only in where the one matrix lies; the stage run over a testbed branch checks it. Nothing
goes online.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from living_doc_utilities.contracts.coverage_matrix import AcCoverage, CoverageSummary

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHECK = REPO_ROOT / "tests" / "testbed" / "check_testbed_toolkit_stage.py"
RUN_OUTPUT = REPO_ROOT / "tests" / "testbed" / "fixtures" / "testbed-core-run"
MATRICES = ("inner", "release")
# The fixture's `core` has no skipped scenario, and today's `core` does: the check needs a counted criterion whose only
# scenarios are skipped. The fixture skips a criterion's only scenario, one with no declared values that links nothing
# else, as tests/integration/test_local_integration.py's does.
SKIPPED_AC = "FUNC-009-02"
SKIPPED_SCENARIO_ID = ("AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv_doc_func/"
                       "func-009-loan-list-states.feature/member-without-loans-sees-the-empty-state")


@pytest.fixture
def root(tmp_path: Path) -> Path:
    copy = tmp_path / "testbed-core"
    shutil.copytree(RUN_OUTPUT, copy, ignore=shutil.ignore_patterns("*.log", "*.md", "generator-markdown"))
    skip_scenario(copy)
    return copy


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _ui_tests(root: Path) -> Path:
    return root / "collector-gh" / "ui-tests" / "ui-tests.json"


def _matrix(root: Path, view: str) -> Path:
    return root / view / "toolkit" / "coverage-matrix" / "coverage-matrix.json"


def criterion(root: Path, state: str) -> str:
    """The first criterion of ``doc-source`` in ``state``."""
    doc_source = _json(root / "collector-gh" / "doc-source" / "doc-source.json")
    return next(ac["id"] for kind in ("user_stories", "functionalities") for entity in doc_source[kind]
                for ac in entity["acceptance_criteria"] if ac["state"] == state)


def link(root: Path, scenario: int, ac_id: str, aspect: str | None = None) -> str:
    """Adds a link to ``ac_id`` to the ``scenario``-th scenario of ``ui-tests``; returns the scenario's id."""
    data = _json(_ui_tests(root))
    data["scenarios"][scenario]["acceptance_criteria"].append({"id": ac_id, "aspect": aspect})
    _write(_ui_tests(root), data)
    return data["scenarios"][scenario]["scenario_id"]


def warn(root: Path, code: str, ac_id: str, scenario_id: str, views: tuple[str, ...] = MATRICES) -> None:
    """Adds the warning the toolkit writes for a link from ``scenario_id`` to ``ac_id`` to the views' matrices."""
    for view in views:
        data = _json(_matrix(root, view))
        data["warnings"].append({"code": code, "message": f"Scenario {scenario_id!r} links {ac_id!r}.",
                                 "context": f"scenario_id={scenario_id!r}", "entity_id": ac_id.rsplit("-", 1)[0],
                                 "ac_id": ac_id})
        by_code = data["metadata"]["stats"]["cardinality"]["warnings_by_code"]
        by_code[code] = by_code.get(code, 0) + 1
        _write(_matrix(root, view), data)


def _summary(rows: list[dict]) -> dict:
    return CoverageSummary.from_rows([AcCoverage.model_validate(row) for row in rows]).model_dump(mode="json")


def skip_scenario(root: Path) -> None:
    """Tags ``SKIPPED_SCENARIO_ID`` ``@skip`` in ``ui-tests``, and writes each view's matrix as the toolkit does under
    living-doc-utilities 0.9.0's coverage rule: ``SKIPPED_AC`` not covered, its summaries recomputed, and the link's
    ``SKIPPED_SCENARIO`` warning."""
    data = _json(_ui_tests(root))
    scenario = next(scenario for scenario in data["scenarios"] if scenario["scenario_id"] == SKIPPED_SCENARIO_ID)
    assert [link["id"] for link in scenario["acceptance_criteria"]] == [SKIPPED_AC], scenario
    scenario["tags"].append("@skip")
    _write(_ui_tests(root), data)
    for view in MATRICES:
        data = _json(_matrix(root, view))
        for entity in data["entities"]:
            for row in entity["acceptance_criteria"]:
                if row["ac_id"] == SKIPPED_AC:
                    row.update(status="not_covered", scenario_ids=[])
            entity["summary"] = _summary(entity["acceptance_criteria"])
        data["summary"] = _summary([row for entity in data["entities"] for row in entity["acceptance_criteria"]])
        _write(_matrix(root, view), data)
    warn(root, "SKIPPED_SCENARIO", SKIPPED_AC, SKIPPED_SCENARIO_ID)


def check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECK), "--runner", str(root), str(root / "collector-gh" / "doc-source" / "doc-source.json"),
         str(_ui_tests(root))], capture_output=True, text=True, encoding="utf-8")


def test_the_output_with_no_link_to_a_planned_or_in_review_criterion_passes(root: Path) -> None:
    result = check(root)

    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(("state", "code"), [("planned", "PLANNED_AC_HAS_TESTS"),
                                             ("in_review", "IN_REVIEW_AC_HAS_TESTS")])
def test_a_link_to_a_criterion_the_matrix_does_not_count_expects_its_warning(root: Path, state: str, code: str) -> None:
    ac_id = criterion(root, state)
    warn(root, code, ac_id, link(root, 0, ac_id))

    result = check(root)

    assert result.returncode == 0, result.stdout
    assert f"{code} for AC:{ac_id}" in result.stdout


def test_the_warning_is_expected_once_per_scenario_and_criterion(root: Path) -> None:
    ac_id = criterion(root, "planned")
    first = link(root, 0, ac_id, "one")
    link(root, 0, ac_id, "two")
    second = link(root, 1, ac_id)
    warn(root, "PLANNED_AC_HAS_TESTS", ac_id, first)
    warn(root, "PLANNED_AC_HAS_TESTS", ac_id, second)

    result = check(root)

    assert result.returncode == 0, result.stdout


def test_the_warning_without_a_scenario_that_links_its_criterion_fails(root: Path) -> None:
    ac_id = criterion(root, "planned")
    scenario_id = _json(_ui_tests(root))["scenarios"][0]["scenario_id"]
    warn(root, "PLANNED_AC_HAS_TESTS", ac_id, scenario_id)

    result = check(root)

    assert result.returncode == 1
    assert f"PLANNED_AC_HAS_TESTS for AC:{ac_id}" in result.stdout


def test_a_link_to_a_planned_criterion_without_its_warning_fails(root: Path) -> None:
    ac_id = criterion(root, "planned")
    link(root, 0, ac_id)

    result = check(root)

    assert result.returncode == 1
    assert f"PLANNED_AC_HAS_TESTS for AC:{ac_id}" in result.stdout


def test_the_expected_warning_reported_twice_fails(root: Path) -> None:
    ac_id = criterion(root, "planned")
    scenario_id = link(root, 0, ac_id)
    warn(root, "PLANNED_AC_HAS_TESTS", ac_id, scenario_id)
    warn(root, "PLANNED_AC_HAS_TESTS", ac_id, scenario_id)

    result = check(root)

    assert result.returncode == 1
    assert "reported 2 time(s)" in result.stdout


def test_the_warning_naming_another_scenario_than_the_one_that_links_fails(root: Path) -> None:
    ac_id = criterion(root, "planned")
    link(root, 0, ac_id)
    warn(root, "PLANNED_AC_HAS_TESTS", ac_id, _json(_ui_tests(root))["scenarios"][1]["scenario_id"])

    result = check(root)

    assert result.returncode == 1
    assert "reported 0 time(s)" in result.stdout
    assert "which no link in ui-tests" in result.stdout


def test_the_expected_warning_missing_from_one_view_fails(root: Path) -> None:
    ac_id = criterion(root, "planned")
    warn(root, "PLANNED_AC_HAS_TESTS", ac_id, link(root, 0, ac_id), views=("inner",))

    result = check(root)

    assert result.returncode == 1
    assert "coverage-matrix.release: PLANNED_AC_HAS_TESTS" in result.stdout
    assert "coverage-matrix.inner: PLANNED_AC_HAS_TESTS" not in result.stdout


def test_a_skipped_scenario_without_its_warning_fails(root: Path) -> None:
    for view in MATRICES:
        data = _json(_matrix(root, view))
        data["warnings"] = [warning for warning in data["warnings"] if warning["code"] != "SKIPPED_SCENARIO"]
        data["metadata"]["stats"]["cardinality"]["warnings_by_code"].pop("SKIPPED_SCENARIO")
        _write(_matrix(root, view), data)

    result = check(root)

    assert result.returncode == 1
    assert (f"SKIPPED_SCENARIO for AC:{SKIPPED_AC} (scenario_id={SKIPPED_SCENARIO_ID!r}) reported 0 time(s), "
            "expected once: the scenario is tagged @skip") in result.stdout


def test_a_skipped_scenario_linking_a_planned_criterion_expects_the_planned_warning(root: Path) -> None:
    ac_id = criterion(root, "planned")
    index = next(index for index, scenario in enumerate(_json(_ui_tests(root))["scenarios"])
                 if scenario["scenario_id"] == SKIPPED_SCENARIO_ID)
    warn(root, "PLANNED_AC_HAS_TESTS", ac_id, link(root, index, ac_id))

    result = check(root)

    assert result.returncode == 0, result.stdout
    assert f"PLANNED_AC_HAS_TESTS for AC:{ac_id} (scenario_id={SKIPPED_SCENARIO_ID!r})" in result.stdout
    assert f"SKIPPED_SCENARIO for AC:{ac_id}" not in result.stdout


def test_any_other_warning_still_fails(root: Path) -> None:
    ac_id = criterion(root, "active")
    warn(root, "STALE_AC_REF", ac_id, _json(_ui_tests(root))["scenarios"][0]["scenario_id"])

    result = check(root)

    assert result.returncode == 1
    assert "STALE_AC_REF" in result.stdout
