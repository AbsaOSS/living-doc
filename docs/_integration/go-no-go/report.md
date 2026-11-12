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

- **Release:** `living-doc` `v0.1.0`, with `living-doc-collector-gh` `v0.2.0`, `living-doc-toolkit` `v0.1.0`,
  `living-doc-generator-markdown` `v0.1.0`, on `living-doc-utilities` `0.8.1`
- **Date:** 2026-11-12
- **Operator:** miroslavpojer; the chain was run for the operator by an agent session on the operator's machine
- **Machine type:** Windows 11 Pro, Git Bash (GNU bash 5.2.21), Python 3.14.6 (`PYTHON=python`), testbed only
- **Release pin pull requests merged:** `living-doc-collector-gh`
  [#161](https://github.com/AbsaOSS/living-doc-collector-gh/pull/161), merged as
  `b197a608d2dfc816a2934ae4fa6f2cdf3fb5b611`; `living-doc-toolkit`
  [#113](https://github.com/AbsaOSS/living-doc-toolkit/pull/113), merged as `fea9aa62d7805fbc675a5816f513a7d0259b7075`;
  `living-doc-generator-markdown` [#38](https://github.com/AbsaOSS/living-doc-generator-markdown/pull/38), merged as
  `005a058ae6b248a66c34e8bacdbe2217bb2a981d`. Each merge commit is the candidate the run used (§ 3).
- **Verdict:** go: the run exited 0 (run id `20261112T115140Z`)
- **The runner's last line:** `tests/integration/local-integration.sh: the chain and the testbed's invariants passed:
  the six documents are under <checkout>/docs/_integration/go-no-go/testbed-core/{inner,release}/generator-markdown`,
  with the machine's path to the `living-doc` checkout shown as `<checkout>`
- **Owner sign-off:** go, 2026-11-12
- **Tags cut, each at its commit in § 3, after go:** `living-doc-collector-gh` `v0.2.0` at
  `b197a608d2dfc816a2934ae4fa6f2cdf3fb5b611`, cut before the run, at the candidate the run used;
  `living-doc-toolkit` `v0.1.0` at `fea9aa62d7805fbc675a5816f513a7d0259b7075`; `living-doc-generator-markdown`
  `v0.1.0` at `005a058ae6b248a66c34e8bacdbe2217bb2a981d`
- **Testbed commit in the release notes:** `AbsaOSS/living-doc-testbed` `master` at
  `36a0ee65ad11df7588cd74a505ea1ace1ef7abc9`

### CI evidence

- **Each candidate's own CI**, green on its candidate commit (push, 2026-11-12), "Static analysis & tests":
  `living-doc-collector-gh` (<https://github.com/AbsaOSS/living-doc-collector-gh/actions/runs/43204268496>),
  `living-doc-toolkit` (<https://github.com/AbsaOSS/living-doc-toolkit/actions/runs/43210965747>) and
  `living-doc-generator-markdown` (<https://github.com/AbsaOSS/living-doc-generator-markdown/actions/runs/43210932117>).
  Each repository's "Link check" is green on the same commit.
- **`living-doc-collector-gh` `v0.2.0`:** its "Draft Release" run at `b197a60`
  (<https://github.com/AbsaOSS/living-doc-collector-gh/actions/runs/43204418736>).
- **`living-doc` at `2e6c9a2`, the runner's commit:** "Link check"
  (<https://github.com/AbsaOSS/living-doc/actions/runs/43089082829>) and "Retired names"
  (<https://github.com/AbsaOSS/living-doc/actions/runs/43089082550>), both green.
- **The testbed stage:** `real-collector.yml` runs the components at their pins in
  [`tests/collector/collector-pins.env`](../../../tests/collector/collector-pins.env), not at these candidates, so it is
  no evidence for this run. It runs them once the pins move to the tags.

## 2. Targets

| Label | Kind | Decides the release | Target SHA (`target:` line) | Configuration |
|---|---|---|---|---|
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes | `36a0ee65ad11df7588cd74a505ea1ace1ef7abc9` | [`testbed-core/env.local`](testbed-core/env.local): `TARGET=testbed`, the testbed and every component at a full commit SHA |

The runner's `target:` line: `testbed-core: AbsaOSS/living-doc-testbed <SHA> (<SHA>)`, the SHA above both times, the
second being the configured `TESTBED_REF`. It marks no uncommitted change.

`--check`: passed, exit 0 (run id `20261112T115117Z`). The run's exit: 0 (run id `20261112T115140Z`). No internal
target was run: only the testbed decides the release.

## 3. Component refs and `utilities` pins

From the runner's header in `testbed-core/local-integration.log` and each component log's header. Each component line
must show its configured ref, `(COLLECTOR_GH_REF=<full SHA>)` and so on, never `(pin)`, and no uncommitted change.

| Runner line | `testbed-core` |
|---|---|
| `living-doc:` | `2e6c9a2ef72788d25dacab7e2a7df318a820badf` |
| `collector-gh:` | `b197a608d2dfc816a2934ae4fa6f2cdf3fb5b611` `(COLLECTOR_GH_REF=b197a608d2dfc816a2934ae4fa6f2cdf3fb5b611)` |
| `toolkit:` | `fea9aa62d7805fbc675a5816f513a7d0259b7075` `(TOOLKIT_REF=fea9aa62d7805fbc675a5816f513a7d0259b7075)` |
| `generator-markdown:` | `005a058ae6b248a66c34e8bacdbe2217bb2a981d` `(GENERATOR_MARKDOWN_REF=005a058ae6b248a66c34e8bacdbe2217bb2a981d)` |
| `python:` | `3.14.6 (python)` |

No line is marked with uncommitted changes, and each component runs at its configured ref, none at its pin.

| Label | `living-doc-utilities:` installed (collector / toolkit / generator) |
|---|---|
| `testbed-core` | `0.8.1` / `0.8.1` / `0.8.1` (the toolkit's and the generator's in each view) |

The pin report over the clones that ran, `testbed-core/pin-report.txt` (exit 0):

```
living-doc-utilities pins
  component           pin    read from
  collector-gh        0.8.1  out/components/living-doc-collector-gh/requirements.txt
  toolkit             0.8.1  out/components/living-doc-toolkit/requirements.txt
  generator-markdown  0.8.1  out/components/living-doc-generator-markdown/requirements.txt
  examples-check      0.8.0  tests/examples/requirements-examples-check.txt
OK: every component pins living-doc-utilities 0.8.
```

The three components pin `0.8.1`. `examples-check` is this repository's corpus checker, not a part of the chain; it
pins `0.8.0`, and `--strict` compares the minor version, `0.8`.

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
`generator-ready`, `ui-test-catalog` and `coverage-matrix`. Every `producer:` line names `living-doc-utilities 0.8.1`:
`AbsaOSS/living-doc-collector-gh 0.2.0` on the collector's two artifacts, and `AbsaOSS/living-doc-toolkit 0.1.0` on the
six toolkit outputs, whose `source_inputs` name the collector at `0.2.0`.

**The release view's `ui-test-catalog` is the inner one, by the canon**, as in
[MS1 § 4](../MS1/report.md#4-per-artifact-and-per-document): the release `ui-test-catalog.md` and its run report are
byte-identical to the inner ones, and the release generator log says `view: inner` for that document. It is no defect.

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

**The checks**, from the runner's `== check:` blocks in `testbed-core/local-integration.log`: the collector's
invariants over `core`, the toolkit's over both views, and the six documents with their run reports. Each block's `OK`
lines:

- **The collector's invariants over `core`:** `doc-source` and `ui-tests` are valid (`doc-source-v1.0.0`,
  `ui-tests-v1.0.0`), each with `sources_failed 0` and no warning. 20 entities, one per file: 3 User Stories (the
  `.feature` files under `projects/core/tests/e2e/features/liv_doc_us`), 12 Functionalities (under
  `projects/core/tests/e2e/features/liv_doc_func`), 5 Features (full-header PageObjects under
  `projects/core/tests/e2e/pages`), every Feature state derived. 32 acceptance criteria, 6 with variants, 3 by
  `Aspect:` and 3 by keyword, each carrying its declared values as aspect. 2 cross-reference pages (PageObjects with
  `parent-feat:`), each a non-primary page on its Feature with its own functionalities and notes; every primary page is
  its Feature's full-header file. 28 scenarios in 16 `.feature` files under `projects/core/tests/e2e/features`, 2 of
  them in 1 file outside the living-doc folders, with no entity and no AC link. 27 AC links, all resolved: 6 aspect
  tags, 4 keyword tags, 1 bare tag on an AC with variants (`aspect: null`). `warnings: none`.
- **The toolkit's invariants over both views:** `generator-ready`, `coverage-matrix` and `ui-test-catalog` are valid in
  the inner and the release view, each with no warning. `coverage-matrix.inner` and `coverage-matrix.release`: 24
  counted criteria each, each verdict equal to what `doc-source` and `ui-tests` give: 20 covered, 2 partially covered, 2
  not covered. The inner view holds every record of `doc-source`; the release view drops 7, none left in `planned` or
  `in_review`. `warnings: none`.
- **The six documents and their run reports:** each view's `technical-project`, `ui-test-catalog` and
  `coverage-matrix`, each with its run report.

**Compared with the MS1 run.** Method: [Compare two runs](../README.md#compare-two-runs), over
`../MS1/testbed-core/` and `testbed-core/`: the collector's two artifacts, and both views' three toolkit outputs,
each through `tests/examples/normalize_snapshot.py`. Result for `testbed-core`: once normalized, each of the eight
differs from MS1's in its producer versions alone, nothing else:

- `living-doc-collector-gh` `version` `0.1.1` → `0.2.0` and `utilities_version` `0.8.0` → `0.8.1`, in the collector's
  two artifacts and in each toolkit output's `metadata.source_inputs[].producer`;
- `living-doc-toolkit` `utilities_version` `0.8.0` → `0.8.1` in the six toolkit outputs; its `version` stays `0.1.0`.

Before normalization each also differs in `metadata.generated_at`, and each file's size equals MS1's to the byte. The
six documents are byte-identical to MS1's, and the six run reports differ in their two `utilities_version` lines alone,
the generator's and its input producer's, `0.8.0` → `0.8.1`. What was mined and what was rendered are unchanged.

## 5. Warnings by code

**`testbed-core`.** Any row is a defect, and the run fails on it. Each code with its count and first ten occurrences
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
| `testbed-core` · `doc-source` | 1.53 s | 57664 bytes |
| `testbed-core` · `ui-tests` | 1.44 s | 26413 bytes |
| `testbed-core` · inner · `generator-ready` | 1.53 s | 74607 bytes |
| `testbed-core` · inner · `ui-test-catalog` | 1.46 s | 40628 bytes |
| `testbed-core` · inner · `coverage-matrix` | 1.59 s | 41264 bytes |
| `testbed-core` · inner · `technical-project.md` | 1.39 s | 19747 bytes, run report 4801 bytes |
| `testbed-core` · inner · `ui-test-catalog.md` | 1.27 s | 16980 bytes, run report 6343 bytes |
| `testbed-core` · inner · `coverage-matrix.md` | 1.28 s | 10212 bytes, run report 10241 bytes |
| `testbed-core` · release · `generator-ready` | 1.49 s | 64265 bytes |
| `testbed-core` · release · `ui-test-catalog` | 1.46 s | 40628 bytes |
| `testbed-core` · release · `coverage-matrix` | 1.50 s | 41266 bytes |
| `testbed-core` · release · `technical-project.md` | 1.39 s | 15459 bytes, run report 3815 bytes |
| `testbed-core` · release · `ui-test-catalog.md` | 1.28 s | 16980 bytes, run report 6343 bytes |
| `testbed-core` · release · `coverage-matrix.md` | 1.34 s | 10111 bytes, run report 10245 bytes |

The whole run took about 8.5 minutes on this machine, from 11:51:40 to 12:00:09 UTC. The fourteen timed steps add up
to 20 s; the rest is cloning and building each component's venv.

## 8. Defects

One row per defect found during this run, each with an issue of its own in the component at fault. A defect from
`testbed-core` is a no-go: its fix makes a new candidate, and a new run replaces this one. A parser defect is fixed by
a `utilities` patch and a new release pin first.

| # | Found on | Description | Issue link | State |
|---|---|---|---|---|
| none | none | none | none | none |

## 9. "The output reads correctly"

What is read is each of the six documents under `testbed-core/<view>/generator-markdown/`. Each verdict is the owner's:
yes or no.

| View | Document | Verdict | What was read (one sentence) |
|---|---|---|---|
| inner | `technical-project.md` | yes | The 20 entities and their 32 criteria in every state, from `active` to `planned`, each Feature with its derived state, its pages and its source permalink at `36a0ee6`. |
| inner | `ui-test-catalog.md` | yes | The 28 scenarios of 13 feature files, grouped by the Functionality or User Story they link or as unlinked, each with its `@AC:` tags, the criteria and aspects it covers, and its source permalink at `36a0ee6`. |
| inner | `coverage-matrix.md` | yes | The summary, 88.2 % over 24 counted criteria (20 covered, 2 partly, 2 not), the planned-work count of 5 criteria (2 in the backlog, 3 for `v1.2.0`), and the rows of the 15 entities with each criterion's state, status and scenarios. |
| release | `technical-project.md` | yes | The 16 entities and 24 criteria the release view keeps, with no `planned` or `in_review` criterion, `FEAT-004` left out, and each Functionality left out named on its Feature without a link, as `FUNC-003` and `FUNC-004` on `FEAT-002`. |
| release | `ui-test-catalog.md` | yes | The inner catalog byte for byte, headed `View: inner`, as the catalog has no view (§ 4). |
| release | `coverage-matrix.md` | yes | The same summary and the same 15 entities' rows as the inner view, headed `View: release`, without the planned-work section. |
