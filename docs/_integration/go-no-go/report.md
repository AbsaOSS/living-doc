# Release go/no-go report: the source-code chain at its release candidates

## Purpose

The record of the release go/no-go: one run of
[`tests/integration/local-integration.sh`](../../../tests/integration/local-integration.sh) over the testbed's `core`,
with every component at the commit its release will tag: `living-doc-collector-gh`, then `living-doc-toolkit` and
`living-doc-generator-markdown` in the inner and the release view. When to run it and what follows: [Integration runs
§ Release go/no-go](../README.md#release-gono-go). How to fill it: [Run a milestone target](../README.md#run-a-milestone-target).

Every figure comes from the run's logs and its pin report. Only the testbed decides; the run's exit is the verdict.
This report replaces `v0.1.0`'s, which stays in git and in that release's notes. The release run fills it and files it
by a pull request of its own.

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

- **Release:** `living-doc` `v0.2.0`, with `living-doc-collector-gh` `v0.3.0`, `living-doc-toolkit` `v0.2.0`,
  `living-doc-generator-markdown` `v0.2.0`, on `living-doc-utilities` `0.9.0`
- **Date:** 2026-11-27
- **Operator:** miroslavpojer; the chain was run for the operator by an agent session on the operator's machine
- **Machine type:** Windows 11 Pro, Git Bash (GNU bash 5.2.21), Python 3.14.6 (`PYTHON=python`), testbed only
- **Release pull requests merged:** `living-doc-collector-gh`
  [#176](https://github.com/AbsaOSS/living-doc-collector-gh/pull/176), merged as
  `3219c9350e96d463a456e4384b4a58a117926233`; `living-doc-toolkit`
  [#128](https://github.com/AbsaOSS/living-doc-toolkit/pull/128), merged as `85e94232ba3294a1c8f86644ebe56d65b9d94a20`;
  `living-doc-generator-markdown` [#56](https://github.com/AbsaOSS/living-doc-generator-markdown/pull/56), merged as
  `d0e8b49cdaf9b6892327f8849742736408baeda3`. Each merge commit is the candidate the run used (§ 3).
- **Verdict:** go: the run exited 0 (run id `20261127T093454Z`)
- **The runner's last line:** `tests/integration/local-integration.sh: the chain and the testbed's invariants passed:
  the six documents are under <checkout>/docs/_integration/go-no-go/testbed-core/{inner,release}/generator-markdown`,
  with the machine's path to the `living-doc` checkout shown as `<checkout>`
- **Earlier runs:** two runs over the same candidates went before this one, and each stopped on `living-doc`'s side,
  not on a candidate's (§ 8)
- **Owner sign-off:** go, 2026-11-27
- **Tags cut, each at its commit in § 3, after go:** pending
- **Testbed commit in the release notes:** `AbsaOSS/living-doc-testbed` `master` at
  `6b9b3ec9262032518023a3cd6e9f86acf97d1f89`

### CI evidence

- **Each candidate's own CI**, "Static analysis & tests", green on its candidate commit (push, 2026-11-27):
  `living-doc-collector-gh` (<https://github.com/AbsaOSS/living-doc-collector-gh/actions/runs/45969605256>),
  `living-doc-toolkit` (<https://github.com/AbsaOSS/living-doc-toolkit/actions/runs/45970033540>) and
  `living-doc-generator-markdown` (<https://github.com/AbsaOSS/living-doc-generator-markdown/actions/runs/45969701190>).
- **Each candidate's "Link check":** green on `living-doc-toolkit`
  (<https://github.com/AbsaOSS/living-doc-toolkit/actions/runs/45970033619>). On `living-doc-collector-gh`
  (<https://github.com/AbsaOSS/living-doc-collector-gh/actions/runs/45969605232>) and `living-doc-generator-markdown`
  (<https://github.com/AbsaOSS/living-doc-generator-markdown/actions/runs/45969701230>) it failed on `503 Service
  Unavailable` from github.com alone, 15 and 2 links, with no link broken.
- **`living-doc`:** the run used the go/no-go branch, which has no pull request and no workflow run (§ 3).
- **The testbed stage:** `real-collector.yml` runs the components at their pins in
  [`tests/collector/collector-pins.env`](../../../tests/collector/collector-pins.env), not at these candidates, so it is
  no evidence for this run. It runs them once the pins move to the tags.

## 2. Targets

| Label | Kind | Decides the release | Target SHA (`target:` line) | Configuration |
|---|---|---|---|---|
| `testbed-core` | public, `AbsaOSS/living-doc-testbed` `projects/core/` | yes | `6b9b3ec9262032518023a3cd6e9f86acf97d1f89` | [`testbed-core/env.local`](testbed-core/env.local): `TARGET=testbed`, the testbed and every component at a full commit SHA, `RELEASE_VERSION=0.1.0` |

The runner's `target:` line: `testbed-core: AbsaOSS/living-doc-testbed <SHA> (<SHA>)`, the SHA above both times, the
second being the configured `TESTBED_REF`. It marks no uncommitted change. `release version: 0.1.0` is the release of
the testbed's content the run reads, which the operator named; it is not `living-doc`'s version.

`--check`: passed, exit 0 (run id `20261127T093447Z`). The run's exit: 0 (run id `20261127T093454Z`). No internal
target was run: only the testbed decides the release.

## 3. Component refs and `utilities` pins

From the runner's header in `testbed-core/local-integration.log` and each component log's header. Each component line
must show its configured ref, `(COLLECTOR_GH_REF=<full SHA>)` and so on, never `(pin)`, and no uncommitted change.

| Runner line | `testbed-core` |
|---|---|
| `living-doc:` | `a8a4cd01b55876e3abdcb0524cd450b24f26acba` |
| `collector-gh:` | `3219c9350e96d463a456e4384b4a58a117926233` `(COLLECTOR_GH_REF=3219c9350e96d463a456e4384b4a58a117926233)` |
| `toolkit:` | `85e94232ba3294a1c8f86644ebe56d65b9d94a20` `(TOOLKIT_REF=85e94232ba3294a1c8f86644ebe56d65b9d94a20)` |
| `generator-markdown:` | `d0e8b49cdaf9b6892327f8849742736408baeda3` `(GENERATOR_MARKDOWN_REF=d0e8b49cdaf9b6892327f8849742736408baeda3)` |
| `python:` | `3.14.6 (python)` |

No line is marked with uncommitted changes, and each component runs at its configured ref, none at its pin.

The `living-doc` commit is on the go/no-go branch, `feature/147-testbed-skipped-scenario`, not on `master`: `master`'s
testbed checks count a skipped scenario, and its runner reads the generator's old file names. The branch holds #147's
checks, #157's runner part, the corpus checker's pin `0.9.0` and the runner fix of § 8; they reach `master` with the
pull request that pins the released tags. `a8a4cd0`'s own change is under `go-no-go/testbed-core/` alone, which the
`living-doc` line leaves out; the runner is its parent `1324e93`'s.

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

The three components pin `0.9.0`, and so does `examples-check`, this repository's corpus checker, since `6c55cf6`
(§ 8). No pin is a release candidate.

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
six toolkit outputs, whose `source_inputs` name the collector at `0.3.0`.

**The release view's `ui-test-catalog` is a release view now.** Its `document.view` is `release`, and it drops the one
link to a criterion the release view leaves out, the `planned` `FUNC-012-01`, while its scenario stays in its feature
file's group. Each view's catalog holds all 37 scenarios. The release document then leaves out the two feature files
whose tests link no criterion, `func-012-show-renewal-history.feature` and `site-is-up.feature`, as the generator's
release view does (AbsaOSS/living-doc-generator-markdown#53).

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

`normalize-tests` reads `doc-source` too since `living-doc-toolkit` `v0.2.0`, for each link's criterion state.

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

**Compared with the MS3 run.** Method: [Compare two runs](../README.md#compare-two-runs), over
`../MS3/testbed-core/`, the last committed run of the chain, and `testbed-core/`: the collector's two artifacts, and
both views' three toolkit outputs, each through `tests/examples/normalize_snapshot.py`, then set side by side by
entity, criterion and scenario id. MS3 read the testbed at `36a0ee6`; this run reads `6b9b3ec`. Each difference, with
the merged issue it comes from and the canon statement it agrees with:

| Difference from MS3 | Where | From | Canon |
|---|---|---|---|
| `living-doc-collector-gh` `0.2.0` → `0.3.0`, `living-doc-toolkit` `0.1.0` → `0.2.0`, `utilities_version` `0.8.1` → `0.9.0` | every artifact's producer and `source_inputs` | the release pull requests (§ 1) | their canon criteria: no canon statement changes beyond their features' |
| A `narrative` on 3 User Stories and 11 Functionalities; `FUNC-009`'s stays `null`, as its file has no description under `Feature:` | `doc-source`, `generator-ready` (11 in the release view, whose 9 Functionalities hold 8) | AbsaOSS/living-doc-utilities#238 | `living-doc-utilities` `docs/authoring/parsers.md` at `v0.9.0`: the description under `Feature:` is the entity's `narrative`, and a file with none keeps `None` |
| The criterion `FUNC-009-03` (`active`), and 9 scenarios (28 → 37): `FUNC-009`'s 4 and `FUNC-010`'s 2, 2 of them tagged `@skip`; `FUNC-012-01`'s scenario; and `US-001`'s 2 under a `Rule:` with a `Background:` | `doc-source`, `ui-tests`, every toolkit output | AbsaOSS/living-doc-testbed#8, AbsaOSS/living-doc-testbed#10 | `living-doc` [authoring formats](../../reference/authoring-formats.md) § 1, § 3 and the scenario tag; testbed#10's canon criterion |
| `steps`, `line`, `rule`, `background` and `rule_background` on every scenario; a feature file's `background` once on the file | `ui-tests`, `ui-test-catalog` | AbsaOSS/living-doc-utilities#249, AbsaOSS/living-doc-collector-gh#170, AbsaOSS/living-doc-toolkit#126 | their canon criteria: the collector records what the file says (F2), the contract fields are `living-doc-utilities`' (F5) |
| Each catalog link carries its criterion's `state`; the release view drops the link to `FUNC-012-01` (`planned`) and keeps its scenario | `ui-test-catalog` | AbsaOSS/living-doc-toolkit#126 | its canon criterion: the release view drops what the rendering rules drop (`planned`, `in_review`) and keeps `deprecated` |
| A scenario tagged `@skip` covers nothing: `FUNC-009-03` is `not_covered`, and `FUNC-010-01` counts its running scenarios alone; one `SKIPPED_SCENARIO` per skipped scenario and counted criterion it links (2) | `coverage-matrix` | AbsaOSS/living-doc-utilities#237, AbsaOSS/living-doc-toolkit#123 | `living-doc-utilities` `docs/contracts/rendering.md` § Coverage at `v0.9.0` |
| `US-001-02` `not_covered` → `covered`, by testbed#10's scenario; `FUNC-009-01`, `FUNC-009-02`, `FUNC-010-01` and `US-001-01` gain a scenario; the summary 24 → 25 counted, 20 → 21 covered, 88.2 → 88.7 % | `coverage-matrix` | the scenarios above | the same § Coverage |
| `PLANNED_AC_HAS_TESTS` on `FUNC-012-01` (1 in each matrix) | `coverage-matrix` | AbsaOSS/living-doc-testbed#10, a test written ahead | the same § Coverage; `living-doc` [error codes](../../reference/errors.md) |

Before normalization each artifact also differs in `metadata.generated_at`, and in the commit inside each source
permalink. Nothing else differs.

**The six documents** differ from MS3's in name and in layout, by design, and are compared by reading (§ 9): each
file names its view, `<document type>-inner.md` and `<document type>-release-v0.1.0.md`, with `RELEASE_VERSION` a
required input (AbsaOSS/living-doc-generator-markdown#53); entities render in ascending ID order
(AbsaOSS/living-doc-generator-markdown#44); the coverage matrix opens with its totals and one table per entity type
(AbsaOSS/living-doc-generator-markdown#45); the technical project opens with one overview table per entity type and
shows each entity's criteria as a table (AbsaOSS/living-doc-generator-markdown#46); the UI test catalog lists the
linked User Stories and Functionalities first, each criterion with its tests, then the tests by feature file, and a
skipped scenario says it covers nothing (AbsaOSS/living-doc-generator-markdown#47, #53); and no document prints a
`View:` line. These are presentation only: the generator renders what its input holds (F4), and no canon statement
holds or changes the order or the tables. The catalog's layout follows `living-doc-utilities`
`docs/contracts/rendering.md` § Test catalog, as #53's canon criterion names.

Eight of the merged issues above predate the canon criterion every issue carries since #163:
AbsaOSS/living-doc-utilities#237 and #238, AbsaOSS/living-doc-toolkit#123,
AbsaOSS/living-doc-generator-markdown#44 to #47, and AbsaOSS/living-doc-testbed#8. Their differences are matched here
with the canon page that states them instead; the owner decided (2026-11-27) that those issues stay without one.

## 5. Warnings by code

**`testbed-core`.** Any row is a defect, and the run fails on it, but
[a test written ahead's or a skipped scenario's](../../../tests/README.md#the-testbed-stage), which the toolkit check
expects. Each code with its count and its occurrences (`path:line_no entity_id/ac_id message`; the toolkit leaves
`path` and `line_no` unset, as a collector fills them), from the eight artifacts and the six documents:

| Code | Count | Occurrences |
|---|---|---|
| `SKIPPED_SCENARIO` | 2 in each `coverage-matrix` and each coverage matrix document | `-:- FUNC-009/FUNC-009-03` "Member whose loans fail to load sees the error state" is tagged `@skip`; `-:- FUNC-010/FUNC-010-01` "Small fines add up to the cent" is tagged `@skip` |
| `PLANNED_AC_HAS_TESTS` | 1 in each `coverage-matrix` and each coverage matrix document | `-:- FUNC-012/FUNC-012-01` the scenario "a renewed loan lists the date of each renewal" links a `planned` criterion |

All three are expected: the toolkit check matches each on `code`, `ac_id` and `context` (§ 4). Every other
artifact's and document's block reads `warnings: 0`, with `warnings_by_code: -`.

`FIELD_LOSS` in any log: none.

## 6. Duplicates found

`DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` per target, by count, or "none": none.

## 7. Timings and sizes

| Label · view · artifact or document | `time:` | `size:` |
|---|---|---|
| `testbed-core` · `doc-source` | 0.93 s | 59014 bytes |
| `testbed-core` · `ui-tests` | 0.99 s | 47060 bytes |
| `testbed-core` · inner · `generator-ready` | 0.93 s | 75983 bytes |
| `testbed-core` · inner · `ui-test-catalog` | 1.10 s | 86041 bytes |
| `testbed-core` · inner · `coverage-matrix` | 1.09 s | 45317 bytes |
| `testbed-core` · inner · `technical-project-inner.md` | 0.84 s | 22534 bytes, run report 4828 bytes |
| `testbed-core` · inner · `ui-test-catalog-inner.md` | 0.96 s | 32287 bytes, run report 6671 bytes |
| `testbed-core` · inner · `coverage-matrix-inner.md` | 0.94 s | 12983 bytes, run report 11230 bytes |
| `testbed-core` · release · `generator-ready` | 0.95 s | 65524 bytes |
| `testbed-core` · release · `ui-test-catalog` | 1.06 s | 85882 bytes |
| `testbed-core` · release · `coverage-matrix` | 1.10 s | 45319 bytes |
| `testbed-core` · release · `technical-project-release-v0.1.0.md` | 0.87 s | 17631 bytes, run report 3851 bytes |
| `testbed-core` · release · `ui-test-catalog-release-v0.1.0.md` | 0.96 s | 30749 bytes, run report 6374 bytes |
| `testbed-core` · release · `coverage-matrix-release-v0.1.0.md` | 0.96 s | 12880 bytes, run report 11243 bytes |

The whole run took about 1.5 minutes on this machine, from 09:34:54 to 09:36:22 UTC, as each component's venv from the
earlier runs was reused. The fourteen timed steps add up to 14 s; the rest is fetching the clones, checking each venv
and the checks.

## 8. Defects

One row per defect found during this run, each with an issue of its own in the component at fault. A defect from
`testbed-core` is a no-go: its fix makes a new candidate, and a new run replaces this one. A parser defect is fixed by
a `utilities` patch and a new release pin first.

No candidate has a defect. Two earlier runs over the same candidates stopped on `living-doc`'s side; each was fixed
under #177 on the go/no-go branch, and the next run replaced it, with no new candidate:

| # | Found on | Description | Issue link | State |
|---|---|---|---|---|
| 1 | run `20261127T091315Z`, at `living-doc` `5f61315` | The strict pin report failed on a minor skew: the corpus checker pinned `living-doc-utilities` `0.8.1`, the components `0.9.0`. The chain had passed; the testbed checks did not run. | [#177](https://github.com/AbsaOSS/living-doc/issues/177) | fixed in `living-doc` `6c55cf6`: the checker pins `0.9.0`, with the guide's and the error codes' pages in line |
| 2 | run `20261127T092236Z`, at `living-doc` `6c55cf6` | Everything passed, but the `living-doc` line read `(uncommitted changes)`: the runner cleared `v0.1.0`'s committed files in its output root before it took that line, so the run could not count. | [#177](https://github.com/AbsaOSS/living-doc/issues/177) | fixed in `living-doc` `1324e93`: the `living-doc` line leaves the output root out |

## 9. "The output reads correctly"

What is read is each of the six documents under `testbed-core/<view>/generator-markdown/`. Each verdict is the owner's:
yes or no.

| View | Document | Verdict | What was read (one sentence) |
|---|---|---|---|
| inner | `technical-project-inner.md` | yes | The 20 entities and their 33 criteria in every state, from `active` to `planned`, opening with one overview table per entity type, each entity's criteria as a table, in ascending ID order. |
| inner | `ui-test-catalog-inner.md` | yes | The 3 User Stories and 10 Functionalities the tests link, each criterion with its state and tests, then the 37 scenarios by feature file with their steps, and `site-is-up.feature`'s 2 tests counted as linking no criterion. |
| inner | `coverage-matrix-inner.md` | yes | The totals, 88.7 % over 25 counted criteria (21 covered, 2 partly, 2 not), one table per entity type, the planned work (5 criteria: 2 in the backlog, 3 for `v1.2.0`), and each of the 15 entities' rows. |
| release | `technical-project-release-v0.1.0.md` | yes | The 16 entities and 25 criteria the release view keeps, with no `planned` or `in_review` criterion, and `FEAT-004`, `FUNC-003`, `FUNC-004` and `FUNC-012` left out. |
| release | `ui-test-catalog-release-v0.1.0.md` | yes | The inner catalog without `FUNC-012`, whose only link, to the `planned` `FUNC-012-01`, the release view drops, and without the two feature files whose tests then link no criterion. |
| release | `coverage-matrix-release-v0.1.0.md` | yes | The same totals and the same 15 entities' rows as the inner view, without the planned-work section. |
