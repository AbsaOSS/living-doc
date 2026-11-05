# tests

Parent: [../CONTEXT.md](../CONTEXT.md)

## Purpose

Checks over `docs/examples/` and the pinned `living-doc-collector-gh` and `living-doc-toolkit`: the static corpus check, the snapshot stage over `docs/examples/`, and the testbed stage over `AbsaOSS/living-doc-testbed`'s `core`. Also two pages checked against the installed `living-doc-utilities` (the authoring guide's before/after pairs, the error codes), and the retired-names check over this repository and the three pinned components (`docs/`). Stages, layout, the workflow diagram and the failure table: [README.md](README.md).

Not here: the agentic layer's tests, which sit next to each script in `agentic/` ([agentic/CONTEXT.md](../agentic/CONTEXT.md)).

## How it fits

- `examples-check.yml` runs `examples/examples_check.py` (the corpus, then the guide's pairs and `docs/reference/errors.md`), then pytest over `examples/` and `docs/`.
- `retired-names.yml` clones each component at its pin and runs `docs/retired_names_check.py --strict` over them and this checkout, on every PR and push to `master`.
- `real-collector.yml` runs `examples/regen-collector-snapshots.sh` (snapshot job) and `testbed/run-testbed-stage.sh` (testbed job). Both source `collector/collector-gh.sh` and `collector/toolkit.sh`, the single definitions of the pinned components, their venvs and their runs. `toolkit.sh` uses `native_dir` and `_collector_gh_venv_python` from `collector-gh.sh`, so it is sourced after it.
- Pins: the component refs only in `collector/collector-pins.env` (`COLLECTOR_GH_REF`, `TOOLKIT_REF`, `GENERATOR_MARKDOWN_REF`); the checker's `living-doc-utilities` in `examples/requirements-examples-check.txt`. `examples/check_utilities_pins.py` warns on a minor-version skew between the four (`--strict` fails). `GENERATOR_MARKDOWN_REF` is read by the pin report and the retired-names workflow only, never run.

## Conventions

- Python files are standalone scripts. Add type hints to new public functions.
- Checkers report problems as data (`examples_check.Finding`: file + rule), never through `logging`.
- Shell runners need bash 3.2+ (macOS) and run from any directory.
- CI uses Python 3.14; the collector stages need 3.10 or later.
- `examples/check_collector_stage.py` and `testbed/check_testbed_stage.py` run in the collector's venv, `examples/check_toolkit_stage.py` and `testbed/check_testbed_toolkit_stage.py` in the toolkit's, none in the checker's.
- The toolkit's venv is reused only for the same interpreter and the same `TOOLKIT_REF`, not the same `requirements.txt`: its packages are installed by path, so a new ref with the same file would keep the old code.

## Invariants and gotchas

- Deterministic: no LLM call in any checker or the normalizer. The only network access is fetching pinned inputs (each component's clone, `git ls-remote` and `requirements.txt`, `pip` from PyPI, `normalisation_cases.yaml` at the installed `living-doc-utilities` tag) and checking out the testbed. No pytest test goes online: fetchers are injected.
- The retired-names check reads tracked files only (`git ls-files`) and skips every `tests/` directory: tests quote retired names to prove they are rejected. A hit that is not a use goes into `docs/retired-names-allow.txt` with its reason; an entry that skips no hit fails the check.
- A pin bump is a reviewed change: regenerate `docs/examples/_expected/` in the same PR and keep the testbed stage green; a bump of `GENERATOR_MARKDOWN_REF` alone regenerates nothing. A move of the checker's `living-doc-utilities` version fails `examples/examples_check.py` until the before/after pairs in `docs/guides/authoring-documentation.md` and the codes in `docs/reference/errors.md` match it (root `CONTEXT.md` § Conventions).
- The testbed is read at `master`, never pinned to a SHA. Nothing about `core`'s content (counts, ids) is written here; every value comes from the checkout at run time. Any warning over `core` is a defect.
- The toolkit stage reads the collector's raw output, never `docs/examples/_expected/**`, and nothing is written under the output directory until every check passed.
- The stage only reads the testbed and fails if its `git status` changes. Never write into the testbed.
- A problem the collector must report is a derived case: a function in `testbed/testbed_cases.py` that changes a copy of `core`, finds its target by structure (never by literal text) and returns the one warning code the run must report. Never a patch file or a testbed change ([testbed/negative-cases.md](testbed/negative-cases.md)).
- A check or case that stops fitting a valid `core` is fixed here, never in the testbed.
- Mining behavior is tested by the collector stages, never by a pytest unit test.
