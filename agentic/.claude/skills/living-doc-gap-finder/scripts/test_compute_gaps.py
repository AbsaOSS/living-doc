#!/usr/bin/env python3
"""
Quick test to verify compute_gaps.py's Gap 3 (FEATURE_WITHOUT_USER_STORY) honours both link
directions.

Regression coverage for the bug flagged in PR #9 review: Gap 3 only checked a
Feature's own `user_stories` back-link; it ignored `features_linked_from_us`
(already built earlier from the forward `us.features` link), so a Feature linked
only from the User Story side was falsely reported FEATURE_WITHOUT_USER_STORY — inconsistent
with Gap 4, which honours both directions.
"""
__test__ = False  # pytest: ignore this helper script

import sys

from compute_gaps import compute_gaps, coverage_stats


def _feature_without_us_ids(snapshot: dict) -> list[str]:
    return [g["entity"] for g in compute_gaps(snapshot) if g["type"] == "FEATURE_WITHOUT_USER_STORY"]


def test_feature_linked_only_from_us_side_not_orphan():
    """A Feature with an empty own user_stories list, but referenced via a User
    Story's forward `features` link, must not be flagged FEATURE_WITHOUT_USER_STORY."""
    snapshot = {
        "catalog": {
            "user_stories": [{"id": "US-001", "title": "Do a thing", "features": ["FEAT-001"]}],
            "features": [{"id": "FEAT-001", "name": "Some Surface", "user_stories": []}],
            "functionalities": [],
        },
        "known_test_links": {},
    }
    assert _feature_without_us_ids(snapshot) == [], "back-linked Feature must not be flagged"
    print("✓ Feature linked only via the User Story's forward link is not flagged orphan")


def test_feature_with_own_forward_link_not_orphan():
    """A Feature whose own user_stories list is non-empty must not be flagged
    (this was already correct — guards against a regression)."""
    snapshot = {
        "catalog": {
            "user_stories": [{"id": "US-001", "title": "Do a thing"}],
            "features": [{"id": "FEAT-001", "name": "Some Surface", "user_stories": ["US-001"]}],
            "functionalities": [],
        },
        "known_test_links": {},
    }
    assert _feature_without_us_ids(snapshot) == [], "Feature with its own forward link must not be flagged"
    print("✓ Feature with its own forward user_stories link is not flagged orphan")


def test_truly_unlinked_feature_still_flagged():
    """A Feature genuinely linked from neither side must still be flagged — the
    fix must not silently suppress real orphans."""
    snapshot = {
        "catalog": {
            "user_stories": [{"id": "US-001", "title": "Unrelated", "features": []}],
            "features": [{"id": "FEAT-001", "name": "Orphan Surface", "user_stories": []}],
            "functionalities": [],
        },
        "known_test_links": {},
    }
    assert _feature_without_us_ids(snapshot) == ["FEAT-001"], "genuinely unlinked Feature must be flagged"
    print("✓ A Feature linked from neither side is still correctly flagged orphan")


# ── AC variants: coverage per declared value, and DEC-74's weighted figure ───────────


def _variant_snapshot() -> dict:
    """One AC covered 1 of 3 declared values, one covered AC without variants, one covered
    0 of 2 — the three coverage states in one snapshot."""
    return {
        "catalog": {
            "user_stories": [{
                "id": "US-001",
                "acceptance_criteria": [
                    {"id": "AC:US-001-01", "aspect": ["email", "sms", "push"]},
                    {"id": "AC:US-001-02"},
                    {"id": "AC:US-001-03", "aspect": ["blank", "malformed"]},
                ],
            }],
            "features": [],
            "functionalities": [],
        },
        "inventory": {},
        "known_test_links": {
            "AC:US-001-01/channel:email": "t.feature::sent by email",
            "AC:US-001-01/channel:sms": None,
            "AC:US-001-01/channel:push": None,
            "AC:US-001-02": "t.feature::link expires",
            "AC:US-001-03": None,
        },
    }


