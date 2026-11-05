# MS1 report: the source-code chain, from `collector-gh` to the Markdown documents

## Purpose

The record of the first milestone: CI's testbed stage, and the operator's run of
[`tests/integration/local-integration.sh`](../../../tests/integration/local-integration.sh) over the testbed's `core`:
`living-doc-collector-gh`, then `living-doc-toolkit` and `living-doc-generator-markdown` in the inner and the release
view. How to run and fill it: [Integration runs](../README.md#run-a-milestone-target).

Every figure comes from the run's logs and its pin report. Only the testbed decides the milestone; an internal target
may be added under its label and never blocks it. The next milestone that runs the chain starts its report from this
one, in its own folder.

Each empty cell and each "…" is the operator's to fill.

## Contents

- [1. Header](#1-header)
- [2. Targets](#2-targets)
- [3. Component refs and `utilities` pins](#3-component-refs-and-utilities-pins)
- [4. Per artifact and per document](#4-per-artifact-and-per-document)
- [5. Warnings by code](#5-warnings-by-code)
- [6. Duplicates found](#6-duplicates-found)
- [7. Timings and sizes](#7-timings-and-sizes)
- [8. Defects](#8-defects)
- [9. "The output reads correctly"](#9-the-output-reads-correctly)

## 1. Header

- **Milestone:** MS1
- **Date:** …
- **Operator:** …
- **Machine type:** …
- **Verdict:** …
- **Owner sign-off:** …

### CI evidence

- **Run:** `real-collector.yml` ("Real collector stages") on `master` at … (…): <…>. Both jobs green:
  `real-collector-snapshot` and `testbed-collector-stage`.
- **Testbed read:** `AbsaOSS/living-doc-testbed` `master` at …, the commit the operator's run read (§ 2). If the
  testbed's `master` has moved since the CI run, dispatch the workflow by hand and replace this run and SHA.
- **What it asserted over `core`, the collector:** …
- **What it asserted over `core`, the toolkit:** …
- **What it asserted over `docs/examples`, the toolkit:** …

CI stops at the toolkit: only the operator's run renders the documents.

## 2. Targets

| Label | Kind | Decides the milestone | Target SHA (`target:` line) | Configuration |
|---|---|---|---|---|
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes |  | [`testbed-core/env.local`](testbed-core/env.local): `TARGET=testbed`, every component at its pin |

`--check`: …. The run's exit: ….

## 3. Component refs and `utilities` pins

From the runner's header in `testbed-core/local-integration.log` and each component log's header:

| Label | `living-doc:` | `collector-gh:` | `toolkit:` | `generator-markdown:` | `python:` |
|---|---|---|---|---|---|
| `testbed-core` |  |  |  |  |  |

| Label | `living-doc-utilities:` installed (collector / toolkit / generator) |
|---|---|
| `testbed-core` |  |

The pin report over the clones that ran, `testbed-core/pin-report.txt` (exit …):

```
…
```

## 4. Per artifact and per document

**The collector's and the toolkit's artifacts**, from each artifact's `stats.cardinality` block. `sources_configured` is
0 on a toolkit artifact, as it reads files, not sources; that is no failure.

| Label · view · artifact | `sources_configured` | `sources_failed` | `entities_skipped` | `entities` | `acceptance_criteria` | `scenarios` | `unresolved_refs` |
|---|---|---|---|---|---|---|---|
| `testbed-core` · `doc-source` |  |  |  |  |  |  |  |
| `testbed-core` · `ui-tests` |  |  |  |  |  |  |  |
| `testbed-core` · inner · `generator-ready` |  |  |  |  |  |  |  |
| `testbed-core` · inner · `ui-test-catalog` |  |  |  |  |  |  |  |
| `testbed-core` · inner · `coverage-matrix` |  |  |  |  |  |  |  |
| `testbed-core` · release · `generator-ready` |  |  |  |  |  |  |  |
| `testbed-core` · release · `ui-test-catalog` |  |  |  |  |  |  |  |
| `testbed-core` · release · `coverage-matrix` |  |  |  |  |  |  |  |

Every artifact's `contract:` line reads: ….

**The matrix's `summary`**, from each view's `summary:` block:

| Label · view | `counted_acs` | `covered_acs` | `partially_covered_acs` | `not_covered_acs` | `coverage_pct` |
|---|---|---|---|---|---|
| `testbed-core` · inner |  |  |  |  |  |
| `testbed-core` · release |  |  |  |  |  |

**Input warnings forwarded**, each `forwarded:` line of each view's toolkit log:

| Label · view | `generator-ready` from `doc-source` | `ui-test-catalog` from `ui-tests` | `coverage-matrix` from `doc-source` | `coverage-matrix` from `ui-tests` |
|---|---|---|---|---|
| `testbed-core` · inner |  |  |  |  |
| `testbed-core` · release |  |  |  |  |

**The documents**, from each view's generator log: per document, its `input:` and `view:` lines, the run report's
`counts:` block, and `not_loaded` from its `render_manifest:` block.

| Label · view · document | `input:` | `view:` | `entities` | `entities_by_type` | `acceptance_criteria` | `scenarios` | `warnings_by_code` | `not_loaded` |
|---|---|---|---|---|---|---|---|---|
| `testbed-core` · inner · `technical-project` |  |  |  |  |  |  |  |  |
| `testbed-core` · inner · `ui-test-catalog` |  |  |  |  |  |  |  |  |
| `testbed-core` · inner · `coverage-matrix` |  |  |  |  |  |  |  |  |
| `testbed-core` · release · `technical-project` |  |  |  |  |  |  |  |  |
| `testbed-core` · release · `ui-test-catalog` |  |  |  |  |  |  |  |  |
| `testbed-core` · release · `coverage-matrix` |  |  |  |  |  |  |  |  |

**Compared with the G2 baseline.** Method: [Compare two runs](../README.md#compare-two-runs), over
`../G2/testbed-core/` and `testbed-core/`: the collector's two artifacts, and the inner view's three toolkit outputs,
each through `tests/examples/normalize_snapshot.py`. Result for `testbed-core`: ….

## 5. Warnings by code

**`testbed-core`.** Any row is a defect. Each code with its count and first ten occurrences
(`path:line_no entity_id/ac_id message`), from the eight artifacts and the six documents:

| Code | Count | First ten occurrences |
|---|---|---|
|  |  |  |

`FIELD_LOSS` in any log: ….

## 6. Duplicates found

`DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` per target, by count, or "none": ….

## 7. Timings and sizes

| Label · view · artifact or document | `time:` | `size:` |
|---|---|---|
| `testbed-core` · `doc-source` |  |  |
| `testbed-core` · `ui-tests` |  |  |
| `testbed-core` · inner · `generator-ready` |  |  |
| `testbed-core` · inner · `ui-test-catalog` |  |  |
| `testbed-core` · inner · `coverage-matrix` |  |  |
| `testbed-core` · inner · `technical-project.md` |  |  |
| `testbed-core` · inner · `ui-test-catalog.md` |  |  |
| `testbed-core` · inner · `coverage-matrix.md` |  |  |
| `testbed-core` · release · `generator-ready` |  |  |
| `testbed-core` · release · `ui-test-catalog` |  |  |
| `testbed-core` · release · `coverage-matrix` |  |  |
| `testbed-core` · release · `technical-project.md` |  |  |
| `testbed-core` · release · `ui-test-catalog.md` |  |  |
| `testbed-core` · release · `coverage-matrix.md` |  |  |

## 8. Defects

One row per defect found during this run, each with an issue of its own in the repository at fault. The milestone
cannot pass while one from `testbed-core` is open; a parser defect is fixed by a `utilities` patch and a re-pin first.
A defect in a component's script on the operator's platform goes in that component's repository.

| # | Found on | Description | Issue link | State |
|---|---|---|---|---|
|  |  |  |  |  |

## 9. "The output reads correctly"

What is read is each of the six documents under `testbed-core/<view>/generator-markdown/`. Each verdict is the owner's:
yes or no.

| View | Document | Verdict | What was read (one sentence) |
|---|---|---|---|
| inner | `technical-project.md` |  |  |
| inner | `ui-test-catalog.md` |  |  |
| inner | `coverage-matrix.md` |  |  |
| release | `technical-project.md` |  |  |
| release | `ui-test-catalog.md` |  |  |
| release | `coverage-matrix.md` |  |  |
