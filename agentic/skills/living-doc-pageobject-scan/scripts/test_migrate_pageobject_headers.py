#!/usr/bin/env python3
"""
Tests for migrate_pageobject_headers.py — the migration path for PageObject headers written
before the canon dropped a surface's state and a Feature's deprecation date.

Covers Authoring formats' "Common mistakes" table: `status:` and `deprecated_at:` are removed,
`type:`/`owner:` are renamed (and `type: screen` becomes `surface_type: UI`), the retirement
keys that stay are left alone, `feature_dependencies: none` and a missing required key are
reported for a human, and a header already at the canon reports nothing.
"""
__test__ = False  # pytest: ignore this helper script

import sys
import tempfile
from pathlib import Path

from migrate_pageobject_headers import header_bounds, scan_file

CANONICAL = """\
/* =============================================================================
 * LIVING DOC — FEAT-001 · Login Page
 * =============================================================================
 * surface_type:          UI
 * route:                 /login
 * owners:                Identity Team
 * purpose:               The sign-in screen.
 * user_stories:          US-001
 * functionalities:       FUNC-001
 * external_dependencies: none
 * page-object:           LoginPage.ts
 * ============================================================================= */
export class LoginPage {}
"""

LEGACY = """\
/* =============================================================================
 * LIVING DOC — FEAT-007 · Legacy Reports
 * =============================================================================
 * type:                  screen
 * route:                 /reports
 * owner:                 Reporting Team
 * status:                active
 * deprecated_at:         2026-05-01
 * deprecation_reason:    Replaced by the new dashboard
 * superseded_by:         FEAT-012
 * purpose:               The legacy reports screen.
 * user_stories:          US-030
 * functionalities:       FUNC-044
 * external_dependencies: none
 * page-object:           OldPage.ts
 * ============================================================================= */
export class OldPage {}
"""


def _scan(text: str) -> dict:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "Page.ts"
        p.write_text(text, encoding="utf-8")
        return scan_file(p)


def _actions(result: dict, key: str) -> list[str]:
    return [f["action"] for f in result["findings"] if f["key"] == key]


def test_canonical_header_reports_nothing():
    """A header already at the canon must not be touched — the migration is a no-op on it."""
    result = _scan(CANONICAL)
    assert result["findings"] == [], result["findings"]
    assert result["lines"] is None
    print("✓ A header already at the canon reports nothing")


def test_status_and_deprecated_at_are_removed():
    """A surface has no status, and a Feature has no deprecation date — both lines go."""
    result = _scan(LEGACY)
    assert _actions(result, "status") == ["remove"], result["findings"]
    assert _actions(result, "deprecated_at") == ["remove"], result["findings"]
    migrated = "".join(result["lines"])
    assert "status:" not in migrated and "deprecated_at:" not in migrated, migrated
    print("✓ status: and deprecated_at: are removed")


def test_retirement_keys_are_kept():
    """`deprecation_reason:` and `superseded_by:` are the keys that record a retirement; the
    migration must not take them with the state it removes."""
    migrated = "".join(_scan(LEGACY)["lines"])
    assert "deprecation_reason:    Replaced by the new dashboard" in migrated, migrated
    assert "superseded_by:         FEAT-012" in migrated, migrated
    print("✓ deprecation_reason: and superseded_by: survive the migration")


def test_type_and_owner_are_renamed_with_the_canonical_value():
    """`type: screen` is `surface_type: UI` — the key and the value are both wrong before."""
    result = _scan(LEGACY)
    assert _actions(result, "type") == ["rename"], result["findings"]
    assert _actions(result, "owner") == ["rename"], result["findings"]
    migrated = "".join(result["lines"])
    assert "surface_type:          UI" in migrated, migrated
    assert "owners:                Reporting Team" in migrated, migrated
    print("✓ type:/owner: are renamed, and type: screen becomes surface_type: UI")


def test_value_column_is_preserved():
    """A header's values sit in one column; a key rename must not leave the block ragged."""
    migrated = "".join(_scan(LEGACY)["lines"])
    columns = {
        line.index(line.split(":", 1)[1].strip())
        for line in migrated.splitlines()
        if ":" in line and line.strip().startswith("*") and line.split(":", 1)[1].strip()
        and not line.strip().startswith("* LIVING DOC")
    }
    assert len(columns) == 1, f"values should share one column, got {sorted(columns)}"
    print("✓ The value column survives a key rename")


def test_migration_is_idempotent():
    """Running it twice changes nothing the second time."""
    once = "".join(_scan(LEGACY)["lines"])
    assert _scan(once)["findings"] == [], _scan(once)["findings"]
    print("✓ The migration is idempotent")


def test_stub_status_without_reason_needs_a_human():
    """`status: STUB` is the only record that a surface is not instrumented. Removing it with
    no `stub-reason:` present would lose that, so it is reported rather than dropped."""
    text = CANONICAL.replace(" * route:", " * status:                STUB\n * route:")
    result = _scan(text)
    assert _actions(result, "status") == ["needs-human"], result["findings"]
    print("✓ status: STUB with no stub-reason: is reported, not silently dropped")


def test_stub_status_with_reason_is_removed():
    """With `stub-reason:` already written, the status carries nothing and can go."""
    text = CANONICAL.replace(
        " * route:",
        " * stub-reason:           No test-id attributes yet.\n * status:                STUB\n * route:")
    result = _scan(text)
    assert _actions(result, "status") == ["remove"], result["findings"]
    print("✓ status: STUB alongside a stub-reason: is removed")


def test_feature_dependencies_none_needs_a_human():
    """The field has no `none` value: the key is omitted instead, which is not a safe rewrite."""
    text = CANONICAL.replace(" * page-object:", " * feature_dependencies:  none\n * page-object:")
    result = _scan(text)
    assert _actions(result, "feature_dependencies") == ["needs-human"], result["findings"]
    print("✓ feature_dependencies: none is reported for a human")


def test_missing_required_key_is_reported():
    """`user_stories:` takes `none`; it is not optional, so its absence is a finding."""
    text = CANONICAL.replace(" * user_stories:          US-001\n", "")
    result = _scan(text)
    assert _actions(result, "user_stories") == ["needs-human"], result["findings"]
    print("✓ A missing required key is reported")


def test_file_without_a_living_doc_header_is_skipped():
    """A source file with no living-doc header is not a PageObject this tool touches."""
    result = _scan("export class Plain {}\n")
    assert result["findings"] == [] and result["lines"] is None
    assert header_bounds(["export class Plain {}"]) is None
    print("✓ A file with no living-doc header is skipped")


if __name__ == "__main__":
    try:
        test_canonical_header_reports_nothing()
        test_status_and_deprecated_at_are_removed()
        test_retirement_keys_are_kept()
        test_type_and_owner_are_renamed_with_the_canonical_value()
        test_value_column_is_preserved()
        test_migration_is_idempotent()
        test_stub_status_without_reason_needs_a_human()
        test_stub_status_with_reason_is_removed()
        test_feature_dependencies_none_needs_a_human()
        test_missing_required_key_is_reported()
        test_file_without_a_living_doc_header_is_skipped()
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
