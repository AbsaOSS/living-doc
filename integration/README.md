# Integration tests

## Purpose

This page is for contributors who run, debug or extend the integration tests. Both run the pinned
`living-doc-collector-gh` for real and check what it mines.

Read before: [CONTRIBUTING.md § Regenerating the collector snapshots](../CONTRIBUTING.md#regenerating-the-collector-snapshots)
and [§ The collector stage over the testbed](../CONTRIBUTING.md#the-collector-stage-over-the-testbed).

## Contents

- [Stages](#stages)
- [Layout](#layout)
- [The testbed stage](#the-testbed-stage)
- [Cases](#cases)
- [What a testbed run does](#what-a-testbed-run-does)
- [What the testbed checks assert](#what-the-testbed-checks-assert)
- [Run the testbed stage](#run-the-testbed-stage)
- [Add a problem case](#add-a-problem-case)
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

## Layout

The shell scripts sit in this folder; the Python and the pin file they use sit in [`tools/`](tools/).

| File | Stage | Holds |
|---|---|---|
| [`regen-collector-snapshots.sh`](regen-collector-snapshots.sh) | snapshot | the runner; writes `docs/examples/_expected/` or a directory to diff against it |
| [`run-testbed-stage.sh`](run-testbed-stage.sh) | testbed | the runner, and the testbed's collector paths and `project-id` |
| [`collector-gh.sh`](collector-gh.sh) | both | the pinned collector, its venv and its run; both runners source it |
| [`testbed_cases.py`](testbed_cases.py) | testbed | the derived problem cases, one function each |
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
A problem the pipeline must report is never authored in the testbed. It is derived here, from a copy.
The stage only reads the testbed, and fails if it leaves the checkout changed.

## Cases

Each case changes one thing in a copy of `core` and must make the run report exactly one warning.
The function's docstring is the full definition.

| Case | Reports | What it changes | What it proves |
|---|---|---|---|
| [`misindented_ac_line`](testbed_cases.py) | `MISINDENTED_LINE` | dedents, by one space, the last bullet of a multi-line AC block in the first Functionality file that has one | an AC line that fits no indent level is reported at its line and dropped, with no other warning |

`python integration/testbed_cases.py --list` prints the names the runner uses.

## What a testbed run does

1. Clones the pinned collector and builds or reuses its venv → `collector-gh.sh::collector_gh_setup`.
2. Shallow-clones the testbed's `master`, or reads the checkout passed as the first argument.
3. Records the checkout's full `git status`, ignored and untracked files included → `run-testbed-stage.sh::testbed_status`.
4. Mines `projects/core` with `doc-source` and `ui-tests` → `run-testbed-stage.sh::mine`.
5. Asserts the invariants over that output → `tools/check_testbed_stage.py::check_core`.
6. For each case: copies `core`, applies the case, makes the copy a git checkout, mines it with
   `doc-source` only, and asserts the one expected warning → `tools/check_testbed_stage.py::check_case`.
7. Fails if the testbed's `git status` differs from step 3.

A failed collector run or check marks the stage failed and moves on, so step 7 always runs.
All output lives in a temp work dir, deleted on exit.
The case copy is a git checkout because a file outside one is reported `NO_SOURCE_URL`.

## What the testbed checks assert

The full list is the module docstring of [`tools/check_testbed_stage.py`](tools/check_testbed_stage.py).
Where each part is checked:

- Every artifact validates against its contract; `sources_failed` is 0 → `check_testbed_stage.py::_read`.
- No warning at all, in either artifact → `check_testbed_stage.py::check_core`.
- Entities, their ACs, Feature states, pages and AC variants → `check_testbed_stage.py::check_doc_source`.
- Scenarios, AC links, tag parameters, files outside the living-doc folders → `check_testbed_stage.py::check_ui_tests`.
- `core` holds at least one of each construct, so no check passes on nothing → `check_testbed_stage.py::check_core`.
- A case run reports exactly one warning: its code, at its line, in its file → `check_testbed_stage.py::check_case`.

A case run is not held to the `core` invariants: what a case breaks can leave other data dangling.

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

To apply one case by hand, copy `core` first. A case changes the folder it is given, in place:

```shell
mkdir -p /tmp/case/projects
cp -R ../living-doc-testbed/projects/core /tmp/case/projects/core
python integration/testbed_cases.py misindented_ac_line /tmp/case/projects/core
# MISINDENTED_LINE  17  /tmp/case/projects/core/tests/e2e/features/liv_doc_func/func-001-….feature  line 17 dedented …
```

Never pass the testbed checkout itself.

## Add a problem case

Add a case only when a warning needs a real-looking project to show it.

1. Write a function in [`testbed_cases.py`](testbed_cases.py) that takes the path to a copy of `core`
   and returns `Expected`.
2. Find the target by structure, never by literal text or a line number. Reuse `_functionality_files`
   and `_ac_blocks` where they fit.
3. Change one thing, so the run reports exactly one warning. Pick a target where no later line is
   reported with it.
4. Keep line endings: open the file with `newline=""`, as `misindented_ac_line` does.
5. Return `Expected(code, line, path, change)`: the warning code, the 1-based line, the changed file,
   and a short note for the log.
6. Raise `LookupError` when `core` has no target, so the stage fails loudly.
7. Add the function to the tuple behind `CASES`. Its name is the case name.
8. In the docstring, say what the case changes and why that yields exactly one warning.
9. Add a row to [Cases](#cases).
10. Run `integration/run-testbed-stage.sh` against a local testbed checkout.

Never add a patch file, and never change the testbed to make a case fit.

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
In CI, the job summary names the testbed SHA the run read.
