#!/usr/bin/env python3
"""
compute_gaps.py — Living Doc Gap Finder

Runs all 9 gap-detection algorithms over a catalog snapshot JSON and outputs a
structured gap report. The model uses the report to propose remediation actions
rather than computing the traversal itself — ensuring deterministic, token-efficient results.

Usage:
    python compute_gaps.py <catalog-snapshot.json>
    python compute_gaps.py <catalog-snapshot.json> --output report.json
    python compute_gaps.py <catalog-snapshot.json> --summary

Input format: see evals/files/catalog-snapshot.json for a worked example.
The catalog JSON must contain:
  catalog.user_stories  — list of User Story entities
  catalog.features      — list of Feature entities
  catalog.functionalities — list of Functionality entities
  inventory.ui_screens  — list of discovered UI screen paths (optional)
  inventory.api_endpoints — list of discovered API paths (optional)
  inventory.test_files  — list of {file, linked_ac} test entries (optional)
  inventory.bdd_scenarios — list of {scenario, linked_ac} entries (optional)
  known_test_links       — dict of AC_ID → test path | null
  deprecated_acs         — list of deprecated AC IDs (optional)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

# Gap type → (sort priority, severity label)
PRIORITIES = {
    "UNTESTED_AC": (1, "Blocker"),
    # An AC whose variants are only partly covered is a real gap but not a blocker: the
    # behaviour is tested, some declared values are not (DEC-74's `partially_covered`).
    "PARTIALLY_TESTED_AC": (1, "Important"),
    "UNDOCUMENTED_SURFACE": (2, "Important"),
    "FEATURE_WITHOUT_USER_STORY": (3, "Important"),
    "ORPHAN_USER_STORY": (4, "Important"),
    "ORPHAN_FUNCTIONALITY": (5, "Important"),
    "ORPHAN_TEST": (6, "Important"),
    "STALE_REFERENCE": (7, "Important"),
    "UNDOCUMENTED_FUNCTIONALITY": (8, "Nit"),
    "FEATURE_WITHOUT_FUNCTIONALITY": (9, "Nit"),
}


def load_snapshot(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_gaps(snapshot: dict) -> list[dict]:
    catalog = snapshot.get("catalog", {})
    inventory = snapshot.get("inventory", {})
    known_test_links: dict = snapshot.get("known_test_links", {})

    user_stories: list[dict] = catalog.get("user_stories", [])
    features: list[dict] = catalog.get("features", [])
    functionalities: list[dict] = catalog.get("functionalities", [])

    ui_screens: list[str] = inventory.get("ui_screens", [])
    api_endpoints: list[str] = inventory.get("api_endpoints", [])
    test_files: list[dict] = inventory.get("test_files", [])
    bdd_scenarios: list[dict] = inventory.get("bdd_scenarios", [])

    gaps: list[dict] = []
    gap_counter = 0

    def add_gap(gap_type: str, entity: str, description: str, proposed_action: str) -> None:
        nonlocal gap_counter
        gap_counter += 1
        priority_order, severity = PRIORITIES[gap_type]
        gaps.append(
            {
                "id": f"GAP-{gap_counter:03d}",
                "type": gap_type,
                "_priority": priority_order,
                "severity": severity,
                "entity": entity,
                "description": description,
                "proposed_action": proposed_action,
            }
        )

    # ── Build lookup indices ───────────────────────────────────────────────────
    feature_index = {f["id"]: f for f in features}
    us_ids = {us["id"] for us in user_stories}

    # Features referenced by at least one User Story back-link
    features_linked_from_us: set[str] = set()
    for feat in features:
        for us_id in feat.get("user_stories", []):
            if us_id in us_ids:
                features_linked_from_us.add(feat["id"])
    # Also honour forward links on the User Story entity itself
    for us in user_stories:
        for feat_id in us.get("features", []):
            if feat_id in feature_index:
                features_linked_from_us.add(feat_id)

    # Effective Functionality count per Feature (union of forward + back links)
    feature_func_counts: dict[str, int] = {f["id"]: 0 for f in features}
    for fn in functionalities:
        parent = fn.get("parent_feature")
        if parent and parent in feature_func_counts:
            feature_func_counts[parent] += 1
    for feat in features:
        declared = feat.get("functionalities", [])
        if declared:
            feature_func_counts[feat["id"]] = max(feature_func_counts[feat["id"]], len(declared))

    # Documented surface name tokens for Gap-2 matching (case-insensitive)
    documented_surface_tokens: set[str] = set()
    for feat in features:
        name = feat.get("name", "").lower()
        if name:
            documented_surface_tokens.add(name)
        for path in feat.get("paths", []):
            documented_surface_tokens.add(path.lower())

    # Deprecated ACs from explicit list + link metadata
    deprecated_ac_ids: set[str] = set(snapshot.get("deprecated_acs", []))
    for ac_id, link in known_test_links.items():
        if isinstance(link, dict) and link.get("ac_status", "").lower() == "deprecated":
            deprecated_ac_ids.add(ac_id)

    # ── Gap 1 — UNTESTED_AC / PARTIALLY_TESTED_AC ─────────────────────────────
    # Counted per declared variant value: an AC with values is a gap until every one of them
    # has a scenario. Only the missing values go in the proposed action — the covered ones
    # need no scenario (living-doc-header-types.md#ac-variants, DEC-74).
    declared = declared_values(catalog)
    covered_by_value = covered_values(known_test_links)
    for ac_id in {aid for aid, _ in (_split_link_key(k) for k in known_test_links)}:
        state, hit, total_values, missing = ac_coverage(ac_id, declared, covered_by_value)
        if state == "covered":
            continue
        figure = f" ({hit}/{total_values})" if ac_id in declared else ""
        if state == "partially_covered":
            add_gap(
                "PARTIALLY_TESTED_AC",
                ac_id,
                f"AC '{ac_id}' has no scenario for every declared value{figure}: "
                f"{', '.join(missing)}",
                "Generate one scenario per missing value with "
                "living-doc-scenario-creator, each tagged "
                f"@{ac_id}/<name>:<value> with the AC's own variant name",
            )
        else:
            add_gap(
                "UNTESTED_AC",
                ac_id,
                f"AC '{ac_id}' has no linked test{figure}"
                + (f": {', '.join(missing)}" if missing else ""),
                "Generate a BDD scenario using living-doc-scenario-creator, "
                "or add a unit/integration test and link it to this AC",
            )

    # ── Gap 2 — UNDOCUMENTED_SURFACE ──────────────────────────────────────────
    for surface in ui_screens + api_endpoints:
        surface_lower = surface.lower().lstrip("/")
        matched = any(
            surface_lower in token or token in surface_lower
            for token in documented_surface_tokens
        )
        if not matched:
            add_gap(
                "UNDOCUMENTED_SURFACE",
                surface,
                f"Surface '{surface}' exists in the application with no Feature entity",
                "Create a Feature entity using living-doc-create-feature",
            )

    # ── Gap 3 — FEATURE_WITHOUT_USER_STORY ────────────────────────────────────────────────
    # Honour both the Feature's own forward `user_stories` link and the back-link
    # from a User Story's `features` list (features_linked_from_us, built above) —
    # otherwise a Feature linked only from the User Story side is falsely flagged,
    # inconsistent with Gap 4 below which already honours both directions.
    for feat in features:
        if not feat.get("user_stories") and feat["id"] not in features_linked_from_us:
            add_gap(
                "FEATURE_WITHOUT_USER_STORY",
                feat["id"],
                f"Feature '{feat['id']}' ({feat.get('name', '')}) has no linked User Stories",
                "Link to an existing User Story or confirm with the product owner whether to deprecate",
            )

    # ── Gap 4 — ORPHAN_USER_STORY ─────────────────────────────────────────────
    us_linked_to_any_feature: set[str] = set()
    for feat in features:
        for us_id in feat.get("user_stories", []):
            us_linked_to_any_feature.add(us_id)
    for us in user_stories:
        has_forward_link = bool(us.get("features"))
        has_back_link = us["id"] in us_linked_to_any_feature
        if not has_forward_link and not has_back_link:
            add_gap(
                "ORPHAN_USER_STORY",
                us["id"],
                f"User Story '{us['id']}' ({us.get('title', us.get('name', ''))}) has no linked Feature",
                "Link to an existing Feature or create the missing Feature using living-doc-create-feature",
            )

    # ── Gap 5 — ORPHAN_FUNCTIONALITY ──────────────────────────────────────────
    for fn in functionalities:
        if not fn.get("parent_feature"):
            add_gap(
                "ORPHAN_FUNCTIONALITY",
                fn["id"],
                f"Functionality '{fn['id']}' has no parent Feature",
                "Link to an existing Feature; if no owning surface exists, deprecate this Functionality",
            )

    # ── Gap 6 — ORPHAN_TEST ───────────────────────────────────────────────────
    all_tests = test_files + bdd_scenarios
    for test in all_tests:
        label = test.get("file") or test.get("scenario", "unknown")
        if not test.get("linked_ac"):
            add_gap(
                "ORPHAN_TEST",
                label,
                f"Test '{label}' has no linked AC",
                "Link to an existing AC, or create a Functionality for the behavior using "
                "living-doc-create-functionality. Never delete the test to resolve the gap.",
            )

    # ── Gap 7 — STALE_REFERENCE ───────────────────────────────────────────────
    for test in all_tests:
        label = test.get("file") or test.get("scenario", "unknown")
        linked_ac = test.get("linked_ac")
        if linked_ac and linked_ac in deprecated_ac_ids:
            add_gap(
                "STALE_REFERENCE",
                label,
                f"Test '{label}' references deprecated AC '{linked_ac}'",
                "Update the test to reference the active replacement AC via gherkin-living-doc-sync; "
                "if the behavior was intentionally removed, delete the test after product owner confirmation",
            )

    # ── Gap 8 — UNDOCUMENTED_FUNCTIONALITY ────────────────────────────────────
    for fn in functionalities:
        if not fn.get("linked_tests"):
            ac_count = fn.get("ac_count", 0)
            add_gap(
                "UNDOCUMENTED_FUNCTIONALITY",
                fn["id"],
                f"Functionality '{fn['id']}' has {ac_count} AC(s) with no linked tests",
                "Create unit or integration tests for this Functionality's ACs and link them",
            )

    # ── Gap 9 — FEATURE_WITHOUT_FUNCTIONALITY ─────────────────────────────────────────────────
    for feat in features:
        if feature_func_counts.get(feat["id"], 0) == 0 and not feat.get("functionalities"):
            add_gap(
                "FEATURE_WITHOUT_FUNCTIONALITY",
                feat["id"],
                f"Feature '{feat['id']}' ({feat.get('name', '')}) has no Functionalities defined",
                "Create Functionalities for known behaviors using living-doc-create-functionality",
            )

    # Sort: priority ascending, then entity ID ascending
    gaps.sort(key=lambda g: (g["_priority"], g["entity"]))
    for g in gaps:
        del g["_priority"]

    return gaps



# ── AC variants: coverage per declared value ─────────────────────────────────────────
# An AC that declares variants is `covered` only when every declared value has a scenario,
# `not_covered` when none has, `partially_covered` otherwise — the coverage matrix's three
# states (living-doc-header-types.md#ac-variants). A link may name the value it covers, in
# the tag's own form (`AC:US-001-01/channel:email`); a bare AC id covers the whole AC, every
# declared value at once.


def declared_values(catalog: dict) -> dict[str, list[str]]:
    """Each AC's declared variant values, by AC id, from the catalog's entities."""
    declared: dict[str, list[str]] = {}
    for group in ("user_stories", "functionalities"):
        for entity in catalog.get(group, []) or []:
            for ac in entity.get("acceptance_criteria", []) or []:
                if not isinstance(ac, dict):
                    continue
                ac_id = ac.get("id")
                values = [str(v) for v in (ac.get("aspect") or [])]
                if ac_id and values:
                    declared[ac_id] = values
    return declared


def _split_link_key(key: str) -> tuple[str, str | None]:
    """An AC link key as `(ac_id, value_or_None)` — `AC:US-1-01/channel:email` names a value."""
    if "/" in key:
        ac_id, _, segment = key.partition("/")
        return ac_id, segment.split(":", 1)[1] if ":" in segment else None
    return key, None


def covered_values(known_test_links: dict) -> dict[str, dict]:
    """Per AC: the declared values its links cover, and whether any link is for the whole AC."""
    covered: dict[str, dict] = {}
    for key, link in known_test_links.items():
        ac_id, value = _split_link_key(key)
        entry = covered.setdefault(ac_id, {"linked": False, "values": set(), "whole": False})
        if link is None:
            continue
        entry["linked"] = True
        if value is None:
            entry["whole"] = True
        else:
            entry["values"].add(value)
    return covered


def ac_coverage(ac_id: str, declared: dict[str, list[str]], covered: dict[str, dict]):
    """``(state, covered_count, declared_count, missing_values)`` for one AC."""
    values = declared.get(ac_id, [])
    entry = covered.get(ac_id) or {"linked": False, "values": set(), "whole": False}
    if not values:
        return ("covered" if entry["linked"] else "not_covered"), int(entry["linked"]), 1, []
    if entry["whole"]:
        return "covered", len(values), len(values), []
    missing = [v for v in values if v not in entry["values"]]
    hit = len(values) - len(missing)
    if hit == 0:
        return "not_covered", 0, len(values), missing
    if missing:
        return "partially_covered", hit, len(values), missing
    return "covered", hit, len(values), []


def coverage_stats(snapshot: dict, gaps: list[dict]) -> dict:
    """The three state counts and one weighted figure, by `DEC-74`'s formula.

    A `covered` AC counts 1, `not_covered` 0, and `partially_covered` its covered values over
    its declared values. The figure is computed from exact fractions and rounded once, to one
    decimal, half up — not by rounding each AC first, and never as the mean of the entities.
    `None` when nothing is counted.
    """
    known_test_links: dict = snapshot.get("known_test_links", {})
    declared = declared_values(snapshot.get("catalog", {}))
    covered_by_value = covered_values(known_test_links)
    ac_ids = sorted({aid for aid, _ in (_split_link_key(k) for k in known_test_links)})

    counts = {"covered": 0, "partially_covered": 0, "not_covered": 0}
    weight = Fraction(0)
    for ac_id in ac_ids:
        state, hit, total_values, _ = ac_coverage(ac_id, declared, covered_by_value)
        counts[state] += 1
        weight += Fraction(hit, total_values) if total_values else Fraction(0)

    counted = len(ac_ids)
    pct = None
    if counted:
        exact = weight / counted * 100
        # Decimal with ROUND_HALF_UP: Python's round() is banker's rounding, which would
        # turn 16.25 into 16.2 where the decision says 16.3.
        pct = float(
            (Decimal(exact.numerator) / Decimal(exact.denominator)).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
        )
    return {
        "total_acs": counted,
        "counted_acs": counted,
        "covered_acs": counts["covered"],
        "partially_covered_acs": counts["partially_covered"],
        "not_covered_acs": counts["not_covered"],
        "coverage_percentage": pct,
        "coverage_pct": pct,
    }


def build_report(snapshot: dict, gaps: list[dict]) -> dict:
    stats = coverage_stats(snapshot, gaps)
    severity_counts = {"Blocker": 0, "Important": 0, "Nit": 0}
    for g in gaps:
        severity_counts[g["severity"]] += 1
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "documentation_coverage": stats,
        "summary": {
            "total_gaps": len(gaps),
            "blockers": severity_counts["Blocker"],
            "important": severity_counts["Important"],
            "nits": severity_counts["Nit"],
        },
        "gaps": gaps,
    }


def print_summary(report: dict) -> None:
    cov = report["documentation_coverage"]
    summ = report["summary"]
    print(f"\n=== Living Doc Gap Report — {report['generated_at']} ===")
    print(
        f"Coverage: {cov['covered_acs']}/{cov['total_acs']} ACs covered "
        f"({cov['coverage_percentage']}%)"
    )
    print(
        f"Gaps: {summ['total_gaps']} total  |  "
        f"{summ['blockers']} Blocker  |  "
        f"{summ['important']} Important  |  "
        f"{summ['nits']} Nit\n"
    )
    for gap in report["gaps"]:
        print(f"  [{gap['severity']:9s}]  {gap['id']}  {gap['type']}")
        print(f"               Entity:  {gap['entity']}")
        print(f"               Action:  {gap['proposed_action']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute living doc gaps from a catalog snapshot."
    )
    parser.add_argument("snapshot", help="Path to catalog-snapshot.json")
    parser.add_argument(
        "--output", "-o", help="Write JSON gap report to this file (default: stdout)"
    )
    parser.add_argument(
        "--summary", "-s", action="store_true", help="Print human-readable summary"
    )
    args = parser.parse_args()

    snapshot = load_snapshot(args.snapshot)
    gaps = compute_gaps(snapshot)
    report = build_report(snapshot, gaps)

    if args.summary:
        print_summary(report)
    elif args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Gap report written to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
