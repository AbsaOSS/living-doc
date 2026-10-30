# .github

Parent: [../CONTEXT.md](../CONTEXT.md)

## Purpose

CI workflows, the PR template, issue templates, CODEOWNERS and Dependabot.

## Workflows

| Workflow | Runs on | Does |
|---|---|---|
| `examples-check.yml` | push to `master` and PRs touching `docs/examples/**`, `docs/guides/**`, `tests/examples/**` | `tests/examples/examples_check.py`, then pytest over `tests/examples/`; Python 3.14 |
| `real-collector.yml` | push to `master` and PRs touching `docs/examples/**`, `tests/**`; manual dispatch | two jobs on the pinned collector and toolkit: `real-collector-snapshot` and `testbed-collector-stage` ([tests/README.md § The workflow](../tests/README.md#the-workflow)) |
| `agentic-tests.yml` | push to `master` and PRs touching `agentic/**` or the two canon guides it copies | canon-copy check, script tests on 3.10 and 3.14, skill format validation |
| `link-check.yml` | push to `master`, PRs; lychee runs only when a `*.md` changed | `lychee` over `./**/*.md` with `--include-fragments` |
| `check-pr-requirements.yml` | PRs | title, ticket in branch, body sections, closing keyword |
| `check_pr_release_notes.yml` | PRs to `master` | release notes present |
| `release_draft.yml` | manual, with a tag name | tag check, release notes, draft release |
| `aquasec-night-scan.yml` | nightly | security scan |
| `agd-update.yml` | weekly, manual | `agd update` of the agentic setup; opens a PR that closes an issue |

## Conventions

- Pin every `uses:` to a full commit SHA with a trailing version comment; never relax a pin to a tag. Some steps still use tags (for example `actions/setup-python@v7`); pin any step you add.
- A path filter is a contract: one that misses a file the job reads silently skips the check. When a job starts reading a new path, add it to the filter.
- The PR rules in `check-pr-requirements.yml` (`title-formats: issue-number`, `branch-require-ticket`, `description-required-sections`) match `CONTRIBUTING.md` and the PR template; change them together.
- No lint, type-check or coverage job; don't propose one.

## Invariants and gotchas

- `real-collector.yml` has no schedule, and none is to be added (owner decision). A testbed merge triggers nothing: dispatch the workflow by hand to read a new testbed `master`.
- `testbed-collector-stage` checks out `AbsaOSS/living-doc-testbed` at `master`, never a SHA.
