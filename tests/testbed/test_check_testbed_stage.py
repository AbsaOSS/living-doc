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
"""Tests for tests/testbed/check_testbed_stage.py: the floor of constructs counts a test written ahead, a scenario
that links a criterion its header declares ``planned`` or ``in_review``.

Run: ``python -m pytest tests/testbed -q`` (needs pytest and ``living-doc-utilities``, which
``tests/examples/requirements-examples-check.txt`` installs). Each case writes a one-file checkout and runs ``core``
over an output root with no artifacts: the floor is read from the checkout alone, so the run fails on the missing
artifacts either way, and the case looks only for the floor's line. The stage run over the testbed checks the rest.
Nothing goes online.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHECK = REPO_ROOT / "tests" / "testbed" / "check_testbed_stage.py"
FLOOR = "nothing to assert: the checkout has no scenario that links a planned or in_review criterion"
STORY = """\
# =============================================================================
# LIVING DOC — US-001 · Borrow a book
# =============================================================================
# status:    active
#
# acceptance_criteria:
#
#   AC:US-001-01 {declaration}
#     - The member borrows a book.
# =============================================================================

@US_ID:US-001
Feature: Borrow a book

  {tag}
  Scenario: The member borrows a book
    Given the member is signed in
    When the member borrows "Dune"
    Then "Dune" is on the member's loans
"""


def core(tmp_path: Path, declaration: str, tag: str = "@AC:US-001-01") -> subprocess.CompletedProcess[str]:
    """Runs `core` over a checkout whose one User Story declares `AC:US-001-01 <declaration>` and whose one scenario
    carries `tag`."""
    checkout = tmp_path / "checkout"
    for folder in ("features/us", "features/func", "pages"):
        (checkout / folder).mkdir(parents=True)
    story = STORY.format(declaration=declaration, tag=tag)
    (checkout / "features" / "us" / "us-001-borrow-a-book.feature").write_text(story, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(CHECK), "core", str(tmp_path / "output"), str(checkout), "--us", "features/us",
         "--func", "features/func", "--pages", "pages", "--scenarios", "features"],
        capture_output=True, text=True, encoding="utf-8")


@pytest.mark.parametrize("declaration", ["(v1.2.0 - planned)", "(planned)", "(v1.1.0 - in_review)"])
def test_a_scenario_that_links_a_planned_or_in_review_criterion_meets_the_floor(tmp_path: Path,
                                                                               declaration: str) -> None:
    result = core(tmp_path, declaration)

    assert "nothing to assert: the checkout has no Feature" in result.stdout, result.stdout + result.stderr
    assert FLOOR not in result.stdout, result.stdout


@pytest.mark.parametrize("declaration", ["(v1.0.0 - active)", "(v1.0.0 - deprecated - removal planned v2.0.0)"])
def test_a_scenario_that_links_only_a_counted_criterion_fails_the_floor(tmp_path: Path, declaration: str) -> None:
    result = core(tmp_path, declaration)

    assert result.returncode == 1
    assert FLOOR in result.stdout, result.stdout


def test_a_planned_criterion_no_scenario_links_fails_the_floor(tmp_path: Path) -> None:
    result = core(tmp_path, "(v1.2.0 - planned)", tag="@smoke")

    assert result.returncode == 1
    assert FLOOR in result.stdout, result.stdout
