# Negative testbed cases

## Purpose

This page is for contributors who read, run or add a negative case of the testbed stage.
A negative case breaks one thing in a copy of the testbed's `core` and names the one warning the run must report.
The code calls it a derived problem case.

Read before: [Integration tests § The testbed stage](README.md#the-testbed-stage).
Next: [Integration tests § Read a testbed failure](README.md#read-a-testbed-failure).

## Contents

- [Principle](#principle)
- [Cases](#cases)
- [How a case run is checked](#how-a-case-run-is-checked)
- [What a case cannot cover](#what-a-case-cannot-cover)
- [Apply a case by hand](#apply-a-case-by-hand)
- [Add a case](#add-a-case)

## Principle

The run over `core` reports nothing: that proves the collector accepts the canon.
A negative case proves the other half: a known defect is reported once, at its line.
The defect is never authored in the testbed. A function here derives it from a copy.
The function finds its target by structure, so a testbed merge does not break it.

## Cases

One row per case in [`testbed_cases.py`](testbed_cases.py), in run order.
The function's docstring is the full definition.

| Case | Reports | What it proves |
|---|---|---|
| `misindented_ac_line` | `MISINDENTED_LINE` | an AC line that fits no indent level is reported at its line, with no other warning |

`python integration/testbed_cases.py --list` prints the names the runner uses.

### `misindented_ac_line`

- **Target:** in the first Functionality file that has one, the first AC block whose last line is a bullet
  at the block's content level, other than its first bullet.
- **Change:** that line loses one space of indent.
- **Reports:** `MISINDENTED_LINE` at that line, and no other warning.
- **Why that target:** the docstring of [`misindented_ac_line`](testbed_cases.py).
- **No target:** `LookupError`, and the stage fails with `ERROR: case misindented_ac_line could not be applied`.

The shape of the change, in placeholders; the real target is found at run time:

```text
#   AC:<id> (…)
#     - <the criterion's text>
#     - <its last bullet>        before: at the content level
#    - <its last bullet>         after: one space less, fits no level
```

## How a case run is checked

- Each case gets a fresh copy of `core` in the work dir, so no case sees another's change
  → `run-testbed-stage.sh`, the case loop.
- The copy is a git checkout with the testbed as `origin`: a file outside one is reported `NO_SOURCE_URL`
  → `run-testbed-stage.sh`, the case loop.
- The copy is mined with `doc-source` only → `run-testbed-stage.sh::mine`.
- The artifact validates against its contract, and `sources_failed` is 0 → `tools/check_testbed_stage.py::_read`.
- The run reports exactly one warning: the case's code, at its line, in the changed file
  → `tools/check_testbed_stage.py::check_case`.
- Nothing else is asserted: what a case breaks can leave other data dangling, so the `core` invariants
  do not apply → `tools/check_testbed_stage.py::check_case`.

## What a case cannot cover

- A warning only `ui-tests` reports: a case run mines `doc-source` alone, and the check reads only that artifact.
- `NO_SOURCE_URL`: every copy is a git checkout.
- A code a later stage raises, such as the toolkit's: the stage runs the collector only.
- A defect that needs two changes, or a change that makes a later line report too: the run must report
  exactly one warning.

## Apply a case by hand

A case changes the folder it is given, in place, so copy `core` first:

```shell
rm -rf /tmp/case && mkdir -p /tmp/case/projects
cp -R ../living-doc-testbed/projects/core /tmp/case/projects/core
python integration/testbed_cases.py misindented_ac_line /tmp/case/projects/core
# MISINDENTED_LINE  <line>  /tmp/case/projects/core/…/<file>.feature  line <line> dedented by one space: …
```

Never pass the testbed checkout itself.

## Add a case

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
9. Add a row to [Cases](#cases), and a section under it: target, change, report, why exactly one, no target.
10. Run `integration/run-testbed-stage.sh` against a local testbed checkout.

Never add a patch file, and never change the testbed to make a case fit.
