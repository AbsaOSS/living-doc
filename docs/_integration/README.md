# Integration runs

## Purpose

This page is for the operator who runs a gate's local integration runs and records them. A gate is a checkpoint the
pipeline must pass before the next stage is built on it. G1 checks that `living-doc-collector-gh` and
`living-doc-utilities` work together on real data. Its local run is `living-doc-collector-gh`'s
`local-integration.sh`, run over the public testbed's `core` and, optionally, over internal repositories on a
machine that can reach them.

This folder holds each gate's report and the data from its runs, so a later run can be compared with this one.
**This repository is public.** A run over an internal repository keeps its configuration, its log and its artifacts
on the machine it ran on. Only its row in the report, with a label, counts and codes, may be committed.

Read before: [`living-doc-collector-gh` DEVELOPER.md](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/DEVELOPER.md),
section "Local Integration Run", which covers what the script needs, every `.env.local` key and what a run prints.
The CI counterpart of the testbed run is the testbed stage in [`tests/README.md`](../../tests/README.md).

## Contents

- [Layout](#layout)
- [What may be committed](#what-may-be-committed)
- [Before the first run](#before-the-first-run)
- [Run one target](#run-one-target)
- [Warnings on an internal target](#warnings-on-an-internal-target)
- [Compare two runs](#compare-two-runs)
- [Before you commit](#before-you-commit)

## Layout

One folder per gate, and one folder per target inside it. A target keeps the same label in every gate, so its runs
line up.

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
```

The labels `absa-1`, `absa-2`, `absa-3` stand in for the repositories' names everywhere outside `internal/`. Which
label is which repository is written down only in each folder's `env.local`.

## What may be committed

| Item | Testbed target | Internal target |
|---|---|---|
| `env.local` | committed | stays on the machine |
| `local-integration.log` | stays on the machine | stays on the machine |
| `collector-gh/**/*.json` | may be committed (public content) | stays on the machine |
| Row in `report.md` | everything: SHA, counts, codes, each warning's first ten occurrences | label, SHA, counts, codes and their counts; **no** repository or organization name, path, entity id, AC text or warning message |

A run over an internal repository runs on a machine that can reach it. Nothing about the repository's content leaves
that machine, only its shape.

## Before the first run

On the machine that runs the gate:

1. **Tools.** Python ≥ 3.10 with its `venv` module, `git`, and bash: Linux, macOS, or Git Bash on Windows. pip must be
   able to install from PyPI or its mirror (`pip.conf`, `PIP_INDEX_URL`, a proxy); the script uses that config as it is.
2. **Checkouts, side by side** in one folder, so every relative path in an `env.local` resolves:

   ```shell
   git clone https://github.com/AbsaOSS/living-doc.git
   git clone https://github.com/AbsaOSS/living-doc-collector-gh.git
   git clone https://github.com/AbsaOSS/living-doc-testbed.git
   git clone <each internal repository>      # beside them, under its own name
   ```

3. **The collector at the gate's ref**: the `COLLECTOR_GH_REF` that
   [`tests/collector/collector-pins.env`](../../tests/collector/collector-pins.env) pins, which is the collector CI
   runs.

   ```shell
   git -C living-doc-collector-gh checkout "$(sed -n 's/^COLLECTOR_GH_REF=//p' living-doc/tests/collector/collector-pins.env | tr -d '\r')"
   ```

4. **Each target at the commit to be read**: its default branch, up to date, with no local change
   (`git -C <target> status` clean). The run records the commit it read.

## Run one target

Steps for one target: `testbed-core` first, then each internal repository under its label.

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

The testbed's is committed: [`G1/testbed-core/env.local`](G1/testbed-core/env.local). For an internal target,
create `G1/internal/<label>/env.local`:

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
OUT_DIR=../living-doc/docs/_integration/G1/internal/absa-1
PYTHON=
```

- `PROJECT_ID` is the label, so the artifacts name no repository. Lowercase letters, digits and hyphens.
- Relative paths resolve against the collector's checkout. No token: neither mode calls an API.

### 3. Check, then run

```shell
cd living-doc-collector-gh
RUN=../living-doc/docs/_integration/G1/internal/absa-1      # or …/G1/testbed-core
cp "$RUN/env.local" .env.local
./local-integration.sh --check
set -o pipefail; ./local-integration.sh 2>&1 | tee "$RUN/local-integration.log"
```

The run writes `$RUN/collector-gh/doc-source/doc-source.json` and `$RUN/collector-gh/ui-tests/ui-tests.json`,
re-reads both against their contracts and prints a report. A non-zero exit means a check, the install, the collector
or a validation failed; the log says which. A collector crash or an artifact that fails its contract is a defect,
whatever the target.

### 4. Fill its row in the report

Everything the report asks for is in the log. Copy it into [`G1/report.md`](G1/report.md), within the rules in
[What may be committed](#what-may-be-committed):

| Report section | From the log |
|---|---|
| 2. Targets, 3. Component refs | the header block: `collector:`, `living-doc-utilities:`, `python:`, `target:` (the commit read; "uncommitted changes" means the run does not count) |
| 4. Per artifact | each artifact's `stats.cardinality` block |
| 5. Warnings by code | each artifact's `warnings:` block: the codes with their counts, and the first ten occurrences for the testbed only |
| 6. Duplicates | `DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID` in that block |
| 7. Timings and sizes | each artifact's `time:` and `size:` lines |

## Warnings on an internal target

The testbed follows the canon 100 %, so any warning over it is a defect, and G1 accepts none. An internal
repository may deviate from the canon, so its warnings do not decide the gate. Its run never blocks G1. Classify
each code in the report:

- **authoring**: the file itself deviates from the canon. Record the code and its count; nothing to fix here.
- **pipeline**: the file follows the canon and the collector still reports or drops something, or the run crashes.
  This is a defect. Reduce it to a canonical example that names nothing internal, then open an issue in
  `living-doc-collector-gh` or `living-doc-utilities` with that example. List it in § 8 of the report.

If a construct can be reduced to a canonical example the testbed lacks, it belongs in the testbed too, so later
gates see it.

## Compare two runs

A re-run writes into the same `collector-gh/` folder. To keep the earlier run, rename its folder first, for example
`mv internal/absa-1 internal/absa-1.2026-10-15`. Later gates use the same labels (`G2/internal/absa-1`), so a
target's runs line up across gates.

To compare two artifacts of the same target, replace the values that change with every run (timestamps, run
metadata, the commit in each permalink) and diff the rest:

```shell
N=living-doc/tests/examples/normalize_snapshot.py
python "$N" < <old>/collector-gh/doc-source/doc-source.json > old.json
python "$N" < <new>/collector-gh/doc-source/doc-source.json > new.json
diff -u old.json new.json
```

A difference is then a change in what was mined or in the producer's version, nothing else. For counts only, set the
two logs' `stats.cardinality` and `warnings:` blocks side by side.

## Before you commit

```shell
git -C living-doc status --short --ignored docs/_integration
```

Only `README.md`, `.gitignore`, `<gate>/report.md` and `<gate>/testbed-core/` may show as changed. `internal/` and
every `local-integration.log` must show as ignored (`!!`). Read the report's internal rows once more: a label, a SHA,
counts and codes, nothing else.
