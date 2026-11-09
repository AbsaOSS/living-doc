# How to Contribute?

## Purpose

This page is how to contribute to this repository: reporting bugs and proposing features, branches and pull
requests, the rules every page follows, the checks over the corpus and the testbed, and the agentic layer.

## Contents

- [Identifying and Reporting Bugs](#identifying-and-reporting-bugs)
- [Proposing New Features](#proposing-new-features)
- [Branch Naming](#branch-naming)
- [PR Naming](#pr-naming)
- [PR Description](#pr-description)
- [Writing documentation](#writing-documentation)
- [Regenerating the collector snapshots](#regenerating-the-collector-snapshots)
- [The collector stage over the testbed](#the-collector-stage-over-the-testbed)
- [The agentic layer](#the-agentic-layer)
- [Target Branches](#target-branches)
- [Community and Communication](#community-and-communication)

## Identifying and Reporting Bugs

* **Ensure the bug has not already been reported** by searching our **[GitHub Issues](https://github.com/AbsaOSS/living-doc/issues)**.
* If you cannot find an open issue describing the problem, use the **Bug Report** GitHub issue template to open a new one.

## Proposing New Features

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

PR body has to also include these sections: `## Overview`, `## Release Notes`, `## Framework`, `## Related`.
- **Overview** – what changed and why.
- **Release Notes** – short, user-facing summary for the changelog.
- **Framework** – tick one box: the change stays inside the frame of [Principles](docs/introduction/principles.md#the-frame), or names the row it bends and adds the exception there.
- **Related** – link the issue with a closing keyword, e.g. `Closes #123` or `Fixes AB#12345`.

## Writing documentation

**Provisional.** These are the rules every page of this repository follows; this section is their only copy here.
`tests/docs/test_page_structure.py` checks the ones marked *(checked)*, in `examples-check.yml`, on every change to
`README.md`, `CONTRIBUTING.md` or `docs/**`.

**Levels.** A page's folder gives its level; the levels run from the concept down to the definition, so no hub page
is needed.

| Level | Pages | Rule |
|---|---|---|
| L0 | `README.md` | what this is, where to start |
| L1 | `docs/introduction/` | the concept and the shape of the system |
| L2 | `docs/guides/`, and `docs/examples/README.md`, the corpus guide | how to do one thing; may show YAML and inputs; links every reference fact |
| L3 | `docs/tutorials/` | one copy-pasteable pipeline, complete |
| L4 | `docs/reference/` | the only level that defines a fact |
| L5 | `docs/projects/` | one card per repository, at most 25 lines: role, files in and out, README link; no input table |
| D | `CONTRIBUTING.md`, `docs/_integration/README.md` | contributing to and running this repository |

Not pages: every `CONTEXT.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.github/`, `.local_context/`, `agentic/` (its
own rules, in [`agentic/CONTRIBUTING.md`](agentic/CONTRIBUTING.md)), `tests/`, the mined inputs under
`docs/examples/gh-issues/`, and each run folder under `docs/_integration/`.

**Flow rules.**

1. Every page opens with `## Purpose`, then `## Contents` *(checked)*.
2. `README.md` and `docs/introduction/` stay conceptual: no field name, input table, YAML block *(checked)* or
   version number. `README.md`'s one version names the release the documentation describes.
3. A reference fact is linked, never restated.
4. Nothing planned is described as available: a page that presents a planned part says so in one line.
5. Every page is within three links of `README.md` *(checked)*.
6. No page carries a `path::symbol` anchor *(checked)*.

**Page anatomy.**

1. `# Title`.
2. `## Purpose`: one to three sentences on what the page is for ("This page is …", "This page defines …"), not who
   reads it. Where the page sits on a reading path, `Read before:` and `Next:` links follow. `README.md` says what
   Living Documentation does and where this repository sits instead.
3. `## Contents`: one `- [title](#chapter)` line for each other `##` chapter, and nothing else *(checked)*.
4. Then only the parts the page needs:

| Part | Form |
|---|---|
| Principle | at most five short sentences: the core idea |
| Fact or decision list | one line per item |
| Option list | every available option with a one-line meaning; complete |
| Example | at most 20 lines in a guide; complete in a tutorial |
| Prose | only in Purpose, Principle and one-line list lead-ins; a block is at most four lines |
| Language | sentences of at most 20 words; active voice; one term per idea, the glossary's |

Two kinds of page are exempt:

- A **project card** is its `# Title` and `## Purpose` only, with no other chapter and no table, in at most 25
  lines *(checked)*.
- A **redirect** keeps a moved or merged page's path: its `# Title`, a blank line and one
  ``Moved to [`<path>`](<link>).`` line *(checked)*. No page links it *(checked)*; it is there for links from other
  repositories, so it is exempt from the three-link rule.

A new page goes into `PAGES`, `CARDS` or `REDIRECTS` in `tests/docs/pages.py`; the check fails on a tracked page
that is on no list.

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

The `collector-gh`, `toolkit` and `generator-markdown` pins live only in
`tests/collector/collector-pins.env`. A pin bump is a reviewed change, like a dependency bump: change the
ref and commit the regenerated snapshots in the same PR. `generator-markdown` feeds no snapshot, so its pin
alone regenerates nothing. `python tests/examples/check_utilities_pins.py` prints the
`living-doc-utilities` version pinned by the collector, the toolkit, `generator-markdown` and the corpus
checker (`tests/examples/requirements-examples-check.txt`) and warns on a minor-version skew; `--strict`
makes that a failure.

[Authoring documentation § What the pipeline also accepts](docs/guides/authoring-documentation.md#what-the-pipeline-also-accepts)
shows each corrected variant as a before/after pair copied from `living-doc-utilities`'
`living_doc_utilities/authoring/normalisation_cases.yaml` at the version the page names.
`tests/examples/examples_check.py` compares each pair with that file at the tag of the corpus checker's
`living-doc-utilities` version, and the codes of [Error codes](docs/reference/errors.md#codes) with that
version's registry. A change that moves that version fails `examples-check.yml` until the same PR brings
both pages in line:

1. For each pair the check names, copy the case's `input` into the `before` block and its `expected` into
   the `after` block, byte for byte.
2. For a case id the file no longer has, show the case that replaced it, or drop the pair.
3. Move the version in the page's link to the file and in the sentence after it.
4. Add or remove the row of each code the check names.
5. Not checked: add a pair for a new `feature_header`, `page_object` or `scenario_file` case whose variant
   the page does not show yet.

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
A gate or a milestone runs the whole chain on an operator's machine instead:
[Integration runs](docs/_integration/README.md).

## The agentic layer

The skills and the `living-doc-bdd-copilot` agent that help an author write living-doc input live
in [`agentic/`](agentic/) and ship from this repository. They are optional — the pipeline is
AI-free and runs without them.

A change there has its own conventions, its own test commands and its own PR checklist:
see [`agentic/CONTRIBUTING.md`](agentic/CONTRIBUTING.md).

## Target Branches

PRs have to target `main`, `master`, `support/*`, or `release/*`.

## Community and Communication

If you have any questions or need help, don't hesitate to reach out through our GitHub discussion section!

Thanks!
