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

from examples_check import (AC_HEADER_RE, AC_TAG_RE, FEATURE_STOP_RE, FEATURE_STRIP_RE, Corpus,
                            _decomment_block, check_corpus, check_feature_levels)

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_EXAMPLES = REPO_ROOT / "docs" / "examples"
US_FEATURE = "gherkin/liv_doc_us/us-001-customer-login.feature"
FUNC_FEATURE = "gherkin/liv_doc_func/func-001-validate-password-strength.feature"
FUNC2_FEATURE = "gherkin/liv_doc_func/func-002-reject-breached-password.feature"
PAGEOBJECT = "pageobject/LoginPage.ts"
FEAT3_PAGEOBJECT = "pageobject/RegistrationPage.ts"
US_ISSUE = "gh-issues/us-001-customer-login.md"
FEAT_ISSUE = "gh-issues/feat-001-login-page.md"
API_FEAT_ISSUE = "gh-issues/feat-002-breached-password-check.md"
FEAT3_ISSUE = "gh-issues/feat-003-registration-page.md"
FUNC_ISSUE = "gh-issues/func-001-validate-password-strength.md"
FUNC2_ISSUE = "gh-issues/func-002-reject-breached-password.md"


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


@pytest.mark.parametrize("bad_id", ["FEAT-001-02", "JIRA-12-01"])
def test_ac_header_with_non_owner_prefix_fails(corpus_dir: Path, bad_id: str) -> None:
    target = corpus_dir / US_FEATURE
    text = target.read_text(encoding="utf-8").replace(
        "#   AC:US-001-02 (v1.0.0 - active)", f"#   AC:{bad_id} (v1.0.0 - active)"
    )
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(US_FEATURE in f.file and "glossary grammar" in f.rule for f in findings), findings


@pytest.mark.parametrize("bad_id", ["FEAT-001-01", "JIRA-12-01"])
def test_ac_tag_with_non_owner_prefix_fails(corpus_dir: Path, bad_id: str) -> None:
    target = corpus_dir / US_FEATURE
    text = target.read_text(encoding="utf-8").replace("  @AC:US-001-01\n", f"  @AC:{bad_id}\n")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(US_FEATURE in f.file and f"@AC:{bad_id}" in f.rule and "tag format" in f.rule
               for f in findings), findings


@pytest.mark.parametrize("ac_id", ["US-001-01", "FUNC-001-01"])
def test_ac_header_accepts_owner_prefix(ac_id: str) -> None:
    m = AC_HEADER_RE.match(f"AC:{ac_id} (v1.0.0 - active)")
    assert m is not None and m.group("id") == ac_id


@pytest.mark.parametrize("ac_id", ["US-001-01", "FUNC-001-01"])
def test_ac_tag_accepts_owner_prefix(ac_id: str) -> None:
    m = AC_TAG_RE.match(f"@AC:{ac_id}/aspect:minimum-length")
    assert m is not None and m.group("id") == ac_id


def test_issue_body_extra_heading_fails(corpus_dir: Path) -> None:
    target = corpus_dir / "gh-issues/us-001-customer-login.md"
    text = target.read_text(encoding="utf-8") + "\n## Implementation Notes\n\nnope\n"
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("Implementation Notes" in f.rule for f in findings), findings


def test_coverage_pair_broken_when_every_ac_covered(corpus_dir: Path) -> None:
    # tag every countable (non-planned) declared AC, leaving none uncovered corpus-wide;
    # the planned ACs (US-001-03, FUNC-002-01) are excluded from the invariant either way
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


def test_pageobject_deprecated_at_field_fails(corpus_dir: Path) -> None:
    # The source-code twin of test_feat_deprecated_at_heading_fails: a Feature's deprecation date
    # is derived, so the PageObject form has no place for it either.
    target = corpus_dir / PAGEOBJECT
    text = target.read_text(encoding="utf-8").replace(
        " * surface_type:          UI\n",
        " * surface_type:          UI\n * deprecated_at:         2026-09-15\n",
    )
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    match = [f for f in findings if PAGEOBJECT in f.file and "deprecated_at:" in f.rule]
    assert match, findings
    # The hint must use the header's own syntax, not the issue body's headings.
    assert "'deprecation_reason:'" in match[0].hint, match[0].hint


