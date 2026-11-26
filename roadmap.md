# Roadmap: pilot feedback → R1

The team tracks progress on the epic [living-doc#144](https://github.com/AbsaOSS/living-doc/issues/144). Every
filed issue is one of its sub-issues, in this roadmap's order, so its progress bar counts them; utilities#224 is the
one exception, a sub-issue of #111. When you file a new one, add it as a sub-issue, put its link in the epic's Subtasks
list and here, and remove its chapter below. Pilot notes: [notes.md](../.local_context/pilot-feedback/notes.md).

## Contents

- [Goal](#goal)
- [Order](#order)
- [Deferred and after R1](#deferred-and-after-r1)
- [Pre-release output](#pre-release-output)
- [Release R1](#release-r1)
- [Debt that wakes on the way](#debt-that-wakes-on-the-way)
- [Owner calls](#owner-calls)
- [Issues](#issues)

## Goal

R1 is `living-doc` `v0.2.0`, the ecosystem release the pilot's feedback asked for:

- coverage counts no scenario tagged `@skip`, and every User Story and Functionality shows its statement;
- the coverage matrix and the technical project open with overview tables, in ascending ID order;
- the UI test catalog has the layout agreed on #155, and every document's file name names its view;
- a pull request that breaks a living-doc header fails its check (#156);
- the milestone run at the R1 tags passes.

The work runs in two passes, each bottom-up through the repositories: a repository's block is finished before the
next one up starts.

1. **Build.** `living-doc-utilities` first, since every component pins it; it ends with the release candidate
   `0.9.0rc2`, which the components pin while they build on it. Then collector-gh, toolkit, generator-markdown, the
   testbed, and `living-doc`.
2. **Release.** Final versions in the same order: utilities `0.9.0`, each component's release PR, the go/no-go, the
   tags, the pin PR and the milestone run.

## Order

This table is the navigation, open tasks only, top to bottom: pick the first **bold** row, it is ready, and do its
Next step. A task is ready once the tasks in its Needs cell are merged. Keep Status and Next step at each task's state
now, with no dates or history: `not filed`, `ready`, `blocked: <tasks>`, `branch …` or `PR …`. Delete a row when its
task merges, and any note below that only it needed.

Every row's issue carries a canon criterion, its own or, for an unfiled row, the draft's under [Issues](#issues);
a review checks it against the diff. A new row gets one when its issue is filed.

| # | Task | Issue | Needs | Status | Next step |
|---|---|---|---|---|---|
| | **Build: `living-doc-utilities`** | | | | |
| 4 | Pin the release actions to their releases | [utilities#246](https://github.com/AbsaOSS/living-doc-utilities/issues/246) | version-tag-check#119, generate-release-notes#367 released | blocked: upstream releases | not R1-blocking: `release_draft.yml` works on the upstream PR heads |
| | **Build: `living-doc-collector-gh`** | | | | |
| **5c** | **The frame: F5 names the shared checks, E2 the `doc-check` mode (`living-doc`)** | [#162](https://github.com/AbsaOSS/living-doc/issues/162) | — | **ready** | collector-gh's `master` has the `doc-check` mode the frame doesn't name yet: merge before the toolkit block starts |
| | **Build: `living-doc-toolkit`** | | | | |
| 6 | `normalize-tests`: new fields, criteria states, release-view drop | [toolkit#126](https://github.com/AbsaOSS/living-doc-toolkit/issues/126) | — | ready after the collector-gh block (bottom-up, see Goal) | decide the input names on the issue; build `CatalogScenario`s (background onto the feature file, `state` on each link), and map the new input paths in the R11 lineage table; pin `0.9.0rc2` (today `0.9.0rc1` in `requirements.txt` and five `pyproject.toml` files) |
| | **Build: `living-doc-generator-markdown`** | | | | |
| 7 | The catalog layout and the view in every file name | [markdown#53](https://github.com/AbsaOSS/living-doc-generator-markdown/issues/53) | — | ready after the toolkit block (bottom-up, see Goal) | decide the release version input's name on the issue; pin `0.9.0rc2` |
| | **Build: `living-doc-testbed`**, with its guard in `living-doc` | | | | |
| **8** | **The testbed checks accept testbed#10's cases** (`living-doc`) | [#158](https://github.com/AbsaOSS/living-doc/issues/158) | — | **ready** | lands on `master` before 9: `real-collector.yml` reads the testbed at `master`, and the pinned toolkit `v0.1.0` already reports `PLANNED_AC_HAS_TESTS` |
| 9 | Gherkin cases `core` doesn't have yet | [testbed#10](https://github.com/AbsaOSS/living-doc-testbed/issues/10) | 8 | blocked: 8 | author the cases |
| | **Build: `living-doc`** | | | | |
| 10 | The go/no-go branch: the testbed checks expect a skipped scenario, and the runner reads the new file names | [#147](https://github.com/AbsaOSS/living-doc/issues/147), [#157](https://github.com/AbsaOSS/living-doc/issues/157) | 7, 8 | #147 on branch `feature/147-testbed-skipped-scenario`, pushed, no PR | rebase #147's branch onto 8; add #157's runner part (`tests/integration/`) to it; no PR: 16 runs from it, 17 merges it |
| 11 | A PR workflow running the collector's `doc-check` mode, in the GitHub Source → Markdown tutorial | [#159](https://github.com/AbsaOSS/living-doc/issues/159) | — | ready after the testbed block (bottom-up, see Goal) | proof run on a testbed fork's PR that breaks one header, with collector-gh's `master`; also § How to check before you push in the authoring guide; the page pins the collector, so it merges with 17 |
| | **Release** | | | | |
| 12 | [Release utilities `0.9.0`](#12-release-utilities) | | 5–9 merged (5b and 5c included), the components green on `0.9.0rc2` | not filed | — |
| 13 | [Prepare the release](#13-to-15-prepare-the-component-releases): collector-gh `v0.3.0` | | 12 | not filed | — |
| 14 | [Prepare the release](#13-to-15-prepare-the-component-releases): toolkit `v0.2.0` | | 12 | not filed | — |
| 15 | [Prepare the release](#13-to-15-prepare-the-component-releases): generator-markdown `v0.2.0` | | 12 | not filed | — |
| 16 | [Release go/no-go](#16-release-gono-go) | | 13, 14, 15, 10 | not filed | on go, the owner tags the three components at the run's commits |
| 17 | [Pin the released tags](#17-pin-the-released-tags) | | 16, tags | not filed | carries #147, #157 and #159, and closes the Pointer #145; moves the checker's pin (`tests/examples/requirements-examples-check.txt`, today `0.8.1`) to `0.9.0` too, which `examples_check.py` fails on until `docs/reference/errors.md` has `MISSING_REQUIRED_KEY` (emitter: collector-gh `doc-check`) and `authoring-documentation.md` says `v0.9.0` for the normalisation cases; then the owner runs Draft Release for `v0.2.0` |
| 18 | [Release milestone run](#18-release-milestone-run) | | 17, `v0.2.0` | not filed | — |

## Deferred and after R1

- **P, the pilot's pre-release run** (owner step, no issue), deferred by the owner. When it is picked up, see
  [Pre-release output](#pre-release-output).
- **#142** (warning policy) and **#143** (coverage regression) go to the toolkit after R1, under #111. They read the
  same policy file as `living-doc-check` (#156).
- **#111's before-merge action and editor extension** wrap `living-doc-check` after R1.
## Pre-release output

An owner step: no issue and no commit, deferred by the owner. It's a local simulation of the whole chain, with every
component at its `master` and the unreleased utilities installed. Once rows 5–7 merge, the documents' file names and the
catalog change, and `check_prerelease.py` reads today's names: it follows them before the next run.

The `living-doc` runner can't do this as it stands. It discards every change in its own clones under `out/`, and each
component builds its venv from `requirements.txt` alone. So the simulation runs the components' own scripts in the
sibling checkouts:

1. Put `living-doc-collector-gh` and `living-doc-generator-markdown` on `master`, and `living-doc-toolkit` on `master`,
   which pins `0.9.0rc1`: it needs `SKIPPED_SCENARIO`.
2. In each of the three components, change the `living-doc-utilities==…` line in `requirements.txt` locally to
   `living-doc-utilities==0.9.0rc1`, and don't commit it in collector-gh or generator-markdown. Their `master` reads
   `0.8.1`; the toolkit's already reads `0.9.0rc1`. Each script then rebuilds
   `.venv-local-integration/`, because the file changed.
3. Run `./local-integration.sh` in `living-doc-collector-gh`, then in `living-doc-toolkit`, then in
   `living-doc-generator-markdown`. Each one's `.env.local` reads the previous one's output. Run the chain over the
   testbed and over the pilot.
4. Check what the bug fixes should show: the User Stories and Functionalities carry `narrative`, a `@skip` scenario
   covers nothing, the entities are in ID order, and the documents have the two new layouts.
5. Restore each `requirements.txt` (`git checkout -- requirements.txt`).
6. Give the pilot's documents to its readers. Their answers check the agreed catalog layout (#155) before R1.

Steps 1–5 are one command, for whatever target collector-gh's `.env.local` points at:
`bash .local_context/pilot-feedback/run_prerelease.sh <folder holding the three checkouts>`. Its step 4,
[`check_prerelease.py`](../.local_context/pilot-feedback/check_prerelease.py), takes every expectation from the run's
own input (the `.feature` descriptions, the `@skip` tags in `ui-tests.json`) and prints IDs, counts and PASS/FAIL only,
so its output can leave the pilot's machine. Both are git-ignored: copy them to the machine that holds the pilot's
checkout.

## Release R1

The release pass, rows 12–18, follows `CONTRIBUTING.md` § Releasing the ecosystem:

1. 12: utilities releases `0.9.0`.
2. 13–15: each component merges its release PR, which sets the version and pins `0.9.0`.
3. 16: the go/no-go runs over each component's `master` commit, from the go/no-go branch (row 10). Nothing merges to
   those `master` branches until the tags exist.
4. On go, the owner tags the three components at the run's commits.
5. 17: the pin PR moves the pins to the tags, and carries #147, #157 and #159.
6. The owner runs `living-doc`'s Draft Release for `v0.2.0`. Its notes carry the compatibility table and "planned
   next": #111's before-merge action and editor extension, and #142 and #143 in the toolkit.
7. 18: the milestone run at the tags.

Versions:

| Package | From | R1 | Why |
|---|---|---|---|
| `living-doc-utilities` | `0.8.1` | `0.9.0` | a new code, contract fields and a new command: minors |
| `living-doc-collector-gh` | `v0.2.0` | `v0.3.0` | it collects the new scenario fields (#170) |
| `living-doc-toolkit` | `v0.1.0` | `v0.2.0` | `normalize-tests` gains a required input (#126) |
| `living-doc-generator-markdown` | `v0.1.0` | `v0.2.0` | new layouts and file names (#53) |
| `living-doc` | `v0.1.0` | `v0.2.0` | |

## Debt that wakes on the way

| Issue | Wakes on | Proposed |
|---|---|---|
| `living-doc-utilities#233` R7 and R11 don't state three readings the toolkit already applies | `when:v1` | kept out of `0.9.0`: re-tagged in #149 |
| `living-doc-utilities#227` Drop the `github` and `html` install extras | `when:utilities-release` | it can go into `0.9.0`: a minor may break installs |
| `living-doc#132` Define how a milestone checks that the documents read correctly | `when:release` | take it into row 18: R1 changes all three layouts, so this release needs the check most |
| `living-doc#136` Decide what `v1.0.0` requires | `when:release` | owner decision; R1 is not `1.0.0` |

Not woken: `living-doc-utilities#228`, coverage per Feature. The owner keeps it waiting on 2026-11-19, so the
overviews in tasks 7 and 8 show no Feature coverage.

## Owner calls

Each one has a recommendation. Change the plan if you decide otherwise.

- The simulation is a local script now (`run_prerelease.sh`). A runner option that installs utilities from a local
  checkout would still be a small `living-doc` task. Recommended: keep the script.
- `living-doc` version: `v0.2.0` (recommended), or `v0.1.1`.
- The integration folders hold one release each (`go-no-go/`, `MS3/`). Recommended: row 16 overwrites
  `go-no-go/`, since `v0.1.0`'s record stays in git and in its release notes, and row 18 writes a new `MS4/` with
  `MS3/` as its baseline.

## Issues

The fields follow each repository's issue form. The labels are `type:*` in `living-doc` and
`living-doc-generator-markdown`, and plain (`bug`, `operative`, …) in the others. A branch is
`<prefix>/<issue>-<scope>`. Rows up to 11 are filed, or follow a filed model (row 3 is filed like RC1), so they have no chapter here: their issues hold
the text. Every draft here carries its canon criterion (CONTRIBUTING.md § Planning ecosystem work, step 4, from #163),
which goes into the filed issue.

### 12. Release utilities

Repo `living-doc-utilities` · Form Operative Task · Label `operative` · Branch `chore/<n>-release-<version>`

Title: Release `0.9.0`

**Task Summary**

Set the package version to `<version>` and release it.

**Description**

Since `v0.8.1`, these have merged:

- a `.feature` file's description is now read into `narrative`, for User Stories and Functionalities (#238)
- the coverage rule says a `@skip` scenario covers nothing, and the code `SKIPPED_SCENARIO` names it (#237)
- `normalize` no longer records a rewrite that changes nothing (#231)
- a scenario's steps, line, rule and backgrounds, and each link's criterion state, in `ui-tests` and
  `ui-test-catalog`, whose ids stay `-v1.0.0` (#249)
- the authored-input check, as a library, the policy file and `MISSING_REQUIRED_KEY` (#224); the check requires the
  `@US_ID`/`@FUNC_ID` tag (#252)
- #227 (install extras dropped), if it was taken in

`0.9.0` is a minor, because #237 adds a code, and its notes list every breaking change with its migration.

**Objectives / Goals**

- `pyproject.toml` `version` is `<version>`, released by `DEVELOPER.md` § Release.
- The wheel and sdist are on PyPI, checked with `pip download`, because the JSON API lags.
- The release PR lists the re-pin PRs that must follow: rows 13–15.

**Canon Check**

- **Canon:** the notes describe the contracts and codes as `docs/contracts/` does, and every change since `v0.8.1`
  that alters a `living-doc` canon statement has its update planned: #157 (the test catalog), #162 (F5, E2), row 17
  (the error codes).

### 13 to 15. Prepare the component releases

One issue per component, each modelled on its previous release issue (`generator-markdown` #37). The versions come
from the [Release R1](#release-r1) table.

| # | Repo | Title | Label | Branch |
|---|---|---|---|---|
| 13 | `living-doc-collector-gh` | Prepare the `<version>` release | `operative` | `chore/<n>-release-<version>` |
| 14 | `living-doc-toolkit` | Prepare the `<version>` release | `operative` | `chore/<n>-release-<version>` |
| 15 | `living-doc-generator-markdown` | Prepare the `0.2.0` release | `type:operative` | `chore/<n>-release-0.2.0` |

Body, each repository's Operative Task form:

**Task Summary**

Prepare the `<version>` release: set the version and pin R1's `living-doc-utilities`.

**Description**

Step 1 of `DEVELOPER.md` § Release. The tag comes later, at the commit the ecosystem's release go/no-go ran over.

**Objectives / Goals**

- `pyproject.toml` `version` is `<version>`, and R1's `living-doc-utilities` is pinned everywhere the repository pins
  it. Close Dependabot's bump PR for it, if one is open.
- The draft release notes list what merged since the last tag. The `generator-markdown` notes have a § Migration for
  the new layouts and the new file names; the toolkit's for `normalize-tests`' new input.
- Every check is green.

**Canon Check**

- **Canon:** the release changes no canon statement beyond those its merged issues' canon criteria named, and its
  migration notes describe the layouts and inputs as `living-doc`'s pages will after row 17.

### 16. Release go/no-go

Repo `living-doc` · Form Documentation Task · Label `type:documentation` · Branch `docs/<n>-release-go-no-go`

Title: Run the release go/no-go for v0.2.0 over the testbed, and file its report

**Summary**

Run `tests/integration/local-integration.sh` from the go/no-go branch over the testbed's `core`, with every component
at its release PR's merge commit. The branch holds #147's checker, which expects `core`'s skipped scenarios, and
#157's runner part, which reads the generator's new file names; both merge in row 17. Commit the run's files under `docs/_integration/go-no-go/testbed-core/` and fill
`docs/_integration/go-no-go/report.md`.

**Current State (If Updating)**

`go-no-go/` holds `v0.1.0`'s run.

**Proposed Changes**

- `env.local`: the three component SHAs and the testbed's `master` SHA.
- The report compares the run with `MS3/testbed-core/` and explains every difference. The expected differences are
  the producer versions, `narrative` on each User Story and Functionality, ID order, the new layouts of all three
  documents, the new file names, and testbed#10's cases.
- The verdict is go or no-go. On go, the owner tags the three components at the run's SHAs, and nothing merges to
  their `master` branches before that.

**Acceptance Criteria**

- **Canon:** every difference the report explains is one a merged issue's canon criterion named; a difference no
  criterion named is a no-go until its issue says where the canon changes.

**Dependencies / References**

`docs/_integration/README.md` § Release go/no-go; owner call: overwrite `go-no-go/`.

### 17. Pin the released tags

Repo `living-doc` · Form Technical Debt · Label `type:tech-debt` · Branch `chore/<n>-pin-component-tags`

Title: Pin the released component tags and R1's living-doc-utilities

**Description of Technical Debt**

`tests/collector/collector-pins.env` pins `v0.2.0`, `v0.1.0` and `v0.1.0`, and the corpus checker pins
`living-doc-utilities==0.8.1`. The R1 tags are out.

**Impact of Technical Debt**

The docs, the snapshots and the checks describe the previous release.

**Proposed Solution**

- Pins: the three R1 tags in `collector-pins.env`, and R1's utilities in `tests/examples/requirements-examples-check.txt`.
- #147's change, from its branch: the testbed checks expect `core`'s skipped scenarios. The PR closes #147 too. Merged
  alone, either half fails the testbed job: the R1 toolkit gives `SKIPPED_SCENARIO` over `core`, `v0.1.0` counts a
  skipped scenario.
- Every page link that names a component tag moves to the new tag: `docs/guides/build-a-pipeline.md`,
  `docs/guides/github-collection.md`, `docs/reference/data-flows.md`, `docs/tutorials/gh-source-to-markdown.md`
  (including § 5), and whatever else `tests/docs/` finds.
- Regenerate `docs/examples/_expected/`. The User Stories and Functionalities gain `narrative`.
- `tests/examples/examples_check.py` `_report_rewrites` drops its `before == after` filter: with #231 fixed it hides
  nothing, and without it the corpus check catches a regression.
- `docs/reference/rendering-rules.md` § Coverage gains the sentence that a scenario tagged `@skip` covers nothing,
  and `docs/reference/errors.md` the `SKIPPED_SCENARIO` row (rule 9). This is the last PR of the Pointer issue, #145.
- `docs/guides/authoring-documentation.md` links `normalisation_cases.yaml` at `v0.9.0` (rule 8). The case #231 added
  needs no pair in the guide.
- `docs/reference/errors.md` gains the `MISSING_REQUIRED_KEY` row, emitted by collector-gh's `doc-check` mode:
  `examples_check.py` fails on the new checker pin until it does.
- #157 and #159 land here: the new catalog and file names in the guides and tutorials, and the tutorial's
  pull-request check.
- `go-no-go/report.md` § 1 "Tags cut".
- Every check in `AGENTS.md` § This project passes.

**Canon Check**

- **Canon:** after this PR the canon pages agree with the pinned releases: `errors.md` lists every code of the pinned
  utilities, the guides and tutorials describe the new catalog and the check, and `examples_check.py` passes at the
  new pin.

**Dependencies / Related**

The go/no-go issue; the `@skip` Pointer issue, #145.

After this merges, the owner runs Draft Release for `v0.2.0`. Its notes carry the compatibility table and "planned
next".

### 18. Release milestone run

Repo `living-doc` · Form Documentation Task · Label `type:documentation` · Branch `docs/<n>-release-milestone-run`

Title: Run the release milestone over the testbed at the v0.2.0 tags, and file its report

**Summary**

Run `tests/integration/local-integration.sh` over the testbed's `core`, with every component at its released tag.
Commit the run's files under `docs/_integration/MS4/testbed-core/` and fill `docs/_integration/MS4/report.md`.

**Proposed Changes**

- `MS4/` starts from `MS3/`'s report and `env.local` at the R1 tags.
- The comparison is with `go-no-go/testbed-core/`: the artifacts are equal once normalised, and the documents are
  byte-identical.
- If `living-doc#132` is taken in, the report checks that the three documents read correctly, now that their layouts
  have changed.

**Acceptance Criteria**

- **Canon:** the documents at the release tags show what the canon says each view shows, and the report names every
  place they differ.

**Dependencies / References**

`docs/_integration/README.md` § Run a milestone target; owner call: `MS4/`.
