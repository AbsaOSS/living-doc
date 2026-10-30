# How to Contribute?

## **Identifying and Reporting Bugs**

* **Ensure the bug has not already been reported** by searching our **[GitHub Issues](https://github.com/AbsaOSS/living-doc/issues)**.
* If you cannot find an open issue describing the problem, use the **Bug Report** GitHub issue template to open a new one.

## **Proposing New Features**

* **Check if the feature has already been requested** by searching through our **[GitHub Issues](https://github.com/AbsaOSS/living-doc/issues)**.
* If the feature request doesn't exist, feel free to create a new one, using the **Feature Request** GitHub issue template.

## Branch Naming

Branches have to start with one of the allowed prefixes — `feature/`, `fix/`, `docs/`, `chore/` — followed immediately by the related issue number, then a short kebab-case scope: `<prefix>/<issue>-<scope>`.
Examples:
- `feature/128-add-hierarchy-support`
- `fix/567-handle-empty-chapter`
- `docs/203-improve-contribution-guide`
- `chore/91-update-ci-python-version`

Rename if needed before pushing:
```shell
git branch -m fix/<issue>-<new-name>
```
Use lowercase **kebab-case** and reflect actual scope. The issue number is required — CI (`check-pr-requirements`) rejects a branch without one.

## PR Naming

PR titles have to carry the related issue number, using one of these formats: `#123: Title` or `123 - Title`.
Examples:
- `#567: Handle empty chapter`
- `123 - Improve contribution guide`

## PR Description

PR body has to also include these sections: `## Overview`, `## Release Notes`, `## Related`.
- **Overview** – what changed and why.
- **Release Notes** – short, user-facing summary for the changelog.
- **Related** – link the issue with a closing keyword, e.g. `Closes #123` or `Fixes AB#12345`.

## Regenerating the collector snapshots

`.github/workflows/real-collector.yml` runs the real `living-doc-collector-gh` (`doc-source` +
`ui-tests`) over `docs/examples/`, then the real `living-doc-toolkit` over what it mined, and checks the
output twice:

1. `tests/examples/check_collector_stage.py` and `tests/examples/check_toolkit_stage.py` validate each
   raw artifact against its contract and assert its content against values written in the script. The
   toolkit's check also runs two documentation files through its CLI and asserts the failure.
2. The normalized output is diffed against `docs/examples/_expected/collector-gh/` and
   `docs/examples/_expected/toolkit/`. Any diff fails the job, and so does a file under
   `docs/examples/_expected/` the job no longer writes.

Only this diff reads `docs/examples/_expected/`; `examples-check.yml` and the testbed stage do not.

Regenerate and commit the expected files **in the same PR** whenever either side moves:

```shell
tests/examples/regen-collector-snapshots.sh     # writes docs/examples/_expected/{collector-gh,toolkit}/
git add docs/examples/_expected
```

The script writes nothing until every check has passed. No token is needed. It needs Python 3.10 or
later (`python3`, else `python`, or the interpreter `PYTHON` names) and builds two venvs (gitignored),
each from that component's runtime `requirements.txt` at its pinned ref, and from nothing else:

- `.snapshot-venvs/collector-gh/`, reused while the interpreter and the pinned `requirements.txt` stay
  the same.
- `.snapshot-venvs/toolkit/`, reused while the interpreter and `TOOLKIT_REF` stay the same: the toolkit's
  packages are installed by path, so a new ref with the same `requirements.txt` still needs a new venv.

The `collector-gh` and `toolkit` pins live only in `tests/collector/collector-pins.env`. A pin bump is a
reviewed change, like a dependency bump: change the ref and commit the regenerated snapshots in the same
PR. `python tests/examples/check_utilities_pins.py` prints the `living-doc-utilities` version pinned by
the collector, the toolkit and the corpus checker (`tests/examples/requirements-examples-check.txt`) and
warns on a minor-version skew; `--strict` makes that a failure.

## The collector stage over the testbed

The workflow's second job runs the same pinned collector and toolkit over the `core` project of
[`AbsaOSS/living-doc-testbed`](https://github.com/AbsaOSS/living-doc-testbed) at `master`. It asserts
invariants, not snapshots, then runs the derived problem cases, collector only. Run it locally before a
PR that touches `tests/collector/**`, `tests/testbed/**` or the workflow:

```shell
tests/testbed/run-testbed-stage.sh
```

How it works, how to read a failure: [`tests/README.md`](tests/README.md).
Negative cases, how to add one: [`tests/testbed/negative-cases.md`](tests/testbed/negative-cases.md).

## The agentic layer

The skills and the `living-doc-bdd-copilot` agent that help an author write living-doc input live
in [`agentic/`](agentic/) and ship from this repository. They are optional — the pipeline is
AI-free and runs without them.

A change there has its own conventions, its own test commands and its own PR checklist:
see [`agentic/CONTRIBUTING.md`](agentic/CONTRIBUTING.md).

## Target Branches

PRs have to target `main`, `master`, `support/*`, or `release/*`.

### Community and Communication

If you have any questions or need help, don't hesitate to reach out through our GitHub discussion section!

#### Thanks!
