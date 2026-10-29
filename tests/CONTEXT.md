# tests

Parent: [../CONTEXT.md](../CONTEXT.md)

## Purpose

Checks over `docs/examples/` and the pinned `living-doc-collector-gh`: the static corpus check, the snapshot stage over `docs/examples/`, and the testbed stage over `AbsaOSS/living-doc-testbed`'s `core`. Stages, layout, the workflow diagram and the failure table: [README.md](README.md).

Not here: the agentic layer's tests, which sit next to each script in `agentic/` ([agentic/CONTEXT.md](../agentic/CONTEXT.md)).

## How it fits

- `examples-check.yml` runs `examples/examples_check.py`, then pytest over `examples/`.
- `real-collector.yml` runs `examples/regen-collector-snapshots.sh` (snapshot job) and `testbed/run-testbed-stage.sh` (testbed job). Both source `collector/collector-gh.sh`, the single definition of the pinned collector, its venv and its run.
- Pins: the collector ref only in `collector/collector-pins.env` (`COLLECTOR_GH_REF`); the checker's `living-doc-utilities` in `examples/requirements-examples-check.txt`. `examples/check_utilities_pins.py` warns on a minor-version skew between the two (`--strict` fails).

## Conventions

- Python files are standalone scripts. Add type hints to new public functions.
- Checkers report problems as data (`examples_check.Finding`: file + rule), never through `logging`.
- Shell runners need bash 3.2+ (macOS) and run from any directory.
- CI uses Python 3.14; the collector stages need 3.10 or later.
- `examples/check_collector_stage.py` and `testbed/check_testbed_stage.py` run in the collector's venv, not the checker's.

## Invariants and gotchas

- Deterministic and offline: no LLM call and no network request in any checker or the normalizer. The only network access is fetching the pinned collector (clone, `git ls-remote`, its `requirements.txt`, `pip` from PyPI) and checking out the testbed.
- A pin bump is a reviewed change: regenerate `docs/examples/_expected/` in the same PR and keep the testbed stage green.
- The testbed is read at `master`, never pinned to a SHA. Nothing about `core`'s content (counts, ids) is written here; every value comes from the checkout at run time. Any warning over `core` is a defect.
- The stage only reads the testbed and fails if its `git status` changes. Never write into the testbed.
- A problem the pipeline must report is a derived case: a function in `testbed/testbed_cases.py` that changes a copy of `core`, finds its target by structure (never by literal text) and returns the one warning code the run must report. Never a patch file or a testbed change ([testbed/negative-cases.md](testbed/negative-cases.md)).
- A check or case that stops fitting a valid `core` is fixed here, never in the testbed.
- Mining behavior is tested by the collector stages, never by a pytest unit test.
