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
PAGEOBJECT = "pageobject/LoginPage.ts"
US_ISSUE = "gh-issues/us-001-customer-login.md"
FEAT_ISSUE = "gh-issues/feat-001-login-page.md"
FUNC_ISSUE = "gh-issues/func-001-validate-password-strength.md"


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
    # tag every countable (non-planned) declared AC, leaving none uncovered corpus-wide;
    # the planned ACs (US-001-03, FUNC-001-03) are excluded from the invariant either way
    target = corpus_dir / US_FEATURE
    target.write_text(target.read_text(encoding="utf-8").replace(
        "  @AC:US-001-01\n",
        "  @AC:US-001-01\n  @AC:US-001-02\n",
    ), encoding="utf-8")
    func = corpus_dir / FUNC_FEATURE
    func.write_text(func.read_text(encoding="utf-8").replace(
        "  @AC:FUNC-001-01/aspect:minimum-length\n",
        "  @AC:FUNC-001-01/aspect:minimum-length\n  @AC:FUNC-001-02\n",
    ), encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("coverage-pair" in f.rule for f in findings), findings


def test_pageobject_missing_required_field_fails(corpus_dir: Path) -> None:
    target = corpus_dir / PAGEOBJECT
    kept = [ln for ln in target.read_text(encoding="utf-8").splitlines()
            if not ln.lstrip(" *").startswith("route:")]
    target.write_text("\n".join(kept) + "\n", encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(PAGEOBJECT in f.file and "route" in f.rule for f in findings), findings


def test_pageobject_status_field_fails(corpus_dir: Path) -> None:
    target = corpus_dir / PAGEOBJECT
    text = target.read_text(encoding="utf-8").replace(
        " * surface_type:          UI\n",
        " * surface_type:          UI\n * status:                active\n",
    )
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(PAGEOBJECT in f.file and "status:" in f.rule for f in findings), findings


def test_pageobject_stub_reason_is_optional(corpus_dir: Path) -> None:
    target = corpus_dir / PAGEOBJECT
    kept = [ln for ln in target.read_text(encoding="utf-8").splitlines()
            if not ln.lstrip(" *").startswith("stub-reason:")
            and not ln.lstrip(" *").startswith("documented from the interface spec")]
    target.write_text("\n".join(kept) + "\n", encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert not any(PAGEOBJECT in f.file for f in findings), findings


def test_missing_project_profile_fails(corpus_dir: Path) -> None:
    (corpus_dir / "project-profile" / ".project-profile.yaml").unlink()
    findings = findings_for(corpus_dir)
    assert any(".project-profile.yaml" in f.file for f in findings), findings
def test_missing_us_status_heading_fails(corpus_dir: Path) -> None:
    target = corpus_dir / US_ISSUE
    text = target.read_text(encoding="utf-8").replace("## Status\n\nactive\n\n", "")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(US_ISSUE in f.file
               and "required '## Status' heading missing for a US issue body" in f.rule
               for f in findings), findings


def test_missing_func_status_heading_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FUNC_ISSUE
    text = target.read_text(encoding="utf-8").replace("## Status\n\nactive\n\n", "")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(FUNC_ISSUE in f.file
               and "required '## Status' heading missing for a FUNC issue body" in f.rule
               for f in findings), findings


def test_feat_status_heading_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FEAT_ISSUE
    text = target.read_text(encoding="utf-8") + "\n## Status\n\nactive\n"
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(FEAT_ISSUE in f.file
               and "has no place in the FEAT issue-body layout" in f.rule
               for f in findings), findings


def test_deprecated_at_heading_accepted(corpus_dir: Path) -> None:
    target = corpus_dir / FEAT_ISSUE
    text = target.read_text(encoding="utf-8").replace(
        "## External Dependencies\n\nauth-api", "## Deprecated At\n\n2026-09-15")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert not any("Deprecated At" in f.rule for f in findings), findings


def test_deprecation_reason_heading_accepted(corpus_dir: Path) -> None:
    target = corpus_dir / FEAT_ISSUE
    text = target.read_text(encoding="utf-8").replace(
        "## External Dependencies\n\nauth-api",
        "## Deprecation Reason\n\nSuperseded by the passkey sign-in surface.")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert not any("Deprecation Reason" in f.rule for f in findings), findings


def test_superseded_by_heading_accepted(corpus_dir: Path) -> None:
    target = corpus_dir / FEAT_ISSUE
    text = target.read_text(encoding="utf-8").replace(
        "## External Dependencies\n\nauth-api",
        "## Superseded By\n\nthe passkey sign-in surface")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert not any("Superseded By" in f.rule for f in findings), findings


def test_unknown_ac_state_fails(corpus_dir: Path) -> None:
    target = corpus_dir / US_FEATURE
    text = target.read_text(encoding="utf-8").replace(
        "AC:US-001-02 (v1.0.0 - active)", "AC:US-001-02 (v1.0.0 - shipped)")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(US_FEATURE in f.file and "is not a documented state" in f.rule
               for f in findings), findings


def test_non_canonical_dash_in_entity_name_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FUNC_FEATURE
    text = target.read_text(encoding="utf-8").replace(
        "Login Page - Validate Password Strength",
        "Login Page \u2014 Validate Password Strength")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(FUNC_FEATURE in f.file and "NON_CANONICAL_FORM" in f.rule
               for f in findings), findings


def test_version_less_non_planned_ac_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FUNC_FEATURE
    text = target.read_text(encoding="utf-8").replace(
        "AC:FUNC-001-02 (v1.0.0 - active)", "AC:FUNC-001-02 (active)")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(FUNC_FEATURE in f.file and "carries no version" in f.rule
               for f in findings), findings


def test_backlog_ac_without_version_is_accepted(corpus_dir: Path) -> None:
    # Drop the target version from a `planned` AC in both of its forms: it becomes a backlog
    # AC, which the grammar accepts with no version at all.
    for path in (US_FEATURE, US_ISSUE):
        target = corpus_dir / path
        target.write_text(
            target.read_text(encoding="utf-8").replace(
                "AC:US-001-03 (v1.1.0 - planned)", "AC:US-001-03 (planned)"),
            encoding="utf-8")

    assert findings_for(corpus_dir) == []


def test_pair_with_different_ac_sets_fails(corpus_dir: Path) -> None:
    target = corpus_dir / US_ISSUE
    text = target.read_text(encoding="utf-8") + (
        "\n### AC:US-001-05 (v1.0.0 - active)\n\n"
        "- A customer can sign out from the account dashboard.\n")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("PAIR_MISMATCH" in f.rule and "different AC set" in f.rule
               for f in findings), findings


def test_pair_required_content_mismatch_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FEAT_ISSUE
    text = target.read_text(encoding="utf-8").replace("Identity Team", "Platform Team")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("PAIR_MISMATCH" in f.rule and "owners" in f.rule for f in findings), findings


def test_two_optional_field_extensions_fail(corpus_dir: Path) -> None:
    target = corpus_dir / US_ISSUE
    text = target.read_text(encoding="utf-8") + (
        "\n## Preconditions\n\n- A registered customer account exists and is not locked.\n")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(US_ISSUE in f.file and "more than one optional field extension" in f.rule
               for f in findings), findings


def test_retired_project_profile_key_fails(corpus_dir: Path) -> None:
    target = corpus_dir / "project-profile" / ".project-profile.yaml"
    text = target.read_text(encoding="utf-8") + "\npageobject_statuses: [candidate, instrumented]\n"
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(".project-profile.yaml" in f.file and "is retired" in f.rule
               for f in findings), findings
