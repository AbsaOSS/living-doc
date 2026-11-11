# .github

Parent: [../CONTEXT.md](../CONTEXT.md)

## Purpose

CI workflows, the PR template, issue templates, CODEOWNERS and Dependabot.

## Workflows

| Workflow | Runs on | Does |
|---|---|---|
| `examples-check.yml` | push to `master` and PRs touching `README.md`, `CONTRIBUTING.md`, `docs/**`, `tests/examples/**`, `tests/docs/**`, `tests/integration/**` | `tests/examples/examples_check.py` (the corpus, then the authoring guide's pairs against `living-doc-utilities`' normalisation cases at the installed version's tag, and `docs/reference/errors.md` against its code registry), then pytest over `tests/examples/`, `tests/docs/` (the page rules over every page, and the retired-names check's tests) and `tests/integration/` (the local integration runner's offline refusals; no workflow runs the runner); Python 3.14 |
| `retired-names.yml` | push to `master`, PRs (no path filter); manual dispatch | clones `collector-gh`, `toolkit` and `generator-markdown` at their pins in `tests/collector/collector-pins.env`, then `tests/docs/retired_names_check.py --strict` over them and the checkout; Python 3.14 |
| `real-collector.yml` | push to `master` and PRs touching `docs/examples/**`, `tests/**`; manual dispatch | two jobs on the pinned collector and toolkit: `real-collector-snapshot` and `testbed-collector-stage` ([tests/README.md § The workflow](../tests/README.md#the-workflow)) |
| `agentic-tests.yml` | push to `master` and PRs touching `agentic/**` (`agentic/.claude/**` and `agentic/.github/**` named too) or the two canon pages it copies | canon-copy check, script tests on 3.10 and 3.14, skill format validation |
| `link-check.yml` | push to `master`, PRs; lychee runs only when a `*.md` changed | `lychee --hidden` over `./**/*.md` (without `--hidden` its `**` skips `.claude/`, `.github/` and the agentic layer's two), with `--include-fragments`; this repository's `blob/master` links are remapped to the checkout |
| `check-pr-requirements.yml` | PRs, except Dependabot's | title, ticket in branch, body sections, closing keyword |
| `check_pr_release_notes.yml` | PRs to `master` | release notes present |
| `release_draft.yml` | manual, with a tag name | tag check, release notes, draft release |
| `aquasec-night-scan.yml` | nightly | security scan |
| `agd-update.yml` | weekly, manual | `agd update` of the agentic setup; opens a PR that closes an issue |

## Conventions

- Pin every `uses:` to a full commit SHA with a trailing version comment; never relax a pin to a tag. Some steps still use tags (for example `actions/setup-python@v7`); pin any step you add.
- A path filter is a contract: one that misses a file the job reads silently skips the check. When a job starts reading a new path, add it to the filter.
- The PR rules in `check-pr-requirements.yml` (`title-formats: issue-number`, `branch-require-ticket`, `description-required-sections`) match `CONTRIBUTING.md` and the PR template; change them together. Dependabot's pull requests skip the job; the comment on its `if:` says why and how.
- No lint, type-check or coverage job; don't propose one.

## Invariants and gotchas

- `real-collector.yml` has no schedule, and none is to be added (owner decision). A testbed merge triggers nothing: dispatch the workflow by hand to read a new testbed `master`.
- `testbed-collector-stage` checks out `AbsaOSS/living-doc-testbed` at `master`, never a SHA.
- AbsaOSS/living-doc#97 gives every `living-doc*` repository the same release-notes configuration; change it in all of them together. It is `release_draft.yml`'s `release-notes-title` and its options `chapters` through `row-format-link-pr`, `check_pr_release_notes.yml`'s `skip-labels` (`no RN,pr:no-release-notes`), and both workflows' `permissions:`. Every chapter but Silent-live names both label schemes (`bug` and `type:bug`, …). `skip-labels` takes no space after a comma: `release-notes-presence-check` v0.4.0 splits it without stripping, unlike the generator's lists.
- How `generate-release-notes` v1.3.3 sorts: it adds an issue's type, lowercased, to its labels (`Tech debt` → `tech debt`). It skips by labels on the issue only; a PR's skip label counts only on a PR that closes no issue. A closed issue with no PR goes under "Closed Issues without Pull Request ⚠️" whatever its labels, unless a skip label drops it. `duplicity-scope` covers only the ⚠️ chapters: an issue with two chapters' labels shows in both, marked 🔔.
- `link-check.yml` checks `https://github.com/AbsaOSS/living-doc/blob/master/…` links against the checkout (`--remap`), because the generated agentic copies and the skills link the canon absolutely and a new page is not on `master` until merged. A local lychee run needs it too, with the checkout's path for `${{ github.workspace }}`: the command is in `AGENTS.md` § Commands.