def test_pageobject_stub_reason_is_optional(corpus_dir: Path) -> None:
    target = corpus_dir / PAGEOBJECT
    kept = [ln for ln in target.read_text(encoding="utf-8").splitlines()
            if not ln.lstrip(" *").startswith("stub-reason:")
            and not ln.lstrip(" *").startswith("documented from the interface spec")]
    target.write_text("\n".join(kept) + "\n", encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert not any(PAGEOBJECT in f.file for f in findings), findings


def test_pageobject_surface_type_service_fails(corpus_dir: Path) -> None:
    target = corpus_dir / PAGEOBJECT
    text = target.read_text(encoding="utf-8").replace(
        " * surface_type:          UI\n",
        " * surface_type:          Service\n",
    )
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(PAGEOBJECT in f.file and "is not 'UI'" in f.rule for f in findings), findings


def test_pageobject_surface_type_api_fails(corpus_dir: Path) -> None:
    target = corpus_dir / PAGEOBJECT
    text = target.read_text(encoding="utf-8").replace(
        " * surface_type:          UI\n",
        " * surface_type:          API\n",
    )
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(PAGEOBJECT in f.file and "is not 'UI'" in f.rule for f in findings), findings


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
    match = [f for f in findings
             if FEAT_ISSUE in f.file
             and "'## Status' has no place in the FEAT issue-body layout" in f.rule]
    assert match, findings
    # The hint is per heading, so assert this heading's own advice - not the other's.
    assert "remove the heading" in match[0].hint, match[0].hint


def test_feat_surface_type_worker_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FEAT_ISSUE
    text = target.read_text(encoding="utf-8").replace(
        "## Surface Type\n\nUI\n", "## Surface Type\n\nWorker\n")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(FEAT_ISSUE in f.file and "is not documented" in f.rule and "Worker" in f.rule
               for f in findings), findings


def test_feat_deprecated_at_heading_fails(corpus_dir: Path) -> None:
    # A Feature's deprecation date is derived with its state, so the heading has no home here.
    target = corpus_dir / FEAT_ISSUE
    text = target.read_text(encoding="utf-8") + "\n## Deprecated At\n\n2026-09-15\n"
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    match = [f for f in findings
             if FEAT_ISSUE in f.file
             and "'## Deprecated At' has no place in the FEAT issue-body layout" in f.rule]
    assert match, findings
    # The hint is user-facing tool output and the whole point of the per-heading dict: a Feature
    # author must be told to keep the two fields that stay authored, not given the `## Status`
    # advice to remove the heading.
    assert "derived with the state" in match[0].hint, match[0].hint
    assert "keep '## Deprecation Reason'" in match[0].hint, match[0].hint


def test_us_deprecated_at_heading_accepted(corpus_dir: Path) -> None:
    # `## Deprecated At` stays optional on a User Story. Swap it in for `## Not In Scope` rather
    # than adding it alongside, so the file keeps exactly one optional field extension.
    target = corpus_dir / US_ISSUE
    text = target.read_text(encoding="utf-8").replace(
        "## Not In Scope\n\n"
        "- Social-identity (OAuth) sign-in — tracked separately as US-002.\n",
        "## Deprecated At\n\n2026-09-15\n")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert not any("Deprecated At" in f.rule for f in findings), findings


def test_notes_heading_is_optional(corpus_dir: Path) -> None:
    # The corpus's single `## Notes` instance lives in the FEAT issue body (its presence is
    # covered by test_pristine_corpus_passes); dropping it must change nothing.
    target = corpus_dir / FEAT_ISSUE
    text = target.read_text(encoding="utf-8")
    target.write_text(text[:text.index("\n## Notes\n")] + "\n", encoding="utf-8")

    assert findings_for(corpus_dir) == []


def test_notes_heading_is_not_an_optional_field_extension(corpus_dir: Path) -> None:
    # `## Notes` is exempt from the one-extension rule: FUNC already spends its extension on
    # `## Rationale`, and a second entity type carrying `## Notes` must still validate clean.
    target = corpus_dir / FUNC_ISSUE
    text = target.read_text(encoding="utf-8") + (
        "\n## Notes\n\n"
        "- The complexity policy is owned by the account service; this check mirrors it client-side.\n")
    target.write_text(text, encoding="utf-8")

    assert findings_for(corpus_dir) == []


def test_us_notes_heading_accepted(corpus_dir: Path) -> None:
    # The third entity type. The User Story is the strongest case for the one-extension exemption:
    # `us-001` already spends its extension on `## Not In Scope`, so `## Notes` arrives alongside it.
    target = corpus_dir / US_ISSUE
    text = target.read_text(encoding="utf-8") + (
        "\n## Notes\n\n"
        "- The customer-facing name of this flow is \"Sign in\"; the test suite uses the US title.\n")
    target.write_text(text, encoding="utf-8")

    assert findings_for(corpus_dir) == []


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


# --- feature_dependencies: the four rules a declared edge must satisfy --------------------
#
# These are the first checks the canon can make on a dependency at all: a free-form
# `external_dependencies` name resolves to nothing, while a `FEAT-` id can be resolved,
# surface-typed and lifecycle-checked. One negative case each, on FEAT-003's PageObject form.

FEAT3_PO_DEPS = " * feature_dependencies:  FEAT-002\n"


def _repoint_feat3_po(corpus_dir: Path, value: str) -> None:
    target = corpus_dir / FEAT3_PAGEOBJECT
    target.write_text(target.read_text(encoding="utf-8").replace(
        FEAT3_PO_DEPS, f" * feature_dependencies:  {value}\n"), encoding="utf-8")


def test_feature_dependency_unknown_target_fails(corpus_dir: Path) -> None:
    _repoint_feat3_po(corpus_dir, "FEAT-404")

    findings = findings_for(corpus_dir)
    assert any(FEAT3_PAGEOBJECT in f.file
               and "feature_dependencies target 'FEAT-404' has no matching entity" in f.rule
               for f in findings), findings


def test_feature_dependency_self_reference_fails(corpus_dir: Path) -> None:
    _repoint_feat3_po(corpus_dir, "FEAT-003")

    findings = findings_for(corpus_dir)
    assert any(FEAT3_PAGEOBJECT in f.file
               and "feature_dependencies target 'FEAT-003' is the declaring Feature itself"
               in f.rule for f in findings), findings
    # The self-reference is reported on its own — not also as a surface-type failure.
    assert not any("is not an 'API' Feature" in f.rule for f in findings), findings


def test_feature_dependency_ui_target_fails(corpus_dir: Path) -> None:
    # Retyping FEAT-002 also drops it to two expected forms, so a PAIR_MISMATCH rides along.
    target = corpus_dir / API_FEAT_ISSUE
    target.write_text(target.read_text(encoding="utf-8").replace(
        "## Surface Type\n\nAPI\n", "## Surface Type\n\nUI\n"), encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(FEAT3_PAGEOBJECT in f.file
               and "feature_dependencies target 'FEAT-002' is not an 'API' Feature" in f.rule
               and "surface type: UI" in f.rule
               for f in findings), findings


def test_feature_dependency_deprecated_target_fails(corpus_dir: Path) -> None:
    # A Feature's deprecation is derived, so what marks a retiring surface in its authored
    # form is the deprecation metadata it does carry.
    target = corpus_dir / API_FEAT_ISSUE
    target.write_text(target.read_text(encoding="utf-8")
                      + "\n## Deprecation Reason\n\nReplaced by the credential-risk service.\n",
                      encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(FEAT3_PAGEOBJECT in f.file
               and "feature_dependencies target 'FEAT-002' is being retired" in f.rule
               for f in findings), findings


# --- feature_dependencies: where it may and may not be authored ---------------------------


def test_feature_dependencies_is_optional(corpus_dir: Path) -> None:
    # Omitted when the Feature calls nothing: drop it from both FEAT-003 forms.
    po = corpus_dir / FEAT3_PAGEOBJECT
    po.write_text(po.read_text(encoding="utf-8").replace(FEAT3_PO_DEPS, ""), encoding="utf-8")
    issue = corpus_dir / FEAT3_ISSUE
    text = issue.read_text(encoding="utf-8")
    issue.write_text(text[:text.index("\n## Feature Dependencies\n")] + "\n", encoding="utf-8")

    assert findings_for(corpus_dir) == []


@pytest.mark.parametrize("path", [FEAT3_PAGEOBJECT, FEAT3_ISSUE])
def test_feature_dependencies_none_value_fails(corpus_dir: Path, path: str) -> None:
    target = corpus_dir / path
    text = target.read_text(encoding="utf-8")
    if path == FEAT3_PAGEOBJECT:
        text = text.replace(FEAT3_PO_DEPS, " * feature_dependencies:  none\n")
    else:
        text = text.replace("## Feature Dependencies\n\nFEAT-002\n",
                            "## Feature Dependencies\n\nnone\n")
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    match = [f for f in findings
             if path in f.file and "feature_dependencies has no 'none' value" in f.rule]
    assert match, findings
    assert "omit the field" in match[0].hint, match[0].hint


def test_func_feature_file_feature_dependencies_key_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FUNC2_FEATURE
    target.write_text(target.read_text(encoding="utf-8").replace(
        "# func_type: field_validation\n",
        "# func_type: field_validation\n# feature_dependencies: FEAT-002\n"), encoding="utf-8")

    findings = findings_for(corpus_dir)
    match = [f for f in findings
             if FUNC2_FEATURE in f.file
             and "Functionality header carries a 'feature_dependencies:' field" in f.rule]
    assert match, findings
    assert "parent Feature" in match[0].hint, match[0].hint


def test_func_feature_dependencies_heading_fails(corpus_dir: Path) -> None:
    target = corpus_dir / FUNC2_ISSUE
    target.write_text(target.read_text(encoding="utf-8")
                      + "\n## Feature Dependencies\n\nFEAT-002\n", encoding="utf-8")

    findings = findings_for(corpus_dir)
    match = [f for f in findings
             if FUNC2_ISSUE in f.file
             and "'## Feature Dependencies' has no place in the FUNC issue-body layout" in f.rule]
    assert match, findings
    assert "parent Feature" in match[0].hint, match[0].hint


def test_us_feature_dependencies_heading_fails(corpus_dir: Path) -> None:
    target = corpus_dir / US_ISSUE
    target.write_text(target.read_text(encoding="utf-8")
                      + "\n## Feature Dependencies\n\nFEAT-002\n", encoding="utf-8")

    findings = findings_for(corpus_dir)
    match = [f for f in findings
             if US_ISSUE in f.file
             and "'## Feature Dependencies' has no place in the US issue-body layout" in f.rule]
    assert match, findings
    assert "declared by the Feature" in match[0].hint, match[0].hint


def test_us_feature_file_feature_dependencies_key_fails(corpus_dir: Path) -> None:
    target = corpus_dir / US_FEATURE
    target.write_text(target.read_text(encoding="utf-8").replace(
        "# status:          active", "# status:          active\n# feature_dependencies: FEAT-002"),
        encoding="utf-8")

    findings = findings_for(corpus_dir)
    match = [f for f in findings
             if US_FEATURE in f.file
             and "User Story header carries a 'feature_dependencies:' field" in f.rule]
    assert match, findings
    assert "declared by the Feature" in match[0].hint, match[0].hint


def test_cross_reference_feature_dependencies_field_fails(corpus_dir: Path) -> None:
    xref = "pageobject/RegistrationConsentPage.ts"
    (corpus_dir / xref).write_text(
        "/* =============================================================================\n"
        " * LIVING DOC — FEAT-003 · Registration Page  [cross-reference]\n"
        " * =============================================================================\n"
        " * parent-feat:          FEAT-003\n"
        " * route:                /register\n"
        " * owners:               Identity Team\n"
        " * purpose:              The consent step of account registration.\n"
        " * feature_dependencies: FEAT-002\n"
        " * page-object:          RegistrationConsentPage.ts\n"
        " * ============================================================================= */\n",
        encoding="utf-8")

    findings = findings_for(corpus_dir)
    match = [f for f in findings
             if xref in f.file
             and "cross-reference header carries a 'feature_dependencies:' field" in f.rule]
    assert match, findings
    assert "primary Feature file" in match[0].hint, match[0].hint


def test_api_feature_with_two_forms_fails(corpus_dir: Path) -> None:
    # The Part 3b rule, enforced: an API contract anchor carries no living-doc header yet, so
    # a second authored form of an API Feature cannot exist.
    target = corpus_dir / PAGEOBJECT
    text = target.read_text(encoding="utf-8").replace(
        "FEAT-001 · Login Page", "FEAT-002 · Breached Password Check")
    (corpus_dir / "pageobject" / "BreachedPasswordCheckPage.ts").write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any("FEAT-002 must have exactly 1 authored form(s) (found 2)" in f.rule
               for f in findings), findings


def test_retired_project_profile_key_fails(corpus_dir: Path) -> None:
    target = corpus_dir / "project-profile" / ".project-profile.yaml"
    text = target.read_text(encoding="utf-8") + "\npageobject_statuses: [candidate, instrumented]\n"
    target.write_text(text, encoding="utf-8")

    findings = findings_for(corpus_dir)
    assert any(".project-profile.yaml" in f.file and "is retired" in f.rule
               for f in findings), findings


# --- indentation: the corpus uses the template levels only --------------------------------
#
# The check is stricter than the canon: the flat layout stays valid for authors, but the corpus
# shows only the canonical levels (living-doc-header-types.md#indentation).

US_HEADER = """\
# =============================================================================
# LIVING DOC — US-001 · Customer Login
# =============================================================================
# status:          active
# business_value:
#   - Registered customers can reach their account area, so returning users
#     convert without friction.
#
# acceptance_criteria:
#
#   AC:US-001-01 (v1.0.0 - active)
#     - A customer who submits valid credentials lands on the account dashboard.
#     preconditions:
#       - A registered customer account exists and is not locked.
#
#   AC:US-001-02 (v1.0.0 - active)
#     - An inline error is shown when the customer submits invalid credentials,
#       without leaving the login screen.
# =============================================================================
"""


def test_feature_header_template_levels_pass() -> None:
    raw = US_HEADER.splitlines()
    corpus = Corpus()
    check_feature_levels(_decomment_block(raw, FEATURE_STRIP_RE, FEATURE_STOP_RE), raw, corpus,
                         US_FEATURE)
    assert corpus.findings == []


def _mutate(corpus_dir: Path, path: str, old: str, new: str) -> None:
    target = corpus_dir / path
    text = target.read_text(encoding="utf-8")
    assert old in text, old
    target.write_text(text.replace(old, new), encoding="utf-8")


def test_criterion_item_at_3_fails(corpus_dir: Path) -> None:
    _mutate(corpus_dir, US_FEATURE, "#     - A customer who submits valid",
            "#    - A customer who submits valid")

    findings = findings_for(corpus_dir)
    assert any(US_FEATURE in f.file and f.rule == "criterion item at indent 3, expected 4"
               for f in findings), findings


def test_flat_layout_sub_key_items_fail(corpus_dir: Path) -> None:
    # Valid for an author, read by line order - but not the corpus's canonical form.
    _mutate(corpus_dir, US_FEATURE, "#       - A registered customer account",
            "#     - A registered customer account")

    findings = findings_for(corpus_dir)
    assert any(US_FEATURE in f.file and f.rule == "sub-key item at indent 4, expected 6"
               for f in findings), findings


def test_tab_in_indent_fails(corpus_dir: Path) -> None:
    _mutate(corpus_dir, US_FEATURE, "#     - A customer who submits valid",
            "#   \t- A customer who submits valid")

    findings = findings_for(corpus_dir)
    assert any(US_FEATURE in f.file and f.rule == "tab or no-break space in an indent"
               for f in findings), findings


def test_nested_item_under_id_list_heading_fails(corpus_dir: Path) -> None:
    _mutate(corpus_dir, FEAT_ISSUE, "## Functionalities\n\nFUNC-001, FUNC-002\n",
            "## Functionalities\n\n- FUNC-001\n  - FUNC-002\n")

    findings = findings_for(corpus_dir)
    assert any(FEAT_ISSUE in f.file and f.rule == "nested item under '## Functionalities', "
               "expected 0" for f in findings), findings


def test_pageobject_wrapped_line_at_key_indent_fails(corpus_dir: Path) -> None:
    _mutate(corpus_dir, PAGEOBJECT, " *                        documented from the interface spec",
            " * documented from the interface spec")

    findings = findings_for(corpus_dir)
    assert any(PAGEOBJECT in f.file
               and f.rule == "wrapped line at indent 0, expected deeper than its key at 0"
               for f in findings), findings
