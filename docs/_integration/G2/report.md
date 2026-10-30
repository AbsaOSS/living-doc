# G2 report: `utilities` + `collector-gh` + `toolkit` integrated

## Purpose

The record of the toolkit gate: CI's testbed stage, and the operator's two `local-integration.sh` runs over the
testbed's `core` and over internal repositories. How to run and fill it: [Integration runs](../README.md). Internal
targets appear under a label, with counts and codes only ([What may be committed](../README.md#what-may-be-committed)).

Every figure comes from that target's two logs. Only the testbed decides the gate. An internal target never blocks it,
and its warnings are classified, not counted against it. The rows of a label that was not run are deleted.

## Contents

- [1. Header](#1-header)
- [2. Targets](#2-targets)
- [3. Component refs and `utilities` pins](#3-component-refs-and-utilities-pins)
- [4. Per artifact](#4-per-artifact)
- [5. Warnings by code](#5-warnings-by-code)
- [6. Duplicates found](#6-duplicates-found)
- [7. Timings and artifact sizes](#7-timings-and-artifact-sizes)
- [8. Defects](#8-defects)
- [9. "The output reads correctly"](#9-the-output-reads-correctly)

## 1. Header

- **Gate:** G2
- **Date:** {…}
- **Operator:** {…}
- **Machine type:** {…}
- **Verdict:** {…}
- **Owner sign-off:** {…}

### CI evidence

- **Run:** `real-collector.yml` ("Real collector stages") on `master` at `b49b19f` (push, 2026-10-30 13:25 UTC):
  <https://github.com/AbsaOSS/living-doc/actions/runs/41063139724>. Both jobs green: `real-collector-snapshot` and
  `testbed-collector-stage`.
- **Testbed read:** `AbsaOSS/living-doc-testbed` `master` at `36a0ee65ad11df7588cd74a505ea1ace1ef7abc9`, which was
  still `master` on 2026-10-30. The workflow has no schedule: if the testbed's `master` has moved by the operator run,
  dispatch the workflow by hand and replace this run and SHA.
- **What it asserted over `core`, the collector:** both artifacts are valid and `sources_failed` is 0, with no warning.
  20 entities (3 User Stories, 12 Functionalities, 5 Features), every Feature state derived. 32 ACs, 6 with variants
  (3 by `Aspect:`, 3 by keyword). 2 cross-reference pages, each non-primary on its Feature. 28 scenarios, 2 of them
  outside the living-doc folders with no entity and no AC link. 27 AC links, all resolved (6 aspect tags, 4 keyword
  tags, 1 bare tag with `aspect: null`). The derived case `misindented_ac_line` gave exactly one `MISINDENTED_LINE`, at
  line 17 of `func-001-filter-search-results.feature`.
- **What it asserted over `core`, the toolkit:** `generator-ready` in the inner and the release view, `coverage-matrix`
  and `ui-test-catalog` are valid, with no warning. 24 counted criteria, each verdict equal to what `doc-source` and
  `ui-tests` give: 20 covered, 2 partially covered, 2 not covered. The inner view holds every record of `doc-source`;
  the release view drops 7, none left in `planned` or `in_review`.
- **What it asserted over `docs/examples`, the toolkit:** the corpus's two warnings, `FEATURE_WITHOUT_FUNCTIONALITY` and
  `UNRESOLVED_RELATION`, are forwarded in both views of `generator-ready` and in `coverage-matrix`, each on its entity
  and naming its documentation input.

## 2. Targets

| Label | Kind | Decides the gate | Target SHA (`target:` line) | Paths configured |
|---|---|---|---|---|
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes | {…} | [`testbed-core/env.local`](testbed-core/env.local), as in CI; [`testbed-core/toolkit.env.local`](testbed-core/toolkit.env.local) |
| `absa-1` | internal | no | {…} | in `internal/absa-1/` only |
| `absa-2` | internal | no | {…} | in `internal/absa-2/` only |
| `absa-3` | internal | no | {…} | in `internal/absa-3/` only |

Authoring deviations noted while finding an internal target's paths (README, step 1), by label: {…}

## 3. Component refs and `utilities` pins

One row per target run, from the two logs' header blocks:

| Label | `collector:` | `toolkit:` | `living-doc-utilities:` (installed, collector / toolkit) | `requirements.txt` pin (collector / toolkit) | `python:` (collector / toolkit) |
|---|---|---|---|---|---|
| `testbed-core` | {…} | {…} | {…} | {…} | {…} |
| `absa-1` | {…} | {…} | {…} | {…} | {…} |
| `absa-2` | {…} | {…} | {…} | {…} | {…} |
| `absa-3` | {…} | {…} | {…} | {…} | {…} |

`python tests/examples/check_utilities_pins.py --strict` output (in `living-doc` at `b49b19f`, 2026-10-30; exit 0):

```
living-doc-utilities pins
  component       pin    read from
  collector-gh    0.8.0  AbsaOSS/living-doc-collector-gh@93faed7fb3af requirements.txt
  toolkit         0.8.0  AbsaOSS/living-doc-toolkit@ed03f179ce6f requirements.txt
  examples-check  0.8.0  tests/examples/requirements-examples-check.txt
OK: every component pins living-doc-utilities 0.8.
```

## 4. Per artifact

From each artifact's `stats.cardinality` block. `sources_configured` is 0 on a toolkit artifact, as it reads files, not
sources; that is no failure.

| Label · artifact | `sources_configured` | `sources_failed` | `entities_skipped` | `entities` | `acceptance_criteria` | `scenarios` | `unresolved_refs` |
|---|---|---|---|---|---|---|---|
| `testbed-core` · `doc-source` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `testbed-core` · `ui-tests` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `testbed-core` · `generator-ready` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `testbed-core` · `ui-test-catalog` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `testbed-core` · `coverage-matrix` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-1` · `doc-source` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-1` · `ui-tests` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-1` · `generator-ready` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-1` · `ui-test-catalog` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-1` · `coverage-matrix` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-2` · `doc-source` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-2` · `ui-tests` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-2` · `generator-ready` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-2` · `ui-test-catalog` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-2` · `coverage-matrix` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-3` · `doc-source` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-3` · `ui-tests` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-3` · `generator-ready` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-3` · `ui-test-catalog` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |
| `absa-3` · `coverage-matrix` | {…} | {…} | {…} | {…} | {…} | {…} | {…} |

**The matrix's `summary`**, from its `summary:` block:

| Label | `counted_acs` | `covered_acs` | `partially_covered_acs` | `not_covered_acs` | `coverage_pct` |
|---|---|---|---|---|---|
| `testbed-core` | {…} | {…} | {…} | {…} | {…} |
| `absa-1` | {…} | {…} | {…} | {…} | {…} |
| `absa-2` | {…} | {…} | {…} | {…} | {…} |
| `absa-3` | {…} | {…} | {…} | {…} | {…} |

**Input warnings forwarded**, each `forwarded:` line of the toolkit's log. `core` has no warning, so `0 of 0` on
`testbed-core` means there was nothing to forward; it cannot show forwarding. The corpus job in CI (see
[CI evidence](#ci-evidence)) and an internal target that has warnings do.

| Label | `generator-ready` from `doc-source` | `ui-test-catalog` from `ui-tests` | `coverage-matrix` from `doc-source` | `coverage-matrix` from `ui-tests` |
|---|---|---|---|---|
| `testbed-core` | {…} | {…} | {…} | {…} |
| `absa-1` | {…} | {…} | {…} | {…} |
| `absa-2` | {…} | {…} | {…} | {…} |
| `absa-3` | {…} | {…} | {…} | {…} |

**Compared with the G1 baseline.** Method: [Compare two runs](../README.md#compare-two-runs), over
`../G1/testbed-core/collector-gh/` and `testbed-core/collector-gh/`, each artifact through
`tests/examples/normalize_snapshot.py`. Result for `testbed-core`: {…}

## 5. Warnings by code

**`testbed-core`.** Any row is a defect. Each code with its count and first ten occurrences
(`path:line_no entity_id/ac_id message`), from all five artifacts:

| Code | Count | First ten occurrences |
|---|---|---|
| {…} | {…} | {…} |

**Internal targets.** Code and count only; the occurrences stay in the target's log. Classification: *authoring* (the
file deviates from the canon) or *pipeline* (a defect, listed in § 8).

| Label · artifact | Code | Count | Classification |
|---|---|---|---|
| {…} | {…} | {…} | {…} |

## 6. Duplicates found

`DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` per target, by count, or "none": {…}

## 7. Timings and artifact sizes

| Label · artifact | `time:` | `size:` |
|---|---|---|
| `testbed-core` · `doc-source` | {…} | {…} |
| `testbed-core` · `ui-tests` | {…} | {…} |
| `testbed-core` · `generator-ready` | {…} | {…} |
| `testbed-core` · `ui-test-catalog` | {…} | {…} |
| `testbed-core` · `coverage-matrix` | {…} | {…} |
| `absa-1` · `doc-source` | {…} | {…} |
| `absa-1` · `ui-tests` | {…} | {…} |
| `absa-1` · `generator-ready` | {…} | {…} |
| `absa-1` · `ui-test-catalog` | {…} | {…} |
| `absa-1` · `coverage-matrix` | {…} | {…} |
| `absa-2` · `doc-source` | {…} | {…} |
| `absa-2` · `ui-tests` | {…} | {…} |
| `absa-2` · `generator-ready` | {…} | {…} |
| `absa-2` · `ui-test-catalog` | {…} | {…} |
| `absa-2` · `coverage-matrix` | {…} | {…} |
| `absa-3` · `doc-source` | {…} | {…} |
| `absa-3` · `ui-tests` | {…} | {…} |
| `absa-3` · `generator-ready` | {…} | {…} |
| `absa-3` · `ui-test-catalog` | {…} | {…} |
| `absa-3` · `coverage-matrix` | {…} | {…} |

## 8. Defects

One row per defect found during these runs. The gate cannot pass while one from `testbed-core` is open; a parser
defect is fixed by a `utilities` patch and a re-pin first. A defect found on an internal target is filed with a
canonical example that names nothing internal. A defect in the toolkit's script on the operator's platform goes in
`living-doc-toolkit`.

| # | Found on | Description | Issue link | State |
|---|---|---|---|---|
| {…} | {…} | {…} | {…} | {…} |

## 9. "The output reads correctly"

What is read is the inner `testbed-core/toolkit/normalize-docs/generator-ready.json`. The verdict and the sentence are
the owner's.

- **Verdict:** {…}
- **What was read (one sentence):** {…}
