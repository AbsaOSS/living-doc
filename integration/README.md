# Integration tests

## Purpose

This page is for contributors who run, debug or extend the integration tests. Both run the pinned
`living-doc-collector-gh` for real and check what it mines.

Read before: [CONTRIBUTING.md § Regenerating the collector snapshots](../CONTRIBUTING.md#regenerating-the-collector-snapshots)
and [§ The collector stage over the testbed](../CONTRIBUTING.md#the-collector-stage-over-the-testbed).
Next: [Negative testbed cases](negative-cases.md).

## Contents

- [Stages](#stages)
- [The workflow](#the-workflow)
- [Layout](#layout)
- [The testbed stage](#the-testbed-stage)
- [What a testbed run does](#what-a-testbed-run-does)
- [What the testbed checks assert](#what-the-testbed-checks-assert)
- [Run the testbed stage](#run-the-testbed-stage)
- [Read a testbed failure](#read-a-testbed-failure)

## Stages

Both are jobs of [`.github/workflows/real-collector-snapshot.yml`](../.github/workflows/real-collector-snapshot.yml).
They run the same collector, in the same venv.

| Stage | CI job | Mines | Asserts |
|---|---|---|---|
| snapshot | `real-collector-snapshot` | `docs/examples/` | the corpus's first-stage content, then no diff against `docs/examples/_expected/` |
| testbed | `testbed-collector-stage` | the testbed's `core` | invariants, then exactly one warning per derived case |

The snapshot stage's procedure (regenerate, commit, bump the pin) is in
[CONTRIBUTING.md § Regenerating the collector snapshots](../CONTRIBUTING.md#regenerating-the-collector-snapshots).
The rest of this page is the testbed stage.

## The workflow

The workflow is the integration test: two independent jobs, one pinned collector.
Either job failing fails the run. A new push to the same ref cancels the run in progress.

```mermaid
flowchart TB
    trigger(["push to master or pull request touching docs/examples/**, integration/**,<br/>the root tools/requirements-examples-check.txt or the workflow · manual dispatch · no schedule"])
    pin[("tools/collector-snapshot-pins.env<br/>COLLECTOR_GH_REF")]
    setup[["collector-gh.sh · collector_gh_setup<br/>clone the pinned collector, build its venv"]]

    subgraph snapshot["job real-collector-snapshot · mines docs/examples/"]
        direction TB
        a1["check out living-doc · Python 3.14"]
        a2["tools/check_utilities_pins.py<br/>report the living-doc-utilities pins"]
        subgraph regen["regen-collector-snapshots.sh"]
            direction TB
            a3["mine docs/examples/<br/>doc-source + ui-tests"]
            a4["tools/check_collector_stage.py<br/>validate, assert the first-stage content"]
            a5["tools/normalize_snapshot.py<br/>placeholders for volatile values"]
            a3 --> a4 --> a5
        end
        a6{"diff -ru against<br/>docs/examples/_expected/"}
        a1 --> a2 --> a3
        a5 --> a6
    end

    subgraph testbed["job testbed-collector-stage · mines the testbed's core"]
        direction TB
        b1["check out living-doc, and living-doc-testbed<br/>at master · Python 3.14"]
        subgraph stage["run-testbed-stage.sh"]
            direction TB
            b2["record the testbed's git status"]
            b3["mine projects/core<br/>doc-source + ui-tests"]
            b4["tools/check_testbed_stage.py core<br/>the invariants, no warning"]
            b5["each case in testbed_cases.py:<br/>copy core, apply the case, git init,<br/>mine doc-source"]
            b6["tools/check_testbed_stage.py case<br/>exactly one warning, at its line"]
            b7{"testbed's git status<br/>unchanged?"}
            b2 --> b3 --> b4 --> b5 --> b6
            b6 -.->|next case| b5
            b6 --> b7
        end
        b1 --> b2
    end

    trigger --> snapshot
    trigger --> testbed
    pin -.-> setup
    setup -.-> a3
    setup -.-> b3
    a6 -->|no diff| passA(["green"])
    a6 -->|diff| failA(["red: regenerate docs/examples/_expected/"])
    b7 -->|yes, and no check failed| passB(["green"])
    b7 -->|no, or a run, case or check failed| failB(["red"])
```

Only each job's last decision is drawn. In the snapshot job, an earlier red step stops the job.
The testbed job's failure handling is in [What a testbed run does](#what-a-testbed-run-does).
Its case steps are on [Negative testbed cases](negative-cases.md).

## Layout

The shell scripts, the cases and the docs sit in this folder; the checkers, the other Python and the pin
file sit in [`tools/`](tools/).

| File | Stage | Holds |
|---|---|---|
| [`regen-collector-snapshots.sh`](regen-collector-snapshots.sh) | snapshot | the runner; writes `docs/examples/_expected/` or a directory to diff against it |
| [`run-testbed-stage.sh`](run-testbed-stage.sh) | testbed | the runner, and the testbed's collector paths and `project-id` |
| [`collector-gh.sh`](collector-gh.sh) | both | the pinned collector, its venv and its run; both runners source it |
| [`testbed_cases.py`](testbed_cases.py) | testbed | the derived problem cases, one function each |
| [`negative-cases.md`](negative-cases.md) | testbed | those cases: each one, how its run is checked, how to add one |
| [`tools/collector-snapshot-pins.env`](tools/collector-snapshot-pins.env) | both | the collector pin, `COLLECTOR_GH_REF` |
| [`tools/check_utilities_pins.py`](tools/check_utilities_pins.py) | snapshot | the `living-doc-utilities` pin report; the CI job runs it first |
| [`tools/check_collector_stage.py`](tools/check_collector_stage.py) | snapshot | the corpus's first-stage content |
| [`tools/normalize_snapshot.py`](tools/normalize_snapshot.py) | snapshot | replaces volatile values with placeholders before the diff |
| [`tools/check_testbed_stage.py`](tools/check_testbed_stage.py) | testbed | the invariants over `core`, and the check for one case |
| [`tools/test_check_utilities_pins.py`](tools/test_check_utilities_pins.py) | — | the pin report's tests; `examples-check.yml` runs them, since that job has `pytest` |

Nothing here depends on the repository's root `tools/`, except one file:
the pin report compares the collector's pin with `tools/requirements-examples-check.txt`.

## The testbed stage

The stage reads the `core` project of
[`AbsaOSS/living-doc-testbed`](https://github.com/AbsaOSS/living-doc-testbed) at its `master`.
`core` follows the canon 100 %, so any warning over it is a defect.
Nothing about `core`'s content is written down here: every count comes from the checkout at run time.
The problems the pipeline must report are [negative cases](negative-cases.md).
The stage only reads the testbed, and fails if it leaves the checkout changed.

## What a testbed run does

1. Clones the pinned collector and builds or reuses its venv → `collector-gh.sh::collector_gh_setup`.
2. Shallow-clones the testbed's `master`, or reads the checkout passed as the first argument.
3. Records the checkout's full `git status`, ignored and untracked files included → `run-testbed-stage.sh::testbed_status`.
4. Mines `projects/core` with `doc-source` and `ui-tests` → `run-testbed-stage.sh::mine`.
5. Asserts the invariants over that output → `tools/check_testbed_stage.py::check_core`.
6. For each case: copies `core`, applies the case, makes the copy a git checkout, mines it with
   `doc-source` only, and asserts the one expected warning → `tools/check_testbed_stage.py::check_case`.
   The details: [Negative testbed cases § How a case run is checked](negative-cases.md#how-a-case-run-is-checked).
7. Fails if the testbed's `git status` differs from step 3.

A failed collector run, case or check marks the stage failed and moves on to the next.
A failed setup step (listing the cases, copying `core`, making the git checkout) stops the stage at once.
All output lives in a temp work dir, deleted on exit.

## What the testbed checks assert

The full list is the module docstring of [`tools/check_testbed_stage.py`](tools/check_testbed_stage.py).
Where each part is checked:

- Every artifact validates against its contract; `sources_failed` is 0 → `check_testbed_stage.py::_read`.
- No warning at all, in either artifact → `check_testbed_stage.py::check_core`.
- Entities, their ACs, Feature states, pages, AC variants, no entity from a file outside the living-doc
  folders → `check_testbed_stage.py::check_doc_source`.
- Scenarios, AC links, tag parameters, no AC link from a file outside the living-doc folders
  → `check_testbed_stage.py::check_ui_tests`.
- `core` holds at least one of each construct, so no check passes on nothing → `check_testbed_stage.py::check_core`.
- A case run's one warning → `check_testbed_stage.py::check_case`.

## Run the testbed stage

From the repository root (the script itself runs from any directory):

```shell
integration/run-testbed-stage.sh                         # shallow-clones the testbed's master
integration/run-testbed-stage.sh ../living-doc-testbed   # reads a checkout you already have
```

It needs bash 3.2 or later (Linux, macOS, or Git Bash on Windows), `git`, and access to github.com.
Python, the venv and the token-free run are the same as for the snapshot stage: see
[CONTRIBUTING.md § Regenerating the collector snapshots](../CONTRIBUTING.md#regenerating-the-collector-snapshots).

Options, both environment variables:

- `PYTHON` — the interpreter the collector's venv is built from.
- `GITHUB_STEP_SUMMARY` — set in CI; the testbed SHA and each check's output are appended to it.

In CI, a testbed merge triggers nothing here. Dispatch the workflow by hand to read a new testbed `master`.

To apply one case by hand, or to add one: [Negative testbed cases](negative-cases.md).

## Read a testbed failure

| Output | Meaning | Fix in |
|---|---|---|
| `FAIL doc-source: …` or `FAIL ui-tests: …` under `testbed core: N invariant(s) failed` | the collector mined `core` wrongly, or `core` left the canon | the collector or `living-doc-utilities` (an issue there); or the testbed |
| `nothing to assert: the checkout has no …` | `core` no longer holds a construct a check needs | the testbed, or the check here if the construct was dropped on purpose |
| `ERROR: case … could not be applied` | the case found no target in `core` | the case here |
| `FAIL doc-source: expected exactly one warning, …` | a case run reported other warnings, or none | the case here, or the collector |
| `ERROR: the collector failed over …` | the collector exited non-zero | the collector, or the pin in `tools/collector-snapshot-pins.env` |
| `ERROR: the stage changed the testbed checkout …` | something wrote into the testbed | the runner or the collector's output paths |

A check or a case here can also stop fitting a valid `core`. Then fix the check or the case, never the testbed.