def test_partially_covered_ac_is_its_own_gap():
    """An AC with a scenario for some of its declared values is PARTIALLY_TESTED_AC, and only
    the missing values are proposed — the covered ones need no scenario."""
    gaps = {g["entity"]: g for g in compute_gaps(_variant_snapshot())}
    partial = gaps["AC:US-001-01"]
    assert partial["type"] == "PARTIALLY_TESTED_AC", partial
    assert "1/3" in partial["description"], partial["description"]
    assert "sms" in partial["description"] and "push" in partial["description"], partial
    assert "email" not in partial["description"], "a covered value must not be queued"
    print("✓ A 1-of-3 keyword AC is PARTIALLY_TESTED_AC, listing only the missing values")


def test_ac_with_no_covered_value_is_untested():
    """No value covered is not_covered, the blocker — not a partial gap."""
    gaps = {g["entity"]: g for g in compute_gaps(_variant_snapshot())}
    untested = gaps["AC:US-001-03"]
    assert untested["type"] == "UNTESTED_AC", untested
    assert untested["severity"] == "Blocker", untested
    assert "0/2" in untested["description"], untested["description"]
    print("✓ An AC with no covered value is UNTESTED_AC")


def test_fully_covered_ac_is_no_gap():
    """An AC without variants and with a link is covered; it must raise no AC gap."""
    entities = [g["entity"] for g in compute_gaps(_variant_snapshot()) if g["type"].endswith("_AC")]
    assert "AC:US-001-02" not in entities, entities
    print("✓ A covered AC raises no coverage gap")


def test_bare_tag_covers_every_declared_value():
    """A bare `@AC:<id>` link covers the whole AC — every declared value at once (DEC-76)."""
    snapshot = _variant_snapshot()
    snapshot["known_test_links"] = {"AC:US-001-01": "t.feature::data-driven"}
    snapshot["catalog"]["user_stories"][0]["acceptance_criteria"] = [
        {"id": "AC:US-001-01", "aspect": ["email", "sms", "push"]}
    ]
    assert [g for g in compute_gaps(snapshot) if g["type"].endswith("_AC")] == []
    stats = coverage_stats(snapshot, [])
    assert stats["covered_acs"] == 1 and stats["coverage_pct"] == 100.0, stats
    print("✓ A bare tag counts for every declared value")


def test_weighted_coverage_figure():
    """DEC-74: a covered AC counts 1, not_covered 0, partially_covered its covered values over
    its declared values; computed from exact fractions and rounded once, one decimal."""
    stats = coverage_stats(_variant_snapshot(), [])
    assert stats["counted_acs"] == 3, stats
    assert (stats["covered_acs"], stats["partially_covered_acs"], stats["not_covered_acs"]) == (1, 1, 1), stats
    # (1/3 + 1 + 0) / 3 * 100 = 44.44… -> 44.4
    assert stats["coverage_pct"] == 44.4, stats
    print("✓ The weighted coverage figure follows the three-state formula")


def test_coverage_figure_rounds_half_up():
    """Rounded half up, not with Python's banker's rounding: 81.25 is 81.3, not 81.2."""
    snapshot = {
        "catalog": {"user_stories": [{"id": "US-001", "acceptance_criteria": [
            {"id": "AC:US-001-01", "aspect": [f"v{i}" for i in range(16)]}]}],
            "features": [], "functionalities": []},
        "inventory": {},
        "known_test_links": {f"AC:US-001-01/a:v{i}": ("t" if i < 13 else None) for i in range(16)},
    }
    assert coverage_stats(snapshot, [])["coverage_pct"] == 81.3, coverage_stats(snapshot, [])
    print("✓ The coverage figure rounds half up")


def test_coverage_figure_is_null_when_nothing_counted():
    """`null` when nothing is counted — not 0.0, which would read as "nothing covered"."""
    stats = coverage_stats({"catalog": {}, "inventory": {}, "known_test_links": {}}, [])
    assert stats["coverage_pct"] is None, stats
    print("✓ The coverage figure is null when nothing is counted")


if __name__ == "__main__":
    try:
        test_feature_linked_only_from_us_side_not_orphan()
        test_feature_with_own_forward_link_not_orphan()
        test_truly_unlinked_feature_still_flagged()
        test_partially_covered_ac_is_its_own_gap()
        test_ac_with_no_covered_value_is_untested()
        test_fully_covered_ac_is_no_gap()
        test_bare_tag_covers_every_declared_value()
        test_weighted_coverage_figure()
        test_coverage_figure_rounds_half_up()
        test_coverage_figure_is_null_when_nothing_counted()
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
