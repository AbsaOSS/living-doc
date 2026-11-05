# Integration runs

## Purpose

This page is for the operator who runs a gate's or a milestone's local integration runs and records them. A gate is a
checkpoint the pipeline must pass before the next stage is built on it; a milestone is one the whole chain must pass.
Each runs local integration scripts over the public testbed's `core` and, optionally, over internal repositories on a
machine that can reach them.

- The first gate, in `G1/`, checks that `living-doc-collector-gh` and `living-doc-utilities` work together on real
  data. It runs `living-doc-collector-gh`'s `local-integration.sh`.
- The second gate, in `G2/`, checks that `living-doc-toolkit` works on that data too. It runs the same script, then
  `living-doc-toolkit`'s `local-integration.sh` over the collector's fresh output.
- The first milestone, in `MS1/`, checks the whole source-code chain, from the collector to the Markdown documents in
  the inner and the release view. It runs this repository's runner,
  [`tests/integration/local-integration.sh`](../../tests/integration/local-integration.sh), which clones the three
  components and runs their `local-integration.sh` in a row: `living-doc-collector-gh`, then `living-doc-toolkit` and
  `living-doc-generator-markdown` in each view.

This folder holds each gate's and milestone's report and the data from its runs, so a later run can be compared with
this one.
**This repository is public.** A run over an internal repository keeps its configuration, its log and its artifacts
on the machine it ran on. Only its row in the report, with a label, counts and codes, may be committed.

