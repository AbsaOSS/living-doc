# G2 report: `utilities` + `collector-gh` + `toolkit` integrated

## Purpose

The record of the toolkit gate: CI's testbed stage, and the operator's two `local-integration.sh` runs over the
testbed's `core`. How to run and fill it: [Integration runs](../README.md).

Every figure comes from the target's two logs. Only the testbed decides the gate. No internal target was run for this
gate.

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
- **Date:** 2026-10-30
- **Operator:** miroslavpojer
- **Machine type:** macOS, testbed only
- **Verdict:** passed
- **Owner sign-off:** passed, 2026-10-30

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
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes | `36a0ee65ad11df7588cd74a505ea1ace1ef7abc9` | [`testbed-core/env.local`](testbed-core/env.local), as in CI; [`testbed-core/toolkit.env.local`](testbed-core/toolkit.env.local) |

Both `--check` passed and both runs exited 0.

## 3. Component refs and `utilities` pins

From the two logs' header blocks:

| Label | `collector:` | `toolkit:` | `living-doc-utilities:` (installed, collector / toolkit) | `requirements.txt` pin (collector / toolkit) | `python:` (collector / toolkit) |
|---|---|---|---|---|---|
| `testbed-core` | `93faed7fb3afcc6514a494114ee25a1fff0fe3ea` | `ed03f179ce6f894f51e48695827331c48a585c21` | `0.8.0` / `0.8.0` | `living-doc-utilities==0.8.0` / `living-doc-utilities==0.8.0` | `3.14.7` / `3.14.7` |

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
| `testbed-core` · `doc-source` | 1 | 0 | 0 | 20 | 32 | 0 | 0 |
| `testbed-core` · `ui-tests` | 1 | 0 | 0 | 0 | 0 | 28 | 0 |
| `testbed-core` · `generator-ready` | 0 | 0 | 0 | 20 | 32 | 0 | 0 |
| `testbed-core` · `ui-test-catalog` | 0 | 0 | 0 | 0 | 0 | 28 | 0 |
| `testbed-core` · `coverage-matrix` | 0 | 0 | 0 | 15 | 24 | 0 | 0 |

Every artifact's `contract:` line reads `valid (read_artifact)`.

**The matrix's `summary`**, from its `summary:` block:

| Label | `counted_acs` | `covered_acs` | `partially_covered_acs` | `not_covered_acs` | `coverage_pct` |
|---|---|---|---|---|---|
| `testbed-core` | 24 | 20 | 2 | 2 | 88.2 |

**Input warnings forwarded**, each `forwarded:` line of the toolkit's log. `core` has no warning, so `0 of 0` on
`testbed-core` means there was nothing to forward; it cannot show forwarding. The corpus job in CI does (see
[CI evidence](#ci-evidence)).

| Label | `generator-ready` from `doc-source` | `ui-test-catalog` from `ui-tests` | `coverage-matrix` from `doc-source` | `coverage-matrix` from `ui-tests` |
|---|---|---|---|---|
| `testbed-core` | 0 of 0 | 0 of 0 | 0 of 0 | 0 of 0 |

**Compared with the G1 baseline.** Method: [Compare two runs](../README.md#compare-two-runs), over
`../G1/testbed-core/collector-gh/` and `testbed-core/collector-gh/`, each artifact through
`tests/examples/normalize_snapshot.py`. Result for `testbed-core`: each artifact differs in one line,
`utilities_version` `0.6.0` → `0.8.0`, the version the collector now pins. What was mined is unchanged.

`tests/testbed/check_testbed_stage.py core` passes over the committed collector artifacts (exit 0).

## 5. Warnings by code

**`testbed-core`.** Any row is a defect. Each code with its count and first ten occurrences
(`path:line_no entity_id/ac_id message`), from all five artifacts:

| Code | Count | First ten occurrences |
|---|---|---|
| none | 0 | — |

No `FIELD_LOSS` in either log.

## 6. Duplicates found

`DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` per target, by count, or "none": none.

## 7. Timings and artifact sizes

| Label · artifact | `time:` | `size:` |
|---|---|---|
| `testbed-core` · `doc-source` | 0.64 s | 57664 bytes |
| `testbed-core` · `ui-tests` | 0.76 s | 26413 bytes |
| `testbed-core` · `generator-ready` | 0.67 s | 74607 bytes |
| `testbed-core` · `ui-test-catalog` | 0.69 s | 40628 bytes |
| `testbed-core` · `coverage-matrix` | 0.65 s | 41264 bytes |

## 8. Defects

One row per defect found during these runs. The gate cannot pass while one from `testbed-core` is open; a parser
defect is fixed by a `utilities` patch and a re-pin first. A defect in the toolkit's script on the operator's platform
goes in `living-doc-toolkit`.

| # | Found on | Description | Issue link | State |
|---|---|---|---|---|
| none | — | — | — | — |

## 9. "The output reads correctly"

What is read is the inner `testbed-core/toolkit/normalize-docs/generator-ready.json`. The verdict and the sentence are
the owner's.

- **Verdict:** yes
- **What was read (one sentence):** The inner `generator-ready.json`, read against its input `doc-source.json` record by record: all 20 entities and 32 criteria are there, each of the 489 populated values is unchanged, nothing is lost or added, and the matrix's 24 counted criteria are those 32 less the 5 planned and 3 in review.
