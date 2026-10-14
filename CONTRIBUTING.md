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

`.github/workflows/real-collector-snapshot.yml` runs the real `living-doc-collector-gh`
(`doc-source` + `ui-tests`) over `docs/examples/`, validates each artifact against its contract,
asserts the corpus's first-stage content (`tools/check_collector_stage.py`), and diffs the normalized
result against the committed files in `docs/examples/_expected/collector-gh/<mode>/<artifact>.json`.
The job fails on any diff, and on any file under `docs/examples/_expected/` it no longer writes.

Regenerate and commit the expected files **in the same PR** whenever either side moves:

```shell
tools/regen-collector-snapshots.sh     # writes docs/examples/_expected/collector-gh/
git add docs/examples/_expected
```

No token is needed. The script needs Python 3.10 or later (`python3`, else `python`, or the
interpreter `PYTHON` names) and builds the collector's own venv in `.snapshot-venvs/collector-gh/`
(gitignored, reused while the interpreter and the pinned `requirements.txt` stay the same) from the
collector's runtime `requirements.txt` at its pinned ref, and from nothing else.

The pinned `collector-gh` ref lives in one place — `tools/collector-snapshot-pins.env`.
Bumping a pin is a reviewed change, exactly like a dependency bump: change the ref there and
commit the regenerated snapshots in the same PR. `python tools/check_utilities_pins.py` prints the
`living-doc-utilities` version the pinned collector and the corpus checker
(`tools/requirements-examples-check.txt`) each pin, and warns when their minor versions differ;
`--strict` turns the warning into a failure.

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
