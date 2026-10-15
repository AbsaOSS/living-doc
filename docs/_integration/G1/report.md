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
- **Date:** {date of the operator runs}
- **Operator:** {name}
- **Machine type:** {public testbed only | internal machine, internal targets included}
- **Verdict:** {passed | not passed}
- **Owner sign-off:** {owner, date}

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
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes | {expected `36a0ee6` unless the testbed moved} | [`testbed-core/env.local`](testbed-core/env.local), as in CI |
| `absa-1` | internal | no | {…} | in `internal/absa-1/env.local` only |
| `absa-2` | internal | no | {…} | in `internal/absa-2/env.local` only |
| `absa-3` | internal | no | {…} | in `internal/absa-3/env.local` only |

Authoring deviations noted while finding an internal target's paths (README, step 1), by label: {none so far}.

## 3. Component refs and `utilities` pins

One row per target run, from the log's header block:

| Label | `collector:` | `living-doc-utilities:` (installed) | `requirements.txt` pin | `python:` |
|---|---|---|---|---|
| `testbed-core` | {expected `1e968ce…`} | {…} | `living-doc-utilities==0.6.0` | {…} |
| `absa-1` | {…} | {…} | `living-doc-utilities==0.6.0` | {…} |
| `absa-2` | {…} | {…} | `living-doc-utilities==0.6.0` | {…} |
| `absa-3` | {…} | {…} | `living-doc-utilities==0.6.0` | {…} |

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
| `testbed-core` · `doc-source` | {…} | {…} | {…} | {expected 20} | {expected 32} | — | {…} |
| `testbed-core` · `ui-tests` | {…} | {…} | {…} | — | — | {expected 28} | {…} |
| `absa-1` · `doc-source` | {…} | {…} | {…} | {…} | {…} | — | {…} |
| `absa-1` · `ui-tests` | {…} | {…} | {…} | — | — | {…} | {…} |
| `absa-2` · `doc-source` | {…} | {…} | {…} | {…} | {…} | — | {…} |
| `absa-2` · `ui-tests` | {…} | {…} | {…} | — | — | {…} | {…} |
| `absa-3` · `doc-source` | {…} | {…} | {…} | {…} | {…} | — | {…} |
| `absa-3` · `ui-tests` | {…} | {…} | {…} | — | — | {…} | {…} |

## 5. Warnings by code

**`testbed-core`.** Any row is a defect. Each code with its count and first ten occurrences
(`path:line_no entity_id/ac_id message`):

| Code | Count | First ten occurrences |
|---|---|---|
| {none expected} | | |

**Internal targets.** Code and count only; the occurrences stay in the target's log. Classification: *authoring* (the
file deviates from the canon) or *pipeline* (a defect, listed in § 8).

| Label · artifact | Code | Count | Classification |
|---|---|---|---|
| {…} | | | |

## 6. Duplicates found

`DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` per target, by count, or "none": {…}

## 7. Timings and artifact sizes

| Label · artifact | `time:` | `size:` |
|---|---|---|
| `testbed-core` · `doc-source` | {…} | {…} |
| `testbed-core` · `ui-tests` | {…} | {…} |
| `absa-1` · `doc-source` | {…} | {…} |
| `absa-1` · `ui-tests` | {…} | {…} |
| `absa-2` · `doc-source` | {…} | {…} |
| `absa-2` · `ui-tests` | {…} | {…} |
| `absa-3` · `doc-source` | {…} | {…} |
| `absa-3` · `ui-tests` | {…} | {…} |

## 8. Defects

One row per defect found during these runs. The gate cannot pass while one from `testbed-core` is open; a parser
defect is fixed by a `utilities` patch and a re-pin first. A defect found on an internal target is filed with a
canonical example that names nothing internal.

| # | Found on | Description | Issue link | State |
|---|---|---|---|---|
| {none so far} | | | | |

## 9. "The output reads correctly"

- **Verdict:** {yes | no}
- **What was read (one sentence):** {…}
