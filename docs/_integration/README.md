# Integration runs

## Purpose

This page is how to run the whole source-code chain on a local machine and record the release go/no-go. Each run
uses this repository's runner, [`tests/integration/local-integration.sh`](../../tests/integration/local-integration.sh).
The runner clones the three components and runs their `local-integration.sh` in a row: `living-doc-collector-gh`,
then `living-doc-toolkit` and `living-doc-generator-markdown` in each view. It runs over the public testbed's `core`,
and optionally over internal repositories on a machine that can reach them.

- **The release go/no-go**, in `go-no-go/`, decides whether the three components may be tagged. It is one testbed
  run on the commits that the release will tag. Its record is the only run record a release keeps, and the release
  pin pull request files it.
- **Any other run** is a trial: it writes to `out/`, which git ignores.

This folder holds the go/no-go's report and the data from its run, so the next go/no-go can be compared with it. The
earlier gate and milestone records are in git history, in
[`docs/_integration/` at `e713454`](https://github.com/AbsaOSS/living-doc/tree/e713454/docs/_integration).

**This repository is public.** A run over an internal repository keeps its configuration, its log and its artifacts
on the machine it ran on. Only its row in the report, with a label, counts and codes, may be committed.

Read before:

- each component's DEVELOPER.md, section "Local Integration Run":
  [`living-doc-collector-gh`](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/DEVELOPER.md),
  [`living-doc-toolkit`](https://github.com/AbsaOSS/living-doc-toolkit/blob/master/DEVELOPER.md#local-integration-run)
  and [`living-doc-generator-markdown`](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/DEVELOPER.md#local-integration-run).
  Each covers what its script needs, every `.env.local` key, and what a run prints;
- the runner's own settings, in [`tests/integration/.env.local.example`](../../tests/integration/.env.local.example).

The CI counterpart of the testbed run is the testbed stage in [`tests/README.md`](../../tests/README.md).

## Contents

- [Layout](#layout)
- [What may be committed](#what-may-be-committed)
- [Before the first run](#before-the-first-run)
- [Run the chain](#run-the-chain)
- [Release go/no-go](#release-gono-go)
- [Warnings on an internal target](#warnings-on-an-internal-target)
- [Compare two runs](#compare-two-runs)
- [Before you commit](#before-you-commit)

## Layout

```
docs/_integration/
  README.md                      this page
  .gitignore                     keeps every internal/ folder and every log out of git
  go-no-go/
    report.md                    the release go/no-go report
    testbed-core/                the runner's output root for the testbed's core
      env.local                  the runner's configuration, its refs left empty for the operator
      local-integration.log      the runner's own log: the resolved refs, each step (ignored)
      pin-report.txt             the living-doc-utilities pins of the clones that ran
      collector-gh/local-integration.log            the collector's log (ignored)
      collector-gh/doc-source/doc-source.json
      collector-gh/ui-tests/ui-tests.json
      inner/                     the inner view
        toolkit/local-integration.log               the toolkit's log (ignored)
        toolkit/normalize-docs/generator-ready.json
        toolkit/normalize-tests/ui-test-catalog.json
        toolkit/coverage-matrix/coverage-matrix.json
        local-integration.log    the generator's log, beside the folder it clears as a whole (ignored)
        generator-markdown/<document type>-inner.md, <document type>-inner.run-report.json
      release/                   the release view: the same files, each document named
                                 <document type>-release-v<RELEASE_VERSION>
    internal/                    ignored as a whole
      <label>/                   env.local and the same files as testbed-core/
```

The runner's clones of the components and the testbed live in `out/` at the repository's root, which git ignores,
never in `go-no-go/`.

The labels `absa-1`, `absa-2` and `absa-3` stand in for the repositories' names everywhere outside `internal/`. Which
label is which repository is written down only in each folder's `env.local`.

## What may be committed

| Item | Testbed target | Internal target |
|---|---|---|
| `env.local`, the copy of the runner's configuration kept with the run (the working copy, `tests/integration/.env.local`, is git-ignored) | committed | stays on the machine |
| every `local-integration.log`: the runner's, and each component's | stays on the machine | stays on the machine |
| `collector-gh/**/*.json`, `<view>/toolkit/**/*.json` | may be committed (public content) | stays on the machine |
| `pin-report.txt` | may be committed: it names the pins and paths inside `living-doc` only | stays on the machine; it names no target, so the report may quote it whole |
| `<view>/generator-markdown/*.md`, `*.run-report.json` | may be committed (public content) | stays on the machine |
| Row in `report.md` | everything: SHA, counts, codes, each warning's first ten occurrences | label, SHA, counts, codes and their counts; **no** repository or organization name, path, entity id, AC text or warning message |

A run over an internal repository runs on a machine that can reach it. Nothing about the repository's content leaves
that machine, only its shape.

The rendered documents may be committed: their links pass `link-check.yml`. A go/no-go whose documents fail the link
check, or `retired-names.yml`, commits its JSON only, and its report says why.

## Before the first run

On the machine that runs the chain, you need:

1. **Tools.** Python ≥ 3.10 with its `venv` module, `git`, and bash: Linux, macOS, or Git Bash on Windows. pip must be
   able to install from PyPI or its mirror (`pip.conf`, `PIP_INDEX_URL`, a proxy); the scripts use that config as it is.
2. **A `living-doc` checkout.** The runner clones the components and the testbed itself, at the refs its configuration
   names.
3. **For an internal target, its checkout at the commit to be read.** That is its default branch, up to date, with no
   local change (`git -C <target> status` clean). The run records the commit it read. The runner checks out the
   testbed itself: at `master`, or at the tag or SHA its `TESTBED_REF` names.

## Run the chain

The runner runs the whole chain for one target with one command, from the root of the `living-doc` checkout. Run
`testbed-core` first, then each internal repository under its label. The runner runs each component's own
`local-integration.sh`, unchanged, so a component's output and log are the ones its DEVELOPER.md describes.

### 1. Configure the runner

The configuration is `tests/integration/.env.local`, which git ignores. Its keys, each with a comment, are in
[`tests/integration/.env.local.example`](../../tests/integration/.env.local.example). A relative path resolves against
the `living-doc` checkout.

- **The testbed.** Its configuration is committed: [`go-no-go/testbed-core/env.local`](go-no-go/testbed-core/env.local).
  `TARGET=testbed` makes the runner clone `living-doc-testbed` and configure `core` as the CI testbed stage does; no
  internal access is needed. For a trial run, empty its `OUT_DIR`, so the run writes to `out/`.

  ```shell
  cp docs/_integration/go-no-go/testbed-core/env.local tests/integration/.env.local
  ```

- **An internal target.** Find its paths first. The collector takes a file's type from the folder list it is
  configured under, not from the file itself, and it reads `.ts` PageObjects only. Run these in the target's checkout,
  and note the folders they print:

  ```shell
  grep -rlE --include='*.feature' 'LIVING DOC .*US-[0-9]'   . | xargs -r -n1 dirname | sort -u   # User Stories
  grep -rlE --include='*.feature' 'LIVING DOC .*FUNC-[0-9]' . | xargs -r -n1 dirname | sort -u   # Functionalities
  grep -rlE --include='*.ts'      'LIVING DOC .*FEAT-[0-9]' . | xargs -r -n1 dirname | sort -u   # Feature PageObjects
  grep -rl  --include='*.feature' '@AC:'                    . | xargs -r -n1 dirname | sort -u   # scenarios with AC tags
  ```

  - User Story and Functionality files must sit in separate folders, because the folder decides the type. A folder
    holding both is an authoring deviation: note it in the report, and configure the folder under the type most of its
    files have.
  - `DOC_SOURCE_US_PATHS` and `UI_TESTS_PATHS` are required. If a repository has no User Story file, point
    `DOC_SOURCE_US_PATHS` at a folder of the checkout that holds no `.feature` file, and note it in the report.
  - A path is relative to the target's checkout and may not lead outside it. Separate several paths with commas.
  - PageObjects in a language other than TypeScript are not read in this version. Note how many there are.

  Then create `docs/_integration/go-no-go/internal/<label>/env.local`, and copy it the same way:

  ```shell
  TARGET=project
  PROJECT_ID=absa-1
  TARGET_CHECKOUT=../<internal repository folder>
  ORGANIZATION_NAME=<its GitHub organization>
  REPOSITORY_NAME=<its name on the server>
  DOC_SOURCE_US_PATHS=<from the search above>
  DOC_SOURCE_FUNC_PATHS=<from the search above, or empty>
  DOC_SOURCE_PAGES_PATHS=<from the search above, or empty>
  UI_TESTS_PATHS=<from the search above>
  GITHUB_SERVER_URL=<empty for github.com; the server's URL for GitHub Enterprise Server>
  RELEASE_VERSION=<the release of the repository's content, as X.Y.Z>
  OUT_DIR=docs/_integration/go-no-go/internal/absa-1
  PYTHON=
  ```

  `PROJECT_ID` is the label, so the artifacts name no repository. It uses lowercase letters, digits and hyphens. No
  token is needed: no script calls an API.

- **The release version.** `RELEASE_VERSION` is the release of the content the run collects, as `X.Y.Z` or `vX.Y.Z`,
  named by whoever runs it. It is not `living-doc`'s version. Every run needs it. The generator names the release
  view's files by it, `<document type>-release-vX.Y.Z.md`, and the inner view's `<document type>-inner.md`.

- **The refs.** Each component runs at its pin in
  [`tests/collector/collector-pins.env`](../../tests/collector/collector-pins.env), unless `COLLECTOR_GH_REF`,
  `TOOLKIT_REF` or `GENERATOR_MARKDOWN_REF` names a tag or a full commit SHA. Any other ref, such as a branch or a
  short SHA, is refused.
- `PYTHON` is passed to every component. On Git Bash for Windows, set `PYTHON=python` if `python3` is the Microsoft
  Store alias.

### 2. Check

```shell
bash tests/integration/local-integration.sh --check
```

The check:

- checks Python ≥ 3.10, `git`, the configuration, that each ref is a full SHA or a tag, and the target;
- clones or updates each component and the testbed in `out/` at the repository's root. A clone holds its ref's files
  only: a clone of another repository is cloned again, and untracked files are removed;
- prints every resolved ref;
- writes the collector's `.env.local` in its clone, and runs the collector's own `--check`.

It builds no venv and runs nothing else. The toolkit's and the generator's own `--check` need their input files, which
only the run writes, so in the run each one runs right before its component.

### 3. Run

```shell
bash tests/integration/local-integration.sh
```

The runner first prints every resolved ref: `living-doc`, each component, and the target. Then it runs the collector
once, and the toolkit and the generator in the inner view and then in the release view, into the folders of
[Layout](#layout). It writes the `.env.local` of its own clones only.

- **Before the chain**, it clears the paths the chain writes in the output root: `collector-gh/doc-source/`,
  `collector-gh/ui-tests/`, each view's toolkit outputs and `generator-markdown/`, the logs and `pin-report.txt`. The
  root then holds one run's files even when the run stops midway. Anything else there, such as the committed
  `env.local`, stays.
- **The `living-doc` line** leaves the output root out, so a re-run over a committed record reads the checkout as it
  is.
- **Refused output roots:** an `OUT_DIR` inside the target's checkout, or inside the runner's clones in `out/`.
- **A failure** stops the run at the first step that fails, with a non-zero exit. It names that step's log, in the
  terminal and at the end of the runner's own `local-integration.log`.
- **The pin report.** After the chain, the runner writes `pin-report.txt`, the `living-doc-utilities` pins of the
  clones that ran (`tests/examples/check_utilities_pins.py --strict`). A skew or a release candidate pin fails the run
  too. With `PIN_REPORT=warn`, those findings are warnings instead, so a trial run over components that pin a release
  candidate reaches the testbed's checks. The run's header and last line then say it is "no gate run": it can't decide
  a go/no-go.

A testbed run then checks its own output with CI's testbed checks
([tests/README.md § What the testbed checks assert](../../tests/README.md#what-the-testbed-checks-assert)). Each one
runs in its component's venv, and the first that fails stops the run:

1. the collector's invariants over `core`: `tests/testbed/check_testbed_stage.py core` over `collector-gh/`;
2. the toolkit's invariants over both views: `tests/testbed/check_testbed_toolkit_stage.py --runner`;
3. the six documents and their run reports exist under each view's `generator-markdown/`, under the names the
   generator gives them: `<document type>-inner` and `<document type>-release-v<RELEASE_VERSION>`.

- **Warnings.** Any warning in an artifact fails check 1 or 2, except
  [a test written ahead's or a skipped scenario's](../../tests/README.md#the-testbed-stage).
- **Output.** Each check's output follows a `== check:` line, in the terminal and in the runner's log.
- **Exit.** The run exits 0 only when the chain, the pin report and the three checks pass. Its last line names the
  check that failed, or says that the chain and the testbed's invariants passed.
- **Project runs** are not judged: an internal project's warnings belong to its authors
  ([Warnings on an internal target](#warnings-on-an-internal-target)).

Rules for the clones:

- Run one at a time per `living-doc` checkout. Every run shares the clones in `out/` and rewrites their `.env.local`.
- `out/` belongs to the runner. Don't link an existing checkout into it to save a clone. A linked clone is replaced by
  a fresh one, and a linked `out/components/` or `out/testbed/` stops the run, so the runner never resets or cleans a
  checkout of yours.
- Keep no git-ignored file in a target's configured folders. The collector mines it, and the `target:` line can't show
  it.

A run with an empty `OUT_DIR` writes to `out/<run-id>/`, where the run id is a UTC timestamp such as
`20261105T120000Z`. That makes a trial run that git ignores. The go/no-go names its folder in `OUT_DIR`.

### 4. Fill its row in the report

Everything the report asks for is in the run's logs and its pin report. Copy it into `go-no-go/report.md`, within the
rules in [What may be committed](#what-may-be-committed):

| Report section | From the run |
|---|---|
| 2. Targets | the runner's `target:` line in `local-integration.log` at the output root. "uncommitted changes" on any commit means the run does not count. On the target, an untracked file counts too, because the collector mines it |
| 3. Component refs | the runner's `living-doc:`, `collector-gh:`, `toolkit:`, `generator-markdown:` and `python:` lines; each component log's `living-doc-utilities:` line; `pin-report.txt` as it is |
| 4. Per artifact | the collector's and each view's toolkit log: each artifact's `stats.cardinality` block, the matrix's `summary:` block, and each output's `forwarded:` lines |
| 4. Per document | each view's generator log, per document: `input:`, `view:`, the `counts:` block, and `not_loaded` in the `render_manifest:` block |
| 4. The checks (a testbed run) | the runner's `== check:` blocks and its last line, in `local-integration.log` at the output root |
| 5. Warnings by code | each artifact's `warnings:` block, and each document's: the codes with their counts, and the first ten occurrences for the testbed only |
| 6. Duplicates | `DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` in those blocks |
| 7. Timings and sizes | each artifact's and each document's `time:` and `size:` lines |
| 9. The output reads correctly | the six documents, read by the owner |

## Release go/no-go

A release of the source-code chain goes ahead only when one testbed run passes on the exact commits it will tag. A
component tag is never cut again, so this run comes before any tag.

- **When:** after the pull request of each component's last issue in the release merges, which sets its version, and
  before any component is tagged.
- **Configuration:** [`go-no-go/testbed-core/env.local`](go-no-go/testbed-core/env.local), copied to
  `tests/integration/.env.local` once its refs are filled:
  - `TARGET=testbed` and `OUT_DIR=docs/_integration/go-no-go/testbed-core`;
  - `TESTBED_REF` is the testbed's `master`, as a full commit SHA;
  - each component ref is its candidate's full commit SHA, which is its `master` once its last issue merged. An empty
    ref runs the pin, and a tag is cut only after go, so neither is a candidate;
  - `PIN_REPORT` stays empty, so the pin report is strict;
  - `RELEASE_VERSION` names the release of the testbed's content that the run reads.
- **Baseline:** before the run, copy the committed record aside, so the run can be compared with it
  ([Compare two runs](#compare-two-runs)).
- **The run:** [Run the chain](#run-the-chain), steps 2 and 3. The testbed run's checks decide.
- **Go:** the run exits 0. Each component is then tagged at exactly the commit that passed. The release notes name the
  testbed commit that the run read.
- **No-go:** the run exits non-zero, and its last line names what failed. A defect issue goes to the component at
  fault. Its fix makes a new candidate, and a new run replaces this one.
- **The tags:** once they are cut, print each tag's commit, and check it against the commit the run read (report § 3):

  ```shell
  tag_commit() { git ls-remote --tags "https://github.com/AbsaOSS/$1" "refs/tags/$2" "refs/tags/$2^{}" | sort -k2 | tail -n1 | cut -f1; }
  for pair in living-doc-collector-gh=<tag> living-doc-toolkit=<tag> living-doc-generator-markdown=<tag>; do
    echo "${pair%%=*} ${pair#*=} $(tag_commit "${pair%%=*}" "${pair#*=}")"
  done
  ```

  Every line must name the commit the run read. A tag on any other commit was cut on something nobody checked.
- **The record:** [`go-no-go/report.md`](go-no-go/report.md), filled as in [Run the chain](#run-the-chain), step 4. Its
  "Tags cut" row holds the tag check's output. The release pin pull request files it, together with the pins
  ([CONTRIBUTING.md § Releasing the ecosystem](../../CONTRIBUTING.md#releasing-the-ecosystem)).

## Warnings on an internal target

The testbed follows the canon 100 %, so any warning over it is a defect. The go/no-go accepts none, except
[a test written ahead's or a skipped scenario's](../../tests/README.md#the-testbed-stage). An internal repository may
deviate from the canon, so its warnings don't decide the go/no-go, and its run never blocks it. Classify each code in
the report:

- **authoring**: the file itself deviates from the canon. Record the code and its count; there is nothing to fix here.
- **pipeline**: the file follows the canon, and the collector or the toolkit still reports or drops something, or the
  run crashes. This is a defect. Reduce it to a canonical example that names nothing internal, then open an issue in
  the repository at fault, `living-doc-collector-gh`, `living-doc-toolkit` or `living-doc-utilities`, with that
  example. List it in § 8 of the report.

The toolkit's own codes are classified the same way: `STALE_AC_REF`, `PLANNED_AC_HAS_TESTS`, `IN_REVIEW_AC_HAS_TESTS`.
A `FIELD_LOSS`, a `forwarded:` line whose two counts differ, or a crash is a pipeline defect on any target, as it
depends on no authoring.

If a construct can be reduced to a canonical example that the testbed lacks, it belongs in the testbed too, so the
next go/no-go sees it.

## Compare two runs

The runner clears its output paths first, so a re-run replaces the run before it. To keep the earlier run, copy its
folder aside first, for example `cp -r docs/_integration/go-no-go/internal/absa-1 out/absa-1.2026-10-15`. A target
keeps the same label in every run, so its runs line up.

The release go/no-go compares its eight artifacts and six documents with the previous release's record: the committed
`go-no-go/testbed-core/`. The run clears that folder, so copy it out of git before the run:

```shell
mkdir -p out/previous
git archive HEAD docs/_integration/go-no-go/testbed-core | tar -x -C out/previous
```

To compare two artifacts of the same target, replace the values that change with every run (timestamps, run metadata,
the commit in each permalink), and diff the rest:

```shell
N=tests/examples/normalize_snapshot.py
P=out/previous/docs/_integration/go-no-go/testbed-core
python3 "$N" < "$P/collector-gh/doc-source/doc-source.json" > old.json      # or python: see Run the chain, step 1
python3 "$N" < docs/_integration/go-no-go/testbed-core/collector-gh/doc-source/doc-source.json > new.json
diff -u old.json new.json
```

A difference is then a change in what was mined, or in the producer's version, nothing else.

- **Counts only:** set the two logs' `stats.cardinality` and `warnings:` blocks side by side.
- **A toolkit output:** compare `<view>/toolkit/…` with the same view's file in the previous record, the same way.
- **The documents and their run reports:** compare them byte for byte. They hold no timestamp, so a difference is a
  change in what was rendered, or in a version. When the release version changes, so do the release view's file
  names: compare each file with the one of the same document type and view.

## Before you commit

```shell
git -C living-doc status --short --ignored docs/_integration
```

Only `README.md`, `.gitignore`, `go-no-go/report.md` and `go-no-go/testbed-core/` may show as changed. `internal/`
and every `local-integration.log` must show as ignored (`!!`). Read the report's internal rows once more: a label, a
SHA, counts and codes, nothing else.
