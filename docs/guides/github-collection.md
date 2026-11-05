# Collecting from GitHub

## Purpose

This page is how to collect from GitHub with `living-doc-collector-gh`: its modes, when to use each, the project id
and where it writes.

Read before: [Build a pipeline](build-a-pipeline.md) · Next: [GitHub Source Code → Markdown](../tutorials/gh-source-to-markdown.md)

## Contents

- [What it collects](#what-it-collects)
- [When to use it](#when-to-use-it)
- [Basic setup](#basic-setup)
- [Where it writes](#where-it-writes)
- [Feeding it forward](#feeding-it-forward)

## What it collects

[living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) is a GitHub Action that mines a
repository into the JSON shape the rest of the ecosystem consumes. It has three independently toggleable modes —
enable one or several in the same workflow step; each takes its own repository list.

| Mode | Mines | Writes | Status |
|---|---|---|---|
| `doc-source` | Living-doc header blocks in checked-out source: User Story and Functionality blocks in `.feature` files, Feature blocks in TypeScript PageObject files, with acceptance criteria, business value, ownership and parent links. The format: [Authoring formats](../reference/authoring-formats.md). | `doc-source/doc-source.json` | Available |
| `ui-tests` | Gherkin scenario blocks from `.feature` files, as a test catalog keyed by `@US_ID` / `@AC` tags: scenario name, tags, steps and source location. | `ui-tests/ui-tests.json` | Available |
| `doc-issues` | GitHub issues used as documentation tickets: title, body, labels, state, timestamps and audit events, optionally with linked GitHub Projects state. | `doc-issues/doc-entities.json` | Planned |

**Planned:** GitHub issues as a documentation source are not in the `v0.1.0` pipeline, and `doc-issues: true` fails the run at start; their layout is fixed already: [GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout).

Each mode's maturity is tracked on the [project README](https://github.com/AbsaOSS/living-doc-collector-gh).
Each file carries a `metadata` provenance block beside the mined entities
([Contracts — The metadata envelope](../reference/contracts.md#the-metadata-envelope)).

## When to use it

Use this collector when your project tracks living documentation — User Stories, Features, and Functionalities — as:

- Source code, including Gherkin test scenarios (`.feature` files)
- Issues (optionally organized in GitHub Projects) — planned

## Basic setup

Check out each repository the modes read earlier in the job, then add one collector step:

```yaml
- uses: actions/checkout@v7
- uses: AbsaOSS/living-doc-collector-gh@v0.2.0
  with:
    project-id: your-project
    doc-source: true
    doc-source-repositories: |
      [{"organization-name": "your-org", "repository-name": "your-repo",
        "us-paths": ["${{ github.workspace }}/features/liv_doc_us"],
        "func-paths": ["${{ github.workspace }}/features/liv_doc_func"],
        "pages-paths": ["${{ github.workspace }}/pages"]}]
    ui-tests: true
    ui-tests-repositories: |
      [{"organization-name": "your-org", "repository-name": "your-repo",
        "paths": ["${{ github.workspace }}/features"]}]
```

- `project-id` names the project every file belongs to
  ([Pipeline rules — Project id](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#project-id)).
- The `doc-source` and `ui-tests` modes read the checkouts only: they call no GitHub API and need no token
  ([prerequisites](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md#prerequisites)).
- Every folder an entry names must exist, or its whole source fails: drop `func-paths` or `pages-paths` when the
  repository has no such folder.
- A project of several repositories checks out each one and adds one entry per repository to each list. The fields
  of an entry:
  [`doc-source`](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/doc_source/README.md#repository-entry),
  [`ui-tests`](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/ui_tests/README.md#repository-entry).
- Every input of the action: [`collector-gh` inputs](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md#inputs).

## Where it writes

Each enabled mode writes its one file into `<output-path>/<mode>/`, `output/collector-gh/doc-source/doc-source.json`
by default, and clears only its own folder
([output layout](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md#output-layout),
[Collector output layout](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#collector-output-layout)).
Which step reads each file: [Data flows — Files](../reference/data-flows.md#files).

## Feeding it forward

Collector output is JSON. It always passes through [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit)'s
normalize step next — generators consume `toolkit`'s canonical dataset, not raw collector output. The whole chain:
[Build a pipeline](build-a-pipeline.md).
