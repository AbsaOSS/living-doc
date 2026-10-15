# G1 report: `utilities` + `collector-gh` integrated

## Purpose

The record of gate G1: CI's testbed stage, and the operator's `local-integration.sh` runs over the testbed's `core`
and over internal repositories. How to run and fill it: [Integration runs](../README.md). Internal targets appear under
a label, with counts and codes only ([What may be committed](../README.md#what-may-be-committed)).

Every `{…}` is filled from that target's `local-integration.log`. Only the testbed decides the gate. An internal
target never blocks it, and its warnings are classified, not counted against it.

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

- **Gate:** G1
- **Date:** 2026-10-15
- **Operator:** local operator (name not recorded)
- **Machine type:** internal machine, internal targets included
- **Verdict:** passed
- **Owner sign-off:** pending

### CI evidence

- **Run:** `real-collector.yml` ("Real collector stages") on `master` at `2934a41` (push, 2026-10-15 08:00 UTC):
  <https://github.com/AbsaOSS/living-doc/actions/runs/38702609304>. Both jobs green: `real-collector-snapshot` and
  `testbed-collector-stage`.
- **Testbed read:** `AbsaOSS/living-doc-testbed` `master` at `36a0ee65ad11df7588cd74a505ea1ace1ef7abc9`, which was
  still `master` on 2026-10-15. The workflow has no schedule: if the testbed's `master` has moved by the operator run,
  dispatch the workflow by hand and replace this run and SHA.
- **What it asserted over `core`:** both artifacts are valid and `sources_failed` is 0, with no warning. 20 entities
  (3 User Stories, 12 Functionalities, 5 Features), every Feature state derived. 32 ACs, 6 with variants (3 by
  `Aspect:`, 3 by keyword). 2 cross-reference pages, each non-primary on its Feature. 28 scenarios, 2 of them in `smoke/`
  with no entity and no AC link. 27 AC links, all resolved (6 aspect tags, 4 keyword tags, 1 bare tag with
  `aspect: null`). The derived case `misindented_ac_line` gave exactly one `MISINDENTED_LINE`, at line 17 of
  `func-001-filter-search-results.feature`.

## 2. Targets

| Label | Kind | Decides the gate | Target SHA (`target:` line) | Paths configured |
|---|---|---|---|---|
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes | `36a0ee65ad11df7588cd74a505ea1ace1ef7abc9` | [`testbed-core/env.local`](testbed-core/env.local), as in CI |
| `absa-1` | internal | no | `9f9064ad178fd5e9ad72b1126ae4f8633aa732b2` | in `internal/absa-1/env.local` only |
| `absa-2` | internal | no | `002abdf18e42ddf383d926fa3d02e3a5e757da49` | in `internal/absa-2/env.local` only |
| `absa-3` | internal | no | `6958900ba52cd8bae4d0741c427ab39775dcbffe` | in `internal/absa-3/env.local` only |

Authoring deviations noted while finding an internal target's paths (README, step 1), by label: `absa-2` has no
User Story source; its documented empty-source path was configured.

## 3. Component refs and `utilities` pins

One row per target run, from the log's header block:

| Label | `collector:` | `living-doc-utilities:` (installed) | `requirements.txt` pin | `python:` |
|---|---|---|---|---|
| `testbed-core` | `1e968ce551e03d0554d31461e993f9250b6eebfb` | `0.6.0` | `living-doc-utilities==0.6.0` | `3.13.2` |
| `absa-1` | `1e968ce551e03d0554d31461e993f9250b6eebfb` | `0.6.0` | `living-doc-utilities==0.6.0` | `3.13.2` |
| `absa-2` | `1e968ce551e03d0554d31461e993f9250b6eebfb` | `0.6.0` | `living-doc-utilities==0.6.0` | `3.13.2` |
| `absa-3` | `1e968ce551e03d0554d31461e993f9250b6eebfb` | `0.6.0` | `living-doc-utilities==0.6.0` | `3.13.2` |

`python tests/examples/check_utilities_pins.py --strict` output (in `living-doc` at `2934a41`, 2026-10-15; exit 0):

```
living-doc-utilities pins
  component       pin    read from
  collector-gh    0.6.0  AbsaOSS/living-doc-collector-gh@1e968ce551e0 requirements.txt
  examples-check  0.6.0  tests/examples/requirements-examples-check.txt
OK: every component pins living-doc-utilities 0.6.
```

## 4. Per artifact

From each artifact's `stats.cardinality` block:

| Label · artifact | `sources_configured` | `sources_failed` | `entities_skipped` | `entities` | `acceptance_criteria` | `scenarios` | `unresolved_refs` |
|---|---|---|---|---|---|---|---|
| `testbed-core` · `doc-source` | 1 | 0 | 0 | 20 | 32 | — | 0 |
| `testbed-core` · `ui-tests` | 1 | 0 | 0 | — | — | 28 | 0 |
| `absa-1` · `doc-source` | 1 | 0 | 2 | 77 | 183 | — | 1 |
| `absa-1` · `ui-tests` | 1 | 0 | 0 | — | — | 52 | 0 |
| `absa-2` · `doc-source` | 1 | 0 | 0 | 0 | 0 | — | 0 |
| `absa-2` · `ui-tests` | 1 | 0 | 0 | — | — | 3 | 0 |
| `absa-3` · `doc-source` | 1 | 0 | 3 | 31 | 48 | — | 0 |
| `absa-3` · `ui-tests` | 1 | 0 | 0 | — | — | 26 | 0 |

## 5. Warnings by code

**`testbed-core`.** Any row is a defect. Each code with its count and first ten occurrences
(`path:line_no entity_id/ac_id message`):

| Code | Count | First ten occurrences |
|---|---|---|
| none | 0 | — |

**Internal targets.** Code and count only; the occurrences stay in the target's log. Classification: *authoring* (the
file deviates from the canon) or *pipeline* (a defect, listed in § 8).

| Label · artifact | Code | Count | Classification |
|---|---|---|---|
| `absa-1` · `doc-source` | `AUTHORING_ERROR` | 8 | authoring |
| `absa-1` · `doc-source` | `FEATURE_WITHOUT_FUNCTIONALITY` | 1 | authoring |
| `absa-1` · `doc-source` | `IGNORED_AUTHORED_KEY` | 35 | authoring |
| `absa-1` · `doc-source` | `RELATION_MISMATCH` | 3 | authoring |
| `absa-1` · `doc-source` | `UNRESOLVED_RELATION` | 1 | authoring |
| `absa-2` · `doc-source` | `EMPTY_SOURCE` | 1 | authoring |
| `absa-3` · `doc-source` | `AUTHORING_ERROR` | 3 | authoring |
| `absa-3` · `doc-source` | `FEATURE_WITHOUT_FUNCTIONALITY` | 4 | authoring |
| `absa-3` · `doc-source` | `IGNORED_AUTHORED_KEY` | 34 | authoring |
| `absa-3` · `doc-source` | `RELATION_MISMATCH` | 5 | authoring |
| `absa-3` · `doc-source` | `STATUS_AC_MISMATCH` | 1 | authoring |
| `absa-3` · `doc-source` | `UNPARSED_AC_LINE` | 1 | authoring |

## 6. Duplicates found

`DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` per target, by count, or "none": none.

## 7. Timings and artifact sizes

| Label · artifact | `time:` | `size:` |
|---|---|---|
| `testbed-core` · `doc-source` | 0.62 s | 57664 bytes |
| `testbed-core` · `ui-tests` | 0.77 s | 26413 bytes |
| `absa-1` · `doc-source` | 0.74 s | 234063 bytes |
| `absa-1` · `ui-tests` | 0.90 s | 50393 bytes |
| `absa-2` · `doc-source` | 0.66 s | 9147 bytes |
| `absa-2` · `ui-tests` | 0.72 s | 3648 bytes |
| `absa-3` · `doc-source` | 0.89 s | 97673 bytes |
| `absa-3` · `ui-tests` | 0.83 s | 24485 bytes |

## 8. Defects

One row per defect found during these runs. The gate cannot pass while one from `testbed-core` is open; a parser
defect is fixed by a `utilities` patch and a re-pin first. A defect found on an internal target is filed with a
canonical example that names nothing internal.

| # | Found on | Description | Issue link | State |
|---|---|---|---|---|
| none | — | — | — | — |

## 9. "The output reads correctly"

- **Verdict:** yes
- **What was read (one sentence):** All eight artifacts passed contract validation; testbed cardinalities match the expected G1 corpus, and internal summaries contain only the permitted labels, SHAs, counts and warning codes.