Read before: [`living-doc-collector-gh` DEVELOPER.md](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/DEVELOPER.md),
section "Local Integration Run", and, for a gate that runs the toolkit,
[`living-doc-toolkit` DEVELOPER.md](https://github.com/AbsaOSS/living-doc-toolkit/blob/master/DEVELOPER.md#local-integration-run).
Each covers what its script needs, every `.env.local` key and what a run prints. A milestone run also renders with
[`living-doc-generator-markdown` DEVELOPER.md](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/DEVELOPER.md#local-integration-run),
and the runner's own settings are in
[`tests/integration/.env.local.example`](../../tests/integration/.env.local.example).
The CI counterpart of the testbed run is the testbed stage in [`tests/README.md`](../../tests/README.md).

## Contents

- [Layout](#layout)
- [What may be committed](#what-may-be-committed)
- [Before the first run](#before-the-first-run)
- [Run one target](#run-one-target)
- [Run a milestone target](#run-a-milestone-target)
- [Warnings on an internal target](#warnings-on-an-internal-target)
- [Compare two runs](#compare-two-runs)
- [Before you commit](#before-you-commit)

## Layout

One folder per gate or milestone, and one folder per target inside it. A target keeps the same label in every gate
and milestone, so its runs line up.

```
docs/_integration/
  README.md                      this page
  .gitignore                     keeps every internal/ folder and every log out of git
  G1/
    report.md                    the gate report: every target, internal ones redacted
    testbed-core/                the public testbed's core (required by the gate)
      env.local                  its configuration, committed
      local-integration.log      the run's output (ignored: it holds machine paths)
      collector-gh/doc-source/doc-source.json
      collector-gh/ui-tests/ui-tests.json
    internal/                    ignored as a whole
      absa-1/                    one folder per internal repository, the same files as above
      absa-2/
      absa-3/
  G2/
    report.md                    the gate report, the toolkit's outputs beside the collector's
    testbed-core/
      env.local                  the collector's configuration, committed
      toolkit.env.local          the toolkit's configuration, committed
      local-integration.log      the collector's output (ignored: it holds machine paths)
      collector-gh/doc-source/doc-source.json
      collector-gh/ui-tests/ui-tests.json
      toolkit/local-integration.log      the toolkit's output (ignored: it holds machine paths)
      toolkit/normalize-docs/generator-ready.json
      toolkit/normalize-tests/ui-test-catalog.json
      toolkit/coverage-matrix/coverage-matrix.json
    internal/                    ignored as a whole
      <label>/                   the same labels as above, the same files as `testbed-core/`
  MS1/
    report.md                    the milestone report: the chain's outputs in both views
    testbed-core/                the runner's output root for the testbed's core
      env.local                  the runner's configuration, committed
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
        generator-markdown/technical-project.md, technical-project.run-report.json
        generator-markdown/ui-test-catalog.md, ui-test-catalog.run-report.json
        generator-markdown/coverage-matrix.md, coverage-matrix.run-report.json
      release/                   the release view: the same files as inner/
    internal/                    ignored as a whole
      <label>/                   env.local and the same files as testbed-core/
```

The runner's clones of the components and the testbed live in `out/` at the repository's root, which git ignores,
never in a milestone folder.

The labels `absa-1`, `absa-2`, `absa-3` stand in for the repositories' names everywhere outside `internal/`. Which
label is which repository is written down only in each folder's `env.local`.

## What may be committed

| Item | Testbed target | Internal target |
|---|---|---|
| `env.local`, `toolkit.env.local`; a milestone's `env.local`, the copy of the runner's configuration kept with the run (the working copy, `tests/integration/.env.local`, is git-ignored) | committed | stays on the machine |
| every `local-integration.log`: the runner's, and each component's | stays on the machine | stays on the machine |
| `collector-gh/**/*.json`, `toolkit/**/*.json`, `<view>/toolkit/**/*.json` | may be committed (public content) | stays on the machine |
| `pin-report.txt` | may be committed: it names the pins and paths inside `living-doc` only | stays on the machine; it names no target, so the report may quote it whole |
| `<view>/generator-markdown/*.md`, `*.run-report.json` | may be committed (public content) | stays on the machine |
| Row in `report.md` | everything: SHA, counts, codes, each warning's first ten occurrences | label, SHA, counts, codes and their counts; **no** repository or organization name, path, entity id, AC text or warning message |

A run over an internal repository runs on a machine that can reach it. Nothing about the repository's content leaves
that machine, only its shape.

The rendered documents may be committed because a local link check over one testbed run's six documents passed
(`lychee --include-fragments`, 0 errors). The first milestone pull request that commits them confirms it in
`link-check.yml`. A run whose documents fail the link check, or `retired-names.yml`, commits its JSON only, as the
gates did, and its report says why.

## Before the first run

On the machine that runs the gate or the milestone. A milestone needs only step 1, a `living-doc` checkout and, for
an internal target, step 4: the runner clones the components and the testbed itself, at the refs its configuration
names (see [Run a milestone target](#run-a-milestone-target)). Steps 2 and 3 are for a gate's runs, one component at a
time.

1. **Tools.** Python ≥ 3.10 with its `venv` module, `git`, and bash: Linux, macOS, or Git Bash on Windows. pip must be
   able to install from PyPI or its mirror (`pip.conf`, `PIP_INDEX_URL`, a proxy); the script uses that config as it is.
2. **Checkouts, side by side** in one folder, so every relative path in an `env.local` resolves:

   ```shell
   git clone https://github.com/AbsaOSS/living-doc.git
   git clone https://github.com/AbsaOSS/living-doc-collector-gh.git
   git clone https://github.com/AbsaOSS/living-doc-toolkit.git
   git clone https://github.com/AbsaOSS/living-doc-testbed.git
   git clone <each internal repository>      # beside them, under its own name
   ```

3. **The collector and the toolkit at the gate's refs**: the `COLLECTOR_GH_REF` and `TOOLKIT_REF` that
   [`tests/collector/collector-pins.env`](../../tests/collector/collector-pins.env) pins, which are the ones CI runs.

   ```shell
   git -C living-doc-collector-gh checkout "$(sed -n 's/^COLLECTOR_GH_REF=//p' living-doc/tests/collector/collector-pins.env | tr -d '\r')"
   git -C living-doc-toolkit checkout "$(sed -n 's/^TOOLKIT_REF=//p' living-doc/tests/collector/collector-pins.env | tr -d '\r')"
   ```

4. **Each target at the commit to be read**: its default branch, up to date, with no local change
   (`git -C <target> status` clean). The run records the commit it read. The runner checks out the testbed itself:
   at `master`, or at the tag or SHA its `TESTBED_REF` names.

## Run one target

Steps for one target: `testbed-core` first, then each internal repository under its label. `<gate>` is the gate's
folder.

### 1. Find the paths (internal targets)

The collector takes a file's type from the folder list it is configured under, not from the file itself. It reads
`.ts` PageObjects only. Run these in the target's checkout, and note the folders they print:

```shell
grep -rlE --include='*.feature' 'LIVING DOC .*US-[0-9]'   . | xargs -r -n1 dirname | sort -u   # User Stories
grep -rlE --include='*.feature' 'LIVING DOC .*FUNC-[0-9]' . | xargs -r -n1 dirname | sort -u   # Functionalities
grep -rlE --include='*.ts'      'LIVING DOC .*FEAT-[0-9]' . | xargs -r -n1 dirname | sort -u   # Feature PageObjects
grep -rl  --include='*.feature' '@AC:'                    . | xargs -r -n1 dirname | sort -u   # scenarios with AC tags
```

- User Story and Functionality files must sit in separate folders, because the folder decides the type. A folder
  holding both is an authoring deviation: note it in the report and configure the folder under the type most of its
  files have.
- `DOC_SOURCE_US_PATHS` and `UI_TESTS_PATHS` are required. If a repository has no User Story file, point
  `DOC_SOURCE_US_PATHS` at a folder of the checkout that holds no `.feature` file, and note it in the report.
- A path is relative to the target's checkout and may not lead outside it. Several paths are separated by commas.
- PageObjects in another language than TypeScript are not read in this version. Note how many there are.

### 2. Write its `env.local`

The testbed's is committed: [`G1/testbed-core/env.local`](G1/testbed-core/env.local) and
[`G2/testbed-core/env.local`](G2/testbed-core/env.local). For an internal target, create
`<gate>/internal/<label>/env.local`:

```shell
PROJECT_ID=absa-1
TARGET_CHECKOUT=../<internal repository folder>
ORGANIZATION_NAME=<its GitHub organization>
REPOSITORY_NAME=<its name on the server>
DOC_SOURCE_US_PATHS=<from step 1>
DOC_SOURCE_FUNC_PATHS=<from step 1, or empty>
DOC_SOURCE_PAGES_PATHS=<from step 1, or empty>
UI_TESTS_PATHS=<from step 1>
GITHUB_SERVER_URL=<empty for github.com; the server's URL for GitHub Enterprise Server>
OUT_DIR=../living-doc/docs/_integration/<gate>/internal/absa-1
PYTHON=
```

A gate that runs the toolkit also needs a `toolkit.env.local` beside it. The testbed's is committed:
[`G2/testbed-core/toolkit.env.local`](G2/testbed-core/toolkit.env.local). For an internal target:

```shell
DOC_INPUT=../living-doc/docs/_integration/<gate>/internal/absa-1/collector-gh/doc-source/doc-source.json
TESTS_INPUT=../living-doc/docs/_integration/<gate>/internal/absa-1/collector-gh/ui-tests/ui-tests.json
VIEW=inner
OUT_DIR=../living-doc/docs/_integration/<gate>/internal/absa-1
PYTHON=
```

- `PROJECT_ID` is the label, so the artifacts name no repository. Lowercase letters, digits and hyphens.
- Relative paths resolve against the checkout of the script that reads the file. No token: neither script calls an API.
- On Git Bash for Windows, `python3` may be the Microsoft Store alias, which does not run: set `PYTHON=python`.

### 3. Check, then run

```shell
cd living-doc-collector-gh
RUN=../living-doc/docs/_integration/<gate>/internal/absa-1      # or …/<gate>/testbed-core
cp "$RUN/env.local" .env.local
./local-integration.sh --check
set -o pipefail; ./local-integration.sh 2>&1 | tee "$RUN/local-integration.log"
```

The run writes `$RUN/collector-gh/doc-source/doc-source.json` and `$RUN/collector-gh/ui-tests/ui-tests.json`,
re-reads both against their contracts and prints a report. A non-zero exit means a check, the install, the collector
or a validation failed; the log says which. A collector crash or an artifact that fails its contract is a defect,
whatever the target.

### 4. Run the toolkit over its output

For a gate that runs the toolkit, in the same shell, once the collector's run has passed:

```shell
cd ../living-doc-toolkit
cp "$RUN/toolkit.env.local" .env.local
./local-integration.sh --check
mkdir -p "$RUN/toolkit"
set -o pipefail; ./local-integration.sh 2>&1 | tee "$RUN/toolkit/local-integration.log"
```

The run writes `$RUN/toolkit/normalize-docs/generator-ready.json`, `$RUN/toolkit/normalize-tests/ui-test-catalog.json`
and `$RUN/toolkit/coverage-matrix/coverage-matrix.json`, re-reads each against its contract and prints a report. A
non-zero exit means a check, the install, a command or a validation failed; the log says which.

### 5. Fill its row in the report

Everything the report asks for is in the logs. Copy it into `<gate>/report.md`, within the rules in
[What may be committed](#what-may-be-committed):

| Report section | From the log |
|---|---|
| 2. Targets, 3. Component refs | the collector's header block: `collector:`, `living-doc-utilities:`, `python:`, `target:` (the commit read; "uncommitted changes" on any commit means the run does not count); the toolkit's: `toolkit:`, `living-doc-utilities:`, `python:` |
| 4. Per artifact | each artifact's `stats.cardinality` block; for the toolkit, also the matrix's `summary:` block and each output's `forwarded:` lines |
| 5. Warnings by code | each artifact's `warnings:` block: the codes with their counts, and the first ten occurrences for the testbed only |
| 6. Duplicates | `DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` in that block |
| 7. Timings and sizes | each artifact's `time:` and `size:` lines |

## Run a milestone target

A milestone runs the whole chain per target with one command, from the root of the `living-doc` checkout:
`testbed-core` first, then each internal repository under its label. `<milestone>` is the milestone's folder. The
runner runs each component's own `local-integration.sh`, unchanged, so a component's output and log are the ones a gate
reads.

### 1. Configure the runner

The configuration is `tests/integration/.env.local`, which git ignores. Its keys, each with a comment, are in
[`tests/integration/.env.local.example`](../../tests/integration/.env.local.example). A relative path resolves against
the `living-doc` checkout.

- **The testbed.** Its configuration is committed: [`MS1/testbed-core/env.local`](MS1/testbed-core/env.local).
  `TARGET=testbed` makes the runner clone `living-doc-testbed` at `master` and configure `core` as the CI testbed stage
  does; no internal access is needed.

  ```shell
  cp docs/_integration/<milestone>/testbed-core/env.local tests/integration/.env.local
  ```

- **An internal target.** Find its paths as in [Run one target](#run-one-target), step 1, then create
  `docs/_integration/<milestone>/internal/<label>/env.local`, and copy it the same way:

  ```shell
  TARGET=project
  PROJECT_ID=absa-1
  TARGET_CHECKOUT=../<internal repository folder>
  ORGANIZATION_NAME=<its GitHub organization>
  REPOSITORY_NAME=<its name on the server>
  DOC_SOURCE_US_PATHS=<from step 1>
  DOC_SOURCE_FUNC_PATHS=<from step 1, or empty>
  DOC_SOURCE_PAGES_PATHS=<from step 1, or empty>
  UI_TESTS_PATHS=<from step 1>
  GITHUB_SERVER_URL=<empty for github.com; the server's URL for GitHub Enterprise Server>
  OUT_DIR=docs/_integration/<milestone>/internal/absa-1
  PYTHON=
  ```

- **The refs.** Each component runs at its pin in
  [`tests/collector/collector-pins.env`](../../tests/collector/collector-pins.env) unless `COLLECTOR_GH_REF`,
  `TOOLKIT_REF` or `GENERATOR_MARKDOWN_REF` names a tag or a full commit SHA, for example a released tag. Any other
  ref, a branch or a short SHA, is refused.
- `PYTHON` is passed to every component. On Git Bash for Windows, set `PYTHON=python` if `python3` is the Microsoft
  Store alias.

### 2. Check

```shell
bash tests/integration/local-integration.sh --check
```

It checks Python ≥ 3.10, `git`, the configuration, that each ref is a full SHA or a tag, and the target, then clones or
updates each component and the testbed in `out/` at the repository's root (a clone holds its ref's files only: one of
another repository is cloned again, and untracked files are removed), prints every resolved ref, writes the
collector's `.env.local` in its clone and runs the collector's own `--check`. It builds no venv and runs nothing else.
The toolkit's and the generator's own `--check` need their input files, which only the run writes: in the run, each
runs right before its component's run.

### 3. Run

```shell
bash tests/integration/local-integration.sh
```

The runner prints every resolved ref first (`living-doc`, each component, the target), then runs the collector once,
and the toolkit and the generator in the inner and then the release view, into the folders of
[Layout](#layout). It writes the `.env.local` of its own clones only. It first clears the paths the chain writes in the
output root (`collector-gh/doc-source/`, `collector-gh/ui-tests/`, each view's toolkit outputs and
`generator-markdown/`, the logs and `pin-report.txt`), so the root holds one run's files even when the run stops
midway; anything else there, such as the committed `env.local`, stays. An `OUT_DIR` inside the target's checkout or
the runner's clones in `out/` is refused. The first step that fails stops the run with a non-zero exit and names
its log, in the terminal and at the end of the runner's own `local-integration.log`. Last, it writes `pin-report.txt`, the living-doc-utilities pins of the clones that
ran (`tests/examples/check_utilities_pins.py --strict`); a skew there fails the run too.

Run one at a time per `living-doc` checkout: every run shares the clones in `out/` and rewrites their `.env.local`.
`out/` is the runner's: don't link an existing checkout into it to save a clone. A linked clone is replaced by a fresh
one, and a linked `out/components/` or `out/testbed/` stops the run, so the runner never resets or cleans a checkout of
yours. Keep no git-ignored file in a target's configured folders either: the collector mines it, and the `target:` line
cannot show it.

A run with an empty `OUT_DIR` writes to `out/<run-id>/`, the run id a UTC timestamp such as `20261105T120000Z`: a trial
run that git ignores. A milestone run names its folder in `OUT_DIR`.

### 4. Fill its row in the report

Everything the report asks for is in the run's logs and its pin report. Copy it into `<milestone>/report.md`, within
the rules in [What may be committed](#what-may-be-committed):

| Report section | From the run |
|---|---|
| 2. Targets | the runner's `target:` line in `local-integration.log` at the output root ("uncommitted changes" on any commit means the run does not count; on the target, an untracked file counts too, as the collector mines it) |
| 3. Component refs | the runner's `living-doc:`, `collector-gh:`, `toolkit:`, `generator-markdown:` and `python:` lines; each component log's `living-doc-utilities:` line; `pin-report.txt` as it is |
| 4. Per artifact | the collector's and each view's toolkit log, as in [Run one target](#run-one-target), step 5 |
| 4. Per document | each view's generator log, per document: `input:`, `view:`, the `counts:` block and `not_loaded` in the `render_manifest:` block |
| 5. Warnings by code | each artifact's `warnings:` block, and each document's: the codes with their counts, and the first ten occurrences for the testbed only |
| 6. Duplicates | `DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` in those blocks |
| 7. Timings and sizes | each artifact's and each document's `time:` and `size:` lines |
| 9. The output reads correctly | the six documents, read by the owner |

## Warnings on an internal target

The testbed follows the canon 100 %, so any warning over it is a defect, and the gate accepts none. An internal
repository may deviate from the canon, so its warnings do not decide the gate. Its run never blocks the gate. Classify
each code in the report:

- **authoring**: the file itself deviates from the canon. Record the code and its count; nothing to fix here.
- **pipeline**: the file follows the canon and the collector or the toolkit still reports or drops something, or the
  run crashes. This is a defect. Reduce it to a canonical example that names nothing internal, then open an issue in
  the repository at fault, `living-doc-collector-gh`, `living-doc-toolkit` or `living-doc-utilities`, with that
  example. List it in § 8 of the report.

The toolkit's own codes are classified the same way: `STALE_AC_REF`, `PLANNED_AC_HAS_TESTS`, `IN_REVIEW_AC_HAS_TESTS`.
A `FIELD_LOSS`, a `forwarded:` line whose two counts differ or a crash is a pipeline defect on any target, as it depends
on no authoring.

If a construct can be reduced to a canonical example the testbed lacks, it belongs in the testbed too, so later
gates see it.

## Compare two runs

A re-run writes into the same `collector-gh/` folder, and also overwrites `toolkit/`; a milestone re-run clears
each view's folders too. To keep the earlier run, rename its folder first, for example
`mv internal/absa-1 internal/absa-1.2026-10-15`. Later gates and milestones use the same labels
(`G2/internal/absa-1`, `MS1/internal/absa-1`), so a target's runs line up.

A gate compares its collector artifacts with the previous gate's `testbed-core/`. A milestone compares its collector
artifacts and its inner view's toolkit outputs with the toolkit's baseline, `G2/testbed-core/`: G2 ran the inner view
only, so the release view's outputs and the documents are first recorded by the first milestone. To compare two
artifacts of the same target, replace the values that change with every run (timestamps, run
metadata, the commit in each permalink) and diff the rest:

```shell
N=living-doc/tests/examples/normalize_snapshot.py
python3 "$N" < <old>/collector-gh/doc-source/doc-source.json > old.json      # or python: see Run one target, step 2
python3 "$N" < <new>/collector-gh/doc-source/doc-source.json > new.json
diff -u old.json new.json
```

A difference is then a change in what was mined or in the producer's version, nothing else. For counts only, set the
two logs' `stats.cardinality` and `warnings:` blocks side by side. For a toolkit output, the inner view's, compare
`<new>/inner/toolkit/…` with `G2/testbed-core/toolkit/…` the same way.

## Before you commit

```shell
git -C living-doc status --short --ignored docs/_integration
```

Only `README.md`, `.gitignore`, `<gate>/report.md` and `<gate>/testbed-core/` may show as changed, or the same
under `<milestone>/`. `internal/` and every `local-integration.log` must show as ignored (`!!`). Read the report's internal rows once more: a label, a SHA,
counts and codes, nothing else.
