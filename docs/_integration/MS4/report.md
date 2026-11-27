# MS4 report: the source-code chain at its `v0.2.0` tags

## Purpose

The record of `v0.2.0`'s release milestone: CI's testbed stage, and the operator's run of
[`tests/integration/local-integration.sh`](../../../tests/integration/local-integration.sh) over the testbed's `core`
with every component at the tag `living-doc` `v0.2.0` lists: `living-doc-collector-gh`, then `living-doc-toolkit` and
`living-doc-generator-markdown` in the inner and the release view. How to run and fill it: [Integration
runs](../README.md#run-a-milestone-target).

Every figure comes from the run's logs and its pin report. Only the testbed decides the milestone; an internal target
may be added under its label and never blocks it. This report is started from `v0.1.0`'s release milestone,
[`MS3/report.md`](../MS3/report.md), and compares its run with the release go/no-go's,
[`go-no-go/report.md`](../go-no-go/report.md), which ran the same component commits before the tags were cut.

The verdict in § 1 is the run's exit and § 8; the sign-off and the verdicts in § 9 are the owner's.

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

- **Milestone:** MS4, the release milestone: `living-doc` `v0.2.0`, with `living-doc-collector-gh` `v0.3.0`,
  `living-doc-toolkit` `v0.2.0` and `living-doc-generator-markdown` `v0.2.0`, on `living-doc-utilities` `0.9.0`
- **Date:** 2026-11-27
- **Operator:** miroslavpojer; the chain was run for the operator by an agent session on the operator's machine
- **Machine type:** Windows 11 Pro, Git Bash (GNU bash 5.2.21), Python 3.14.6 (`PYTHON=python`), testbed only
- **The tags run, each checked against its commit with `git ls-remote --tags`:** `living-doc-collector-gh` `v0.3.0` at
  `3219c9350e96d463a456e4384b4a58a117926233`, `living-doc-toolkit` `v0.2.0` at
  `85e94232ba3294a1c8f86644ebe56d65b9d94a20`, `living-doc-generator-markdown` `v0.2.0` at
  `d0e8b49cdaf9b6892327f8849742736408baeda3`, each the commit the go/no-go ran
  ([go-no-go § 3](../go-no-go/report.md#3-component-refs-and-utilities-pins)); `living-doc-utilities` `v0.9.0` at
  `7a6fb9f36dd24f8593224c14bef1058dd09c7ea6`; `living-doc` `v0.2.0` at `0884bfb443ced6cd7845bc5672cbed8273470c8b`, the
  commit the run used (§ 3)
- **Verdict:** passed: the run exited 0 (run id `20261127T112505Z`), and § 8 lists no defect
- **The runner's last line:** `tests/integration/local-integration.sh: the chain and the testbed's invariants passed:
  the six documents are under <checkout>/docs/_integration/MS4/testbed-core/{inner,release}/generator-markdown`, with
  the machine's path to the `living-doc` checkout shown as `<checkout>`
- **Owner sign-off:** passed, 2026-11-27

### CI evidence

Since `living-doc` `0884bfb`, [`tests/collector/collector-pins.env`](../../../tests/collector/collector-pins.env) pins
the three tags, so CI's testbed stage runs the same `collector-gh` and `toolkit` commits as this run.

- **Run:** `real-collector.yml` ("Real collector stages") on `master` at `0884bfb` (push, 2026-11-27 10:27 UTC):
  <https://github.com/AbsaOSS/living-doc/actions/runs/45982228563>. Both jobs green: "Snapshot the real collector over
  docs/examples" and "Collector stage over the testbed's core".
- **The other gates on that commit:** `examples-check.yml`
  (<https://github.com/AbsaOSS/living-doc/actions/runs/45982228557>) and `retired-names.yml`
  (<https://github.com/AbsaOSS/living-doc/actions/runs/45982229140>), both green. `link-check.yml`
  (<https://github.com/AbsaOSS/living-doc/actions/runs/45982228509>) failed on one `503 Service Unavailable` from
  github.com alone, a testbed permalink in `MS1/`'s technical project, of 2334 links; no link is broken.
- **Testbed read:** `AbsaOSS/living-doc-testbed` `master` at `6b9b3ec9262032518023a3cd6e9f86acf97d1f89`, the commit the
  go/no-go and the operator's run read (§ 2). The testbed's `master` has since moved to `09d6bf8`
  (AbsaOSS/living-doc-testbed#13: its workflow and `docs/living-doc-generation.md`, no file under `projects/core/`);
  this run pins `6b9b3ec`, so its permalinks equal the go/no-go's.
- **What it asserted over `core`, the collector:** 20 entities, one per file (3 User Stories, 12 Functionalities, 5
  Features), every Feature state derived, and 33 acceptance criteria. The derived case `misindented_ac_line` gave
  exactly one `MISINDENTED_LINE`, at line 17 of `func-001-filter-search-results.feature`.
- **What it asserted over `core`, the toolkit:** `coverage-matrix` has 25 counted criteria, each verdict equal to what
  `doc-source` and `ui-tests` give: 21 covered, 2 partially covered, 2 not covered, with the 3 expected warnings.
- **What it asserted over `docs/examples`:** `doc-source` mined 5 entities and 8 acceptance criteria. Both views of
  `generator-ready`, `coverage-matrix` and the catalog are valid, with 6 counted criteria per aspect. The corpus's two
  warnings, `FEATURE_WITHOUT_FUNCTIONALITY` and `UNRESOLVED_RELATION`, are forwarded in each, and two documentation
  files fail with `MULTIPLE_DOCUMENTATION_SOURCES`. The pin report shows the three components, at their tags, and
  `examples-check` on `0.9.0`.

CI stops at the toolkit: only the operator's run renders the documents.

## 2. Targets

| Label | Kind | Decides the milestone | Target SHA (`target:` line) | Configuration |
|---|---|---|---|---|
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes | `6b9b3ec9262032518023a3cd6e9f86acf97d1f89` | [`testbed-core/env.local`](testbed-core/env.local): `TARGET=testbed`, the testbed at the go/no-go's commit, every component at its tag, `RELEASE_VERSION=0.1.0` |

The runner's `target:` line: `testbed-core: AbsaOSS/living-doc-testbed <SHA> (<SHA>)`, the SHA above both times, the
second being the configured `TESTBED_REF`. It marks no uncommitted change. `release version: 0.1.0` is the release of
the testbed's content the run reads, as in the go/no-go; it is not `living-doc`'s version.

`--check`: passed, exit 0 (run id `20261127T112450Z`). The run's exit: 0 (run id `20261127T112505Z`). No internal
target was run for this milestone.

## 3. Component refs and `utilities` pins

From the runner's header in `testbed-core/local-integration.log` and each component log's header. Each component line
shows its configured tag, `(COLLECTOR_GH_REF=v0.3.0)` and so on, never `(pin)`, and the commit the tag points at.

| Runner line | `testbed-core` |
|---|---|
| `living-doc:` | `0884bfb443ced6cd7845bc5672cbed8273470c8b` |
| `collector-gh:` | `3219c9350e96d463a456e4384b4a58a117926233` `(COLLECTOR_GH_REF=v0.3.0)` |
| `toolkit:` | `85e94232ba3294a1c8f86644ebe56d65b9d94a20` `(TOOLKIT_REF=v0.2.0)` |
| `generator-markdown:` | `d0e8b49cdaf9b6892327f8849742736408baeda3` `(GENERATOR_MARKDOWN_REF=v0.2.0)` |
| `python:` | `3.14.6 (python)` |

No line is marked with uncommitted changes. Each component runs at its configured tag, which is also its pin in
[`tests/collector/collector-pins.env`](../../../tests/collector/collector-pins.env) at `0884bfb`, and each tag's commit
is the one the go/no-go ran by SHA.

| Label | `living-doc-utilities:` installed (collector / toolkit / generator) |
|---|---|
| `testbed-core` | `0.9.0` / `0.9.0` / `0.9.0` (the toolkit's and the generator's in each view) |

The pin report over the clones that ran, `testbed-core/pin-report.txt` (exit 0):

```
living-doc-utilities pins
  component           pin    read from
  collector-gh        0.9.0  out/components/living-doc-collector-gh/requirements.txt
  toolkit             0.9.0  out/components/living-doc-toolkit/requirements.txt
  generator-markdown  0.9.0  out/components/living-doc-generator-markdown/requirements.txt
  examples-check      0.9.0  tests/examples/requirements-examples-check.txt
OK: every component pins living-doc-utilities 0.9.
```

The three components and `examples-check`, this repository's corpus checker, all pin `0.9.0`. No pin is a release
candidate.

## 4. Per artifact and per document

**The collector's and the toolkit's artifacts**, from each artifact's `stats.cardinality` block. `sources_configured` is
0 on a toolkit artifact, as it reads files, not sources; that is no failure.

| Label · view · artifact | `sources_configured` | `sources_failed` | `entities_skipped` | `entities` | `acceptance_criteria` | `scenarios` | `unresolved_refs` |
|---|---|---|---|---|---|---|---|
| `testbed-core` · `doc-source` | 1 | 0 | 0 | 20 | 33 | 0 | 0 |
| `testbed-core` · `ui-tests` | 1 | 0 | 0 | 0 | 0 | 37 | 0 |
| `testbed-core` · inner · `generator-ready` | 0 | 0 | 0 | 20 | 33 | 0 | 0 |
| `testbed-core` · inner · `ui-test-catalog` | 0 | 0 | 0 | 0 | 0 | 37 | 0 |
| `testbed-core` · inner · `coverage-matrix` | 0 | 0 | 0 | 15 | 25 | 0 | 0 |
| `testbed-core` · release · `generator-ready` | 0 | 0 | 0 | 16 | 25 | 0 | 0 |
| `testbed-core` · release · `ui-test-catalog` | 0 | 0 | 0 | 0 | 0 | 37 | 0 |
| `testbed-core` · release · `coverage-matrix` | 0 | 0 | 0 | 15 | 25 | 0 | 0 |

`entities_by_type`: `doc-source` and the inner `generator-ready` `DocumentedFeature=5, DocumentedFunctionality=12,
DocumentedUserStory=3`; the release `generator-ready` `DocumentedFeature=4, DocumentedFunctionality=9,
DocumentedUserStory=3`; each view's `coverage-matrix` `DocumentedFunctionality=12, DocumentedUserStory=3`.

Every artifact's `contract:` line reads: `<contract>-v1.0.0, valid (read_artifact)`, for `doc-source`, `ui-tests`,
`generator-ready`, `ui-test-catalog` and `coverage-matrix`. Every `producer:` line names `living-doc-utilities 0.9.0`:
`AbsaOSS/living-doc-collector-gh 0.3.0` on the collector's two artifacts, and `AbsaOSS/living-doc-toolkit 0.2.0` on the
six toolkit outputs.

**The matrix's `summary`**, from each view's `summary:` block:

| Label · view | `counted_acs` | `covered_acs` | `partially_covered_acs` | `not_covered_acs` | `coverage_pct` |
|---|---|---|---|---|---|
| `testbed-core` · inner | 25 | 21 | 2 | 2 | 88.7 |
| `testbed-core` · release | 25 | 21 | 2 | 2 | 88.7 |

**Input warnings forwarded**, each `forwarded:` line of each view's toolkit log:

| Label · view | `generator-ready` from `doc-source` | `ui-test-catalog` from `doc-source` | `ui-test-catalog` from `ui-tests` | `coverage-matrix` from `doc-source` | `coverage-matrix` from `ui-tests` |
|---|---|---|---|---|---|
| `testbed-core` · inner | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from ui-tests-v1.0.0` | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from ui-tests-v1.0.0` |
| `testbed-core` · release | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from ui-tests-v1.0.0` | `0 of 0 from doc-source-v1.0.0` | `0 of 0 from ui-tests-v1.0.0` |

**The documents**, from each view's generator log: per document, its `input:` and `view:` lines, the run report's
`counts:` block, and `not_loaded` from its `render_manifest:` block.

| Label · view · document | `input:` | `view:` | `entities` | `entities_by_type` | `acceptance_criteria` | `scenarios` | `warnings_by_code` | `not_loaded` |
|---|---|---|---|---|---|---|---|---|
| `testbed-core` · inner · `technical-project-inner` | `generator-ready-v1.0.0, valid (read_artifact)` | `inner` | 20 | `DocumentedFeature=5, DocumentedFunctionality=12, DocumentedUserStory=3` | 33 | 0 | `-` | 0 |
| `testbed-core` · inner · `ui-test-catalog-inner` | `ui-test-catalog-v1.0.0, valid (read_artifact)` | `inner` | 0 | `-` | 0 | 37 | `-` | 0 |
| `testbed-core` · inner · `coverage-matrix-inner` | `coverage-matrix-v1.0.0, valid (read_artifact)` | `inner` | 15 | `DocumentedFunctionality=12, DocumentedUserStory=3` | 25 | 0 | `PLANNED_AC_HAS_TESTS=1, SKIPPED_SCENARIO=2` | 0 |
| `testbed-core` · release · `technical-project-release-v0.1.0` | `generator-ready-v1.0.0, valid (read_artifact)` | `release` | 16 | `DocumentedFeature=4, DocumentedFunctionality=9, DocumentedUserStory=3` | 25 | 0 | `-` | 0 |
| `testbed-core` · release · `ui-test-catalog-release-v0.1.0` | `ui-test-catalog-v1.0.0, valid (read_artifact)` | `release` | 0 | `-` | 0 | 37 | `-` | 0 |
| `testbed-core` · release · `coverage-matrix-release-v0.1.0` | `coverage-matrix-v1.0.0, valid (read_artifact)` | `release` | 15 | `DocumentedFunctionality=12, DocumentedUserStory=3` | 25 | 0 | `PLANNED_AC_HAS_TESTS=1, SKIPPED_SCENARIO=2` | 0 |

Each coverage matrix document's log block ends `warnings: 3`, its input's three (§ 5); every other document's ends
`warnings: 0`. No document prints a `View:` line.

**The checks**, from the runner's `== check:` blocks in `testbed-core/local-integration.log`: the collector's
invariants over `core`, the toolkit's over both views, and the six documents with their run reports. Each block's `OK`
lines:

- **The collector's invariants over `core`:** `doc-source` and `ui-tests` are valid (`doc-source-v1.0.0`,
  `ui-tests-v1.0.0`), each with `sources_failed 0` and no warning. 20 entities, one per file: 3 User Stories (the
  `.feature` files under `projects/core/tests/e2e/features/liv_doc_us`), 12 Functionalities (under
  `projects/core/tests/e2e/features/liv_doc_func`), 5 Features (full-header PageObjects under
  `projects/core/tests/e2e/pages`), every Feature state derived. 33 acceptance criteria, 6 with variants, 3 by
  `Aspect:` and 3 by keyword, each carrying its declared values as aspect. 2 cross-reference pages (PageObjects with
  `parent-feat:`), each a non-primary page on its Feature with its own functionalities and notes; every primary page is
  its Feature's full-header file. 37 scenarios in 16 `.feature` files under `projects/core/tests/e2e/features`, 2 of
  them in 1 file outside the living-doc folders, with no entity and no AC link. 35 AC links, all resolved: 6 aspect
  tags, 4 keyword tags, 1 bare tag on an AC with variants (`aspect: null`). `warnings: none`.
- **The toolkit's invariants over both views:** `generator-ready` and `ui-test-catalog` are valid in the inner and the
  release view, each with no warning; `coverage-matrix` is valid in both, with 3 warnings each. `coverage-matrix.inner`
  and `coverage-matrix.release`: 25 counted criteria each, each verdict equal to what `doc-source` and `ui-tests` give:
  21 covered, 2 partially covered, 2 not covered. The inner view holds every record of `doc-source`; the release view
  drops 7, none left in `planned` or `in_review`. Skipped: `FUNC-009-03`, whose only scenarios are tagged `@skip`,
  covered by none. The 3 warnings in each matrix are exactly the expected ones, one per scenario and criterion it
  links that is `planned` or `in_review`, or counted and linked by a scenario tagged `@skip` (§ 5), and none elsewhere.
- **The six documents and their run reports:** each view's `technical-project`, `ui-test-catalog` and
  `coverage-matrix`, each with its run report, under `<document type>-inner` and `<document type>-release-v0.1.0`.

**Compared with the release go/no-go.** Method: [Compare two runs](../README.md#compare-two-runs), over
`../go-no-go/testbed-core/` and `testbed-core/`: the collector's two artifacts and both views' three toolkit outputs,
each through `tests/examples/normalize_snapshot.py`; the six documents, their run reports and `pin-report.txt`, byte
for byte, each against its file as committed. Result for `testbed-core`:

- **The eight artifacts** are equal to the go/no-go's once normalized, no line different. Before normalization each
  differs in `metadata.generated_at` alone, and each file's size equals the go/no-go's to the byte.
- **The six documents and their six run reports** are byte-identical to the go/no-go's, their source permalinks
  included, as both runs read the testbed at `6b9b3ec`.
- **`pin-report.txt`** is byte-identical to the go/no-go's.
- **The runner's header** differs in its run id, in `living-doc:`, `0884bfb` where the go/no-go ran `a8a4cd0` on the
  go/no-go branch, and in the output path. Between the two, `tests/integration/local-integration.sh`, the testbed
  checks it runs, `tests/examples/check_utilities_pins.py` and the corpus checker's requirement are unchanged; the pins
  moved to the tags. The component lines name the same commits, by tag here and by SHA in the go/no-go.

What was mined and what was rendered are unchanged: the released tags give the output the go/no-go approved.

**The documents against the rendering rules.** Each statement of `living-doc`
[rendering rules](../../reference/rendering-rules.md) § Views, § Test catalog and § Coverage, set against the six
documents. No document differs from a statement. Three statements are not exercised by `core`, which holds no
case for them; they are no defect.

| Rule (rendering rules) | What the documents show | Result |
|---|---|---|
| § Views: inner shows every state, and what was not loaded | `technical-project-inner.md`: 20 of 20 entities and 33 of 33 criteria, 21 `active`, 4 `deprecated`, 3 `in_review` and 5 `planned`; nothing was left unloaded (`not_loaded` 0, no collector warning over `core`), so it shows no not-loaded block | agrees; not loaded not exercised |
| § Views: release drops `planned` and `in_review`, keeps `deprecated`; a dropped entity takes its criteria | `technical-project-release-v0.1.0.md`: 16 of 20 entities and 25 of 28 criteria, 21 `active` and 4 `deprecated`, none `planned` or `in_review`; `FEAT-004`, `FUNC-003`, `FUNC-004` and `FUNC-012` left out with their criteria; `US-001-03`, `-05` and `-06` dropped from the kept `US-001`; the `deprecated` `US-003`, `FEAT-005`, `FUNC-002` and `FUNC-007` kept | agrees |
| § Views: entity preconditions not copied into criteria; a criterion's own show as "also …" | `US-001`'s precondition only on the entity; `AC:US-001-02`'s own under **Also requires**, in both views | agrees |
| § Views: a Feature kept or dropped by its derived state; release badges it only when deprecated | inner: every Feature `DERIVED`, `FEAT-004` `PLANNED`; release: `FEAT-004` dropped, `FEAT-005` alone badged `DEPRECATED` | agrees |
| § Views: release hides a Feature's stub reason and an entity's deprecation date and reason | release: no **Deprecated on** or **Deprecation reason** (inner: 3 and 4); the only stub reason, `FEAT-004`'s, is on a `planned` Feature the release view drops anyway | agrees; stub reason on a kept Feature not exercised |
| § Views: every criterion header in its canonical form | every criterion row and block in both views reads `AC:<ID>` | agrees |
| § Views: each file names its view; each run report follows its document | `<document type>-inner.md` and `<document type>-release-v0.1.0.md`, each with its `.run-report.json` | agrees |
| § Test catalog: tests by the entities they link, then every test by its feature file | both catalogs: User Stories and Functionalities first, each criterion with its tests, then the tests by feature file | agrees |
| § Test catalog: each link carries its criterion's state; release drops a link to `planned` or `in_review` | inner: an **AC state** on every link, `FUNC-012-01` `PLANNED`; release: no `PLANNED` or `IN REVIEW` link, `FUNC-012`'s chapter gone; no link to an `in_review` criterion in `core` | agrees; `in_review` link not exercised |
| § Test catalog: a file whose tests link no criterion is in no chapter; only the inner view lists it, with its tests | inner: `site-is-up.feature: 2 tests` under **Not linked to an entity**; release: neither `site-is-up.feature` nor `func-012-show-renewal-history.feature`, whose one link was dropped | agrees |
| § Test catalog: steps as written, under the `Rule:` name; a file's and a rule's background once, above their tests | `us-001-borrow-a-book.feature`: **Background** once, **Rule background** once, then its two tests, each with **Rule:** | agrees |
| § Coverage: `active` and `deprecated` counted in both views; `in_review` and `planned` not | 25 counted in each matrix, `US-001-04`, `US-003-01`, `FUNC-002-01` and `FUNC-007-01` among them; `FUNC-003`, `FUNC-004` and `FUNC-012` "not applicable"; `PLANNED_AC_HAS_TESTS` on `FUNC-012-01` | agrees |
| § Coverage: a skipped scenario covers nothing; the catalog still lists its link | `FUNC-009-03` `NOT COVERED`; `FUNC-010-01` covered by its two running scenarios; both catalogs list the two `@skip` links as `SKIPPED`, and each of the two tests as "Skipped, not counted"; `SKIPPED_SCENARIO` 2 | agrees |
| § Coverage: the figure weighs partly covered by its share | (21 + 1/2 + 2/3) / 25 = 88.7 %, the summary's figure; `FUNC-001-01` 1/2, `FUNC-005-03` 2/3 | agrees |
| § Coverage: the view never changes which criteria are counted; planned work in the inner view only | both matrices: the same summary and the same 15 entities' rows; the release one is the inner one without **Planned work** (5: backlog 2, `v1.2.0` 3) | agrees |

## 5. Warnings by code

**`testbed-core`.** Any row is a defect, and the run fails on it, but
[a test written ahead's or a skipped scenario's](../../../tests/README.md#the-testbed-stage), which the toolkit check
expects. Each code with its count and its occurrences (`path:line_no entity_id/ac_id message`; the toolkit leaves
`path` and `line_no` unset, as a collector fills them), from the eight artifacts and the six documents:

| Code | Count | Occurrences |
|---|---|---|
| `SKIPPED_SCENARIO` | 2 in each `coverage-matrix` and each coverage matrix document | `-:- FUNC-009/FUNC-009-03` "Member whose loans fail to load sees the error state" is tagged `@skip`; `-:- FUNC-010/FUNC-010-01` "Small fines add up to the cent" is tagged `@skip` |
| `PLANNED_AC_HAS_TESTS` | 1 in each `coverage-matrix` and each coverage matrix document | `-:- FUNC-012/FUNC-012-01` the scenario "a renewed loan lists the date of each renewal" links a `planned` criterion |

All three are expected: the toolkit check matches each on `code`, `ac_id` and `context` (§ 4). They are the go/no-go's
three. Every other artifact's and document's block reads `warnings: 0`, with `warnings_by_code: -`.

`FIELD_LOSS` in any log: none.

## 6. Duplicates found

`DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` per target, by count, or "none": none.

## 7. Timings and sizes

| Label · view · artifact or document | `time:` | `size:` |
|---|---|---|
| `testbed-core` · `doc-source` | 1.02 s | 59014 bytes |
| `testbed-core` · `ui-tests` | 0.88 s | 47060 bytes |
| `testbed-core` · inner · `generator-ready` | 0.97 s | 75983 bytes |
| `testbed-core` · inner · `ui-test-catalog` | 1.08 s | 86041 bytes |
| `testbed-core` · inner · `coverage-matrix` | 1.10 s | 45317 bytes |
| `testbed-core` · inner · `technical-project-inner.md` | 1.17 s | 22534 bytes, run report 4828 bytes |
| `testbed-core` · inner · `ui-test-catalog-inner.md` | 1.17 s | 32287 bytes, run report 6671 bytes |
| `testbed-core` · inner · `coverage-matrix-inner.md` | 0.93 s | 12983 bytes, run report 11230 bytes |
| `testbed-core` · release · `generator-ready` | 1.07 s | 65524 bytes |
| `testbed-core` · release · `ui-test-catalog` | 0.97 s | 85882 bytes |
| `testbed-core` · release · `coverage-matrix` | 0.98 s | 45319 bytes |
| `testbed-core` · release · `technical-project-release-v0.1.0.md` | 0.90 s | 17631 bytes, run report 3851 bytes |
| `testbed-core` · release · `ui-test-catalog-release-v0.1.0.md` | 1.19 s | 30749 bytes, run report 6374 bytes |
| `testbed-core` · release · `coverage-matrix-release-v0.1.0.md` | 0.98 s | 12880 bytes, run report 11243 bytes |

The whole run took about 1.5 minutes on this machine, from 11:25:05 to 11:26:38 UTC, as each component's venv from the
go/no-go's runs was reused. The fourteen timed steps add up to 14 s; the rest is fetching the clones, checking each
venv and the checks.

## 8. Defects

One row per defect found during this run, each with an issue of its own in the repository at fault. The milestone
cannot pass while one from `testbed-core` is open; a parser defect is fixed by a `utilities` patch, a component
release that pins it, and a new milestone run.

| # | Found on | Description | Issue link | State |
|---|---|---|---|---|
| none | none | none | none | none |

## 9. "The output reads correctly"

What is read is each of the six documents under `testbed-core/<view>/generator-markdown/`. Each verdict is the owner's:
yes or no. Each document is byte-identical to the go/no-go's (§ 4), and agrees with the rendering rules (§ 4).

| View | Document | Verdict | What was read (one sentence) |
|---|---|---|---|
| inner | `technical-project-inner.md` | yes | The 20 entities and their 33 criteria in every state, from `active` to `planned`, opening with one overview table per entity type, each entity's criteria as a table, in ascending ID order, each source permalink at `6b9b3ec`. |
| inner | `ui-test-catalog-inner.md` | yes | The 3 User Stories and 10 Functionalities the tests link, each criterion with its state and tests, then the 37 scenarios by feature file with their steps, and `site-is-up.feature`'s 2 tests counted as linking no criterion. |
| inner | `coverage-matrix-inner.md` | yes | The totals, 88.7 % over 25 counted criteria (21 covered, 2 partly, 2 not), one table per entity type, the planned work (5 criteria: 2 in the backlog, 3 for `v1.2.0`), and each of the 15 entities' rows. |
| release | `technical-project-release-v0.1.0.md` | yes | The 16 entities and 25 criteria the release view keeps, with no `planned` or `in_review` criterion, and `FEAT-004`, `FUNC-003`, `FUNC-004` and `FUNC-012` left out. |
| release | `ui-test-catalog-release-v0.1.0.md` | yes | The inner catalog without `FUNC-012`, whose only link, to the `planned` `FUNC-012-01`, the release view drops, and without the two feature files whose tests then link no criterion. |
| release | `coverage-matrix-release-v0.1.0.md` | yes | The same totals and the same 15 entities' rows as the inner view, without the planned-work section. |
