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
"""Tests for tools/examples_check.py — the docs/examples corpus validator.

Run: ``python -m pytest tools/test_examples_check.py`` (needs pytest + PyYAML;
see tools/requirements-examples-check.txt).
Each mutation test copies the real corpus, breaks one thing, and asserts the check
reports it by file + rule.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from examples_check import check_corpus

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_EXAMPLES = REPO_ROOT / "docs" / "examples"
US_FEATURE = "gherkin/liv_doc_us/us-001-customer-login.feature"
FUNC_FEATURE = "gherkin/liv_doc_func/func-001-validate-password-strength.feature"


@pytest.fixture
def corpus_dir(tmp_path: Path) -> Path:
    dest = tmp_path / "docs" / "examples"
    dest.parent.mkdir(parents=True)
    shutil.copytree(REAL_EXAMPLES, dest)
    return dest


def findings_for(corpus_dir: Path) -> list:
    return check_corpus(corpus_dir)


def test_pristine_corpus_passes() -> None:
    assert findings_for(REAL_EXAMPLES) == [], "the committed corpus must validate clean"


def test_missing_required_header_field_fails(corpus_dir: Path) -> None:
    target = corpus_dir / US_FEATURE
    kept = [ln for ln in target.read_text(encoding="utf-8").splitlines()
            if not ln.strip().startswith("# status:")]
    target.write_text("\n".join(kept) + "\n", encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(US_FEATURE in f.file and "status" in f.rule for f in findings), findings


def test_undeclared_ac_tag_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FUNC_FEATURE
    text = target.read_text(encoding="utf-8").replace(
        "@AC:FUNC-001-01/aspect:minimum-length",
        "@AC:FUNC-001-99/aspect:minimum-length",
    )
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(FUNC_FEATURE in f.file and "FUNC-001-99" in f.rule for f in findings), findings


def test_unknown_aspect_value_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FUNC_FEATURE
    text = target.read_text(encoding="utf-8").replace(
        "@AC:FUNC-001-01/aspect:character-classes",
        "@AC:FUNC-001-01/aspect:entropy-score",
    )
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("entropy-score" in f.rule for f in findings), findings


def test_dangling_parent_link_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FUNC_FEATURE
    text = target.read_text(encoding="utf-8").replace("parent:    FEAT-001", "parent:    FEAT-404")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("FEAT-404" in f.rule for f in findings), findings


def test_broken_ac_grammar_fails(corpus_dir: Path) -> None:
    target = corpus_dir / US_FEATURE
    text = target.read_text(encoding="utf-8").replace(
        "AC:US-001-02 (v1.0.0 - active)", "AC:US-001-02 (1.0 active)"
    )
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("glossary grammar" in f.rule for f in findings), findings


def test_issue_body_extra_heading_fails(corpus_dir: Path) -> None:
    target = corpus_dir / "gh-issues/us-001-customer-login.md"
    text = target.read_text(encoding="utf-8") + "\n## Implementation Notes\n\nnope\n"
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("Implementation Notes" in f.rule for f in findings), findings


def test_coverage_pair_broken_when_every_ac_covered(corpus_dir: Path) -> None:
    target = corpus_dir / US_FEATURE
    text = target.read_text(encoding="utf-8").replace(
        "  @AC:US-001-01\n  Scenario: Customer signs in with valid credentials",
        "  @AC:US-001-01\n  @AC:US-001-02\n  Scenario: Customer signs in with valid credentials",
    )
    target.write_text(text, encoding="utf-8")
    # also cover both FUNC ACs so nothing is left uncovered corpus-wide
    func = corpus_dir / FUNC_FEATURE
    func.write_text(func.read_text(encoding="utf-8").replace(
        "@AC:FUNC-001-01/aspect:character-classes",
        "@AC:FUNC-001-02",
    ), encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("coverage-pair" in f.rule for f in findings), findings


def test_missing_project_profile_fails(corpus_dir: Path) -> None:
    (corpus_dir / "project-profile" / ".project-profile.yaml").unlink()
    findings = findings_for(corpus_dir)
    assert any(".project-profile.yaml" in f.file for f in findings), findings
