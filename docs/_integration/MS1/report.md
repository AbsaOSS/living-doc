# MS1 report: the source-code chain, from `collector-gh` to the Markdown documents

## Purpose

The record of the first milestone: CI's testbed stage, and the operator's run of
[`tests/integration/local-integration.sh`](../../../tests/integration/local-integration.sh) over the testbed's `core`:
`living-doc-collector-gh`, then `living-doc-toolkit` and `living-doc-generator-markdown` in the inner and the release
view. How to run and fill it: [Integration runs](../README.md#run-a-milestone-target).

Every figure comes from the run's logs and its pin report. Only the testbed decides the milestone; an internal target
may be added under its label and never blocks it. The next milestone that runs the chain starts its report from this
one, in its own folder.

The verdict and the sign-off in § 1 and the verdicts in § 9 are the owner's.

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
- **Date:** 2026-11-05
- **Operator:** miroslavpojer; the chain was run for the operator by an agent session on the operator's machine
- **Machine type:** Windows 11 Pro, Git Bash (GNU bash 5.2.21), Python 3.14.6 (`PYTHON=python`), testbed only
- **Verdict:** passed
- **Owner sign-off:** passed, 2026-11-05

### CI evidence

- **Run:** `real-collector.yml` ("Real collector stages") on `master` at `82c5fc1` (push, 2026-11-05 11:37 UTC):
  <https://github.com/AbsaOSS/living-doc/actions/runs/42020534539>. Both jobs green:
  `real-collector-snapshot` and `testbed-collector-stage`.
- **The other gates on that commit:** `examples-check.yml`
  (<https://github.com/AbsaOSS/living-doc/actions/runs/42020535053>) and `retired-names.yml`
  (<https://github.com/AbsaOSS/living-doc/actions/runs/42020534804>), both green on `82c5fc1`.
- **Testbed read:** `AbsaOSS/living-doc-testbed` `master` at `36a0ee65ad11df7588cd74a505ea1ace1ef7abc9`, the commit the
  operator's run read (§ 2). If the testbed's `master` has moved since the CI run, dispatch the workflow by hand and
  replace this run and SHA.
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
- **What it asserted over `docs/examples`, the toolkit:** both views of `generator-ready`, `coverage-matrix` and
  `ui-test-catalog` are valid, with 6 counted criteria per aspect. The corpus's two warnings,
  `FEATURE_WITHOUT_FUNCTIONALITY` and `UNRESOLVED_RELATION`, are forwarded in both views of `generator-ready` and in
  `coverage-matrix`, and two documentation files fail with `MULTIPLE_DOCUMENTATION_SOURCES`.

CI stops at the toolkit: only the operator's run renders the documents.

## 2. Targets

| Label | Kind | Decides the milestone | Target SHA (`target:` line) | Configuration |
|---|---|---|---|---|
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes | `testbed-core: AbsaOSS/living-doc-testbed 36a0ee65ad11df7588cd74a505ea1ace1ef7abc9 (master)` | [`testbed-core/env.local`](testbed-core/env.local): `TARGET=testbed`, every component at its pin |

`--check`: passed, exit 0 (run id `20261105T121708Z`). The run's exit: 0 (run id `20261105T121744Z`). No internal
target was run for this milestone.

## 3. Component refs and `utilities` pins

From the runner's header in `testbed-core/local-integration.log` and each component log's header:

| Label | `living-doc:` | `collector-gh:` | `toolkit:` | `generator-markdown:` | `python:` |
|---|---|---|---|---|---|
| `testbed-core` | `82c5fc14d276e080c8625b3b780ebb26ffd4aba4` | `93faed7fb3afcc6514a494114ee25a1fff0fe3ea (pin)` | `ed03f179ce6f894f51e48695827331c48a585c21 (pin)` | `e6b1c2d6525fe5fb9ee8418f29672c902831134c (pin)` | `3.14.6 (python)` |

`living-doc` shows no uncommitted change, and each component runs at its pin in
[`tests/collector/collector-pins.env`](../../../tests/collector/collector-pins.env).

| Label | `living-doc-utilities:` installed (collector / toolkit / generator) |
|---|---|
| `testbed-core` | `0.8.0` / `0.8.0` / `0.8.0` (the toolkit's and the generator's in each view) |

The pin report over the clones that ran, `testbed-core/pin-report.txt` (exit 0):

```
living-doc-utilities pins
  component           pin    read from
  collector-gh        0.8.0  out/components/living-doc-collector-gh/requirements.txt
  toolkit             0.8.0  out/components/living-doc-toolkit/requirements.txt
  generator-markdown  0.8.0  out/components/living-doc-generator-markdown/requirements.txt
  examples-check      0.8.0  tests/examples/requirements-examples-check.txt
OK: every component pins living-doc-utilities 0.8.
```

## 4. Per artifact and per document

**The collector's and the toolkit's artifacts**, from each artifact's `stats.cardinality` block. `sources_configured` is
0 on a toolkit artifact, as it reads files, not sources; that is no failure.

| Label · view · artifact | `sources_configured` | `sources_failed` | `entities_skipped` | `entities` | `acceptance_criteria` | `scenarios` | `unresolved_refs` |
|---|---|---|---|---|---|---|---|
| `testbed-core` · `doc-source` | 1 | 0 | 0 | 20 | 32 | 0 | 0 |
| `testbed-core` · `ui-tests` | 1 | 0 | 0 | 0 | 0 | 28 | 0 |
| `testbed-core` · inner · `generator-ready` | 0 | 0 | 0 | 20 | 32 | 0 | 0 |
| `testbed-core` · inner · `ui-test-catalog` | 0 | 0 | 0 | 0 | 0 | 28 | 0 |
| `testbed-core` · inner · `coverage-matrix` | 0 | 0 | 0 | 15 | 24 | 0 | 0 |
| `testbed-core` · release · `generator-ready` | 0 | 0 | 0 | 16 | 24 | 0 | 0 |
| `testbed-core` · release · `ui-test-catalog` | 0 | 0 | 0 | 0 | 0 | 28 | 0 |
| `testbed-core` · release · `coverage-matrix` | 0 | 0 | 0 | 15 | 24 | 0 | 0 |

`entities_by_type`: `doc-source` and the inner `generator-ready` `DocumentedFeature=5, DocumentedFunctionality=12,
DocumentedUserStory=3`; the release `generator-ready` `DocumentedFeature=4, DocumentedFunctionality=9,
DocumentedUserStory=3`; each view's `coverage-matrix` `DocumentedFunctionality=12, DocumentedUserStory=3`.

Every artifact's `contract:` line reads: `<contract>-v1.0.0, valid (read_artifact)`, for `doc-source`, `ui-tests`,
`generator-ready`, `ui-test-catalog` and `coverage-matrix`.

**The release view's `ui-test-catalog` is the inner one, by the canon.** `normalize-tests` takes no view and writes
`document.view: inner`, as the catalog has no view-dependent field (`living-doc-utilities`
`docs/contracts/rendering.md`, § Fields by view). So `release/toolkit/normalize-tests/ui-test-catalog.json` differs
from the inner one in `metadata.generated_at` alone, the release `ui-test-catalog.md` and its run report are
byte-identical to the inner ones, and the release generator log says `view: inner` for that document. It is no
defect.

**The matrix's `summary`**, from each view's `summary:` block:

| Label · view | `counted_acs` | `covered_acs` | `partially_covered_acs` | `not_covered_acs` | `coverage_pct` |
|---|---|---|---|---|---|
| `testbed-core` · inner | 24 | 20 | 2 | 2 | 88.2 |
| `testbed-core` · release | 24 | 20 | 2 | 2 | 88.2 |

**Input warnings forwarded**, each `forwarded:` line of each view's toolkit log:

| Label · view | `generator-ready` from `doc-source` | `ui-test-catalog` from `ui-tests` | `coverage-matrix` from `doc-source` | `coverage-matrix` from `ui-tests` |
|---|---|---|---|---|
| `testbed-core` · inner | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from ui-tests-v1.0.0` | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from ui-tests-v1.0.0` |
| `testbed-core` · release | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from ui-tests-v1.0.0` | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from ui-tests-v1.0.0` |

**The documents**, from each view's generator log: per document, its `input:` and `view:` lines, the run report's
`counts:` block, and `not_loaded` from its `render_manifest:` block.

| Label · view · document | `input:` | `view:` | `entities` | `entities_by_type` | `acceptance_criteria` | `scenarios` | `warnings_by_code` | `not_loaded` |
|---|---|---|---|---|---|---|---|---|
| `testbed-core` · inner · `technical-project` | `generator-ready-v1.0.0, valid (read_artifact)` | `inner` | 20 | `DocumentedFeature=5, DocumentedFunctionality=12, DocumentedUserStory=3` | 32 | 0 | `-` | 0 |
| `testbed-core` · inner · `ui-test-catalog` | `ui-test-catalog-v1.0.0, valid (read_artifact)` | `inner` | 0 | `-` | 0 | 28 | `-` | 0 |
| `testbed-core` · inner · `coverage-matrix` | `coverage-matrix-v1.0.0, valid (read_artifact)` | `inner` | 15 | `DocumentedFunctionality=12, DocumentedUserStory=3` | 24 | 0 | `-` | 0 |
| `testbed-core` · release · `technical-project` | `generator-ready-v1.0.0, valid (read_artifact)` | `release` | 16 | `DocumentedFeature=4, DocumentedFunctionality=9, DocumentedUserStory=3` | 24 | 0 | `-` | 0 |
| `testbed-core` · release · `ui-test-catalog` | `ui-test-catalog-v1.0.0, valid (read_artifact)` | `inner` | 0 | `-` | 0 | 28 | `-` | 0 |
| `testbed-core` · release · `coverage-matrix` | `coverage-matrix-v1.0.0, valid (read_artifact)` | `release` | 15 | `DocumentedFunctionality=12, DocumentedUserStory=3` | 24 | 0 | `-` | 0 |

Every document's log block ends `warnings: 0`.

**Compared with the G2 baseline.** Method: [Compare two runs](../README.md#compare-two-runs), over
`../G2/testbed-core/` and `testbed-core/`: the collector's two artifacts, and the inner view's three toolkit outputs,
each through `tests/examples/normalize_snapshot.py`. Result for `testbed-core`: all five are equal once normalized, no
line different. Before normalization each differs from the baseline's in `metadata.generated_at` alone:
`producer.version` and `producer.utilities_version` are unchanged too (`collector-gh` `0.1.1`, `toolkit` `0.1.0`,
`living-doc-utilities` `0.8.0`), as both runs used the same pins, and each file's size equals the baseline's to the
byte.

## 5. Warnings by code

**`testbed-core`.** Any row is a defect. Each code with its count and first ten occurrences
(`path:line_no entity_id/ac_id message`), from the eight artifacts and the six documents:

| Code | Count | First ten occurrences |
|---|---|---|
| none | 0 | none |

Each of the eight artifacts' and the six documents' blocks reads `warnings: 0`, with `warnings_by_code: -`.

`FIELD_LOSS` in any log: none.

## 6. Duplicates found

`DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` per target, by count, or "none": none.

## 7. Timings and sizes

| Label · view · artifact or document | `time:` | `size:` |
|---|---|---|
| `testbed-core` · `doc-source` | 1.95 s | 57664 bytes |
| `testbed-core` · `ui-tests` | 1.61 s | 26413 bytes |
| `testbed-core` · inner · `generator-ready` | 1.62 s | 74607 bytes |
| `testbed-core` · inner · `ui-test-catalog` | 1.62 s | 40628 bytes |
| `testbed-core` · inner · `coverage-matrix` | 1.59 s | 41264 bytes |
| `testbed-core` · inner · `technical-project.md` | 1.75 s | 19747 bytes, run report 4801 bytes |
| `testbed-core` · inner · `ui-test-catalog.md` | 1.48 s | 16980 bytes, run report 6343 bytes |
| `testbed-core` · inner · `coverage-matrix.md` | 1.83 s | 10212 bytes, run report 10241 bytes |
| `testbed-core` · release · `generator-ready` | 1.67 s | 64265 bytes |
| `testbed-core` · release · `ui-test-catalog` | 1.71 s | 40628 bytes |
| `testbed-core` · release · `coverage-matrix` | 1.62 s | 41266 bytes |
| `testbed-core` · release · `technical-project.md` | 1.81 s | 15459 bytes, run report 3815 bytes |
| `testbed-core` · release · `ui-test-catalog.md` | 1.35 s | 16980 bytes, run report 6343 bytes |
| `testbed-core` · release · `coverage-matrix.md` | 1.72 s | 10111 bytes, run report 10245 bytes |

The whole run took about 9.5 minutes on this machine, nearly all of it `pip` building each component's venv.

## 8. Defects

One row per defect found during this run, each with an issue of its own in the repository at fault. The milestone
cannot pass while one from `testbed-core` is open; a parser defect is fixed by a `utilities` patch and a re-pin first.
A defect in a component's script on the operator's platform goes in that component's repository.

| # | Found on | Description | Issue link | State |
|---|---|---|---|---|
| none | none | none | none | none |

## 9. "The output reads correctly"

What is read is each of the six documents under `testbed-core/<view>/generator-markdown/`. Each verdict is the owner's:
yes or no.

| View | Document | Verdict | What was read (one sentence) |
|---|---|---|---|
| inner | `technical-project.md` | yes | The 20 entities and their 32 criteria in every state, from `active` to backlog `planned`, each Feature with its derived state, its pages and its source permalink at `36a0ee6`. |
| inner | `ui-test-catalog.md` | yes | The 28 scenarios of 13 feature files, grouped by the Functionality or User Story they link or as unlinked, each with its `@AC:` tags, the criteria and aspects it covers, and its source permalink. |
| inner | `coverage-matrix.md` | yes | The summary, 88.2 % over 24 counted criteria (20 covered, 2 partly, 2 not), the planned-work count of 5 criteria, and the rows of the 15 entities with each criterion's status and scenarios. |
| release | `technical-project.md` | yes | The 16 entities and 24 criteria the release view keeps, with no `planned` or `in_review` criterion, `FEAT-004` left out, and each Functionality left out named on its Feature without a link. |
| release | `ui-test-catalog.md` | yes | The inner catalog byte for byte, headed `View: inner`, as the catalog has no view (§ 4). |
| release | `coverage-matrix.md` | yes | The same summary and the same 15 entities' rows as the inner view, headed `View: release`, without the planned-work section. |
