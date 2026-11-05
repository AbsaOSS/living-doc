# Build a pipeline

## Purpose

This page is how to assemble a pipeline: the three stages, the generator to choose, one job's steps, the files a
run writes, and the tutorial for each source and output.

Read before: [Living Documentation in 5 Minutes](../introduction/quickstart.md) ·
Next: [GitHub Source Code → Markdown](../tutorials/gh-source-to-markdown.md)

## Contents

- [Stages](#stages)
- [Choose a generator](#choose-a-generator)
- [The steps](#the-steps)
- [What a run writes](#what-a-run-writes)
- [Tutorials](#tutorials)

## Stages

A pipeline is three stages, always in this order: **collect → normalize → generate**. Each is a GitHub Action, and
a workflow chains them in one job. Why the pipeline is shaped this way: [Architecture](../introduction/architecture.md).

| Stage | Action | What it does here |
|---|---|---|
| Collect | [living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) | mines the headers and scenarios in your checked-out source code ([Collecting from GitHub](github-collection.md)) |
| Normalize | [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) | turns one collector file into the file a generator reads; one step per command |
| Generate | [living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown) | renders one document per step |

- The normalize step is **not optional**: a generator reads only `toolkit` output, never raw collector output, even
  with one collector.
- One pipeline mines one documentation source: source code headers today. GitHub issues and Azure DevOps work
  items are planned ([Choosing a documentation source](choosing-a-documentation-source.md),
  [Collecting from Azure DevOps](azure-devops-collection.md)).
- Which document each step renders, and what it needs: [Document types](living-doc-document-types.md).

## Choose a generator

All generators read the same `toolkit` files, and differ only in what they render. Pick by where the output needs to
live.

| Generator | Output | Best for | Status |
|---|---|---|---|
| [living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown) | Plain `.md` files | Docs committed alongside code, rendered by whatever already renders your repository's Markdown (GitHub, a wiki, a generic static site generator); editable and diffable like code. | Available |
| [living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf) | PDF | Point-in-time deliverables: technical projects, UI test catalogs, coverage matrices — a report or sign-off artifact, shared or archived as a file, not browsed as a site. | Planned |

**PDF output is planned:** `living-doc-generator-pdf` is not part of the `v0.1.0` pipeline ([generator-pdf](../projects/generator-pdf.md)).
One pipeline can run several generator steps over the same `toolkit` files: one per document, and, once PDF output
lands, one per output format.

## The steps

One job's steps: collect the User Stories, normalize them in the release view, render the technical project. Each
action is pinned by its release tag, and one `project-id` names the project.

```yaml
- uses: actions/checkout@v7
- uses: actions/setup-python@v7
  with: { python-version: '3.14' }
- uses: AbsaOSS/living-doc-collector-gh@v0.2.0
  with:
    project-id: your-project
    doc-source: true
    doc-source-repositories: |
      [{"organization-name": "your-org", "repository-name": "your-repo",
        "us-paths": ["${{ github.workspace }}/features/liv_doc_us"]}]
- uses: AbsaOSS/living-doc-toolkit@v0.1.0
  with:
    command: normalize-docs
    input: output/collector-gh/doc-source/doc-source.json
    output: output/toolkit/generator-ready.json
    view: release
- uses: AbsaOSS/living-doc-generator-markdown@v0.1.0
  with:
    document-type: technical-project
    source-path: output/toolkit/generator-ready.json
```

- `toolkit` and `generator-markdown` need Python on the runner, so `actions/setup-python` comes first
  ([`toolkit` prerequisites](https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/action.md#prerequisites)).
- The collector reads the checkout and needs no token
  ([`collector-gh` prerequisites](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md#prerequisites)).
- The test catalog and the coverage matrix need the scenarios too: `ui-tests: true` and its repository list on the
  collect step. `normalize-tests` then turns `ui-tests.json` into `ui-test-catalog.json`, and `coverage-matrix` joins
  the two files; each is one more `toolkit` step, read by one more generator step
  ([Data flows — Commands](../reference/data-flows.md#commands)). The tutorial renders all three.
- Every input of each step:
  [`collector-gh`](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md#inputs),
  [`toolkit`](https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/action.md#inputs),
  [`generator-markdown`](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/docs/action.md#inputs).
- The project id, and why one pipeline documents one project:
  [Pipeline rules](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#project-id).

## What a run writes

- Each generator step writes two files into its `output-path`, named by its document type: the document
  `<document-type>.md` and its `<document-type>.run-report.json`
  ([`generator-markdown` files](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/docs/action.md#files)).
- The run report lists what the document shows; commit it with the document, or publish the document alone.
- Every file of the chain, with its default path and who reads it: [Data flows — Files](../reference/data-flows.md#files).
- A step that warns or fails names a code: [Error codes](../reference/errors.md).

## Tutorials

One per **source + output** combination. The collect and normalize steps are the same across a row; only the
generator step changes between columns.

| Source | → Markdown | → PDF *(planned)* |
|---|---|---|
| GitHub source code (`.feature` files, header blocks) | [GitHub Source Code → Markdown](../tutorials/gh-source-to-markdown.md) | [GitHub Source Code → PDF](../tutorials/gh-source-to-pdf.md) *(planned)* |
| GitHub issues *(planned)* | [GitHub Issues → Markdown](../tutorials/gh-issues-to-markdown.md) *(planned)* | [Technical Project → PDF](../tutorials/technical-project-to-pdf.md) *(planned)* |
| Azure DevOps work items *(planned)* | [Azure DevOps Work Items → Markdown](../tutorials/ado-workitems-to-markdown.md) *(planned)* | planned; no tutorial yet |
