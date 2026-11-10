# Release go/no-go report: the source-code chain at its release candidates

## Purpose

The record of the release go/no-go: one run of
[`tests/integration/local-integration.sh`](../../../tests/integration/local-integration.sh) over the testbed's `core`,
with every component at the commit its release will tag: `living-doc-collector-gh`, then `living-doc-toolkit` and
`living-doc-generator-markdown` in the inner and the release view. When to run it and what follows: [Integration runs
§ Release go/no-go](../README.md#release-gono-go). How to fill it: [Run a milestone target](../README.md#run-a-milestone-target).

Every figure comes from the run's logs and its pin report. Only the testbed decides; the run's exit is the verdict.
This report is started from the first milestone's, [`MS1/report.md`](../MS1/report.md). The release run fills it
and files it by a pull request of its own.

The verdict in § 1 is the run's exit; the sign-off and the verdicts in § 9 are the owner's.

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

- **Release:** …
- **Date:** …
- **Operator:** …
- **Machine type:** …
- **Release pin pull requests merged:** `living-doc-collector-gh` …, `living-doc-toolkit` …,
  `living-doc-generator-markdown` …
- **Verdict:** pending
- **The runner's last line:** …
- **Owner sign-off:** pending
- **Tags cut, each at its commit in § 3, after go:** …
- **Testbed commit in the release notes:** …

## 2. Targets

| Label | Kind | Decides the release | Target SHA (`target:` line) | Configuration |
|---|---|---|---|---|
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes |  | [`testbed-core/env.local`](testbed-core/env.local): `TARGET=testbed`, the testbed and every component at a full commit SHA |

`--check`: …. The run's exit: ….

## 3. Component refs and `utilities` pins

From the runner's header in `testbed-core/local-integration.log` and each component log's header. Each component line
must show its configured ref, `(COLLECTOR_GH_REF=<full SHA>)` and so on, never `(pin)`, and no uncommitted change.

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

**The checks**, from the runner's `== check:` blocks in `testbed-core/local-integration.log`: the collector's
invariants over `core`, the toolkit's over both views, and the six documents with their run reports. Each block's
`OK` lines: ….

**Compared with the MS1 run.** Method: [Compare two runs](../README.md#compare-two-runs), over
`../MS1/testbed-core/` and `testbed-core/`: the collector's two artifacts, and both views' three toolkit outputs,
each through `tests/examples/normalize_snapshot.py`. Result for `testbed-core`: ….

## 5. Warnings by code

**`testbed-core`.** Any row is a defect, and the run fails on it. Each code with its count and first ten occurrences
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

One row per defect found during this run, each with an issue of its own in the component at fault. A defect from
`testbed-core` is a no-go: its fix makes a new candidate, and a new run replaces this one. A parser defect is fixed by
a `utilities` patch and a new release pin first.

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
