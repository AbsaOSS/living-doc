# Getting Started

This guide walks through assembling your first Living Documentation pipeline: pick a source, pick an output, chain the actions.

## 1. Pick a collector

| Your source | Use |
|---|---|
| GitHub repository source code (header blocks, `.feature` files) | [living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) |
| GitHub repository issues/labels *(planned)* | [living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) |
| Azure DevOps work items *(planned)* | [living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad) |

See [Collecting from GitHub](github-collection.md) or [Collecting from Azure DevOps](azure-devops-collection.md) for setup details.

## 2. Pick a generator

| You want | Use |
|---|---|
| Plain Markdown files | [living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown) |
| PDF reports (user stories, test catalogs, coverage matrices) | [living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf) |

See [Choosing a Generator](choosing-a-generator.md) for a full comparison.

## 3. Chain them in a workflow

A pipeline is three stages, always in this order: **collect → normalize → generate**. The normalize step — [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) — is **not optional**: generators consume the canonical dataset toolkit produces, not raw collector output, even when you only have one collector. See [Architecture](../introduction/architecture.md) for why the pipeline is shaped this way.

Unlike the collector and generator, `toolkit` isn't packaged as a GitHub Action — it's a Python CLI, invoked with `pip install` + `run` in its own step. Here's a full pipeline running nightly against a GitHub repository's source code, normalizing it, and committing the rendered Markdown:

```yaml
name: Living Documentation

on:
  schedule:
    - cron: '0 4 * * *'
  workflow_dispatch:

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Collect from source
        uses: AbsaOSS/living-doc-collector-gh@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          repository: ${{ github.repository }}
          modes: doc-source
          # writes doc-source.json into the workspace

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Normalize (toolkit)
        run: |
          pip install living-doc-toolkit
          living-doc normalize-docs --input doc-source.json --output generator-ready.json

      - name: Generate Markdown
        uses: AbsaOSS/living-doc-generator-markdown@v1
        with:
          source-path: generator-ready.json
          output-path: docs/generated

      - name: Publish
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add docs/generated
          git commit -m "docs: update living documentation" || echo "no changes"
          git push
```

A few things to note about these inputs:

- `doc-source.json` and `generator-ready.json` are `collector-gh`'s and `toolkit`'s documented file names — `generator-ready.json` is the canonical dataset `toolkit`'s `normalize-docs` command writes.
- `living-doc normalize-docs` is `toolkit`'s CLI command for the documentation file, taking `--input`/`--output` file paths; `normalize-tests` turns `ui-tests.json` into `ui-test-catalog.json`, and `coverage-matrix` joins the two — each a workflow step like any other, not a local-only affordance.
- Swap the collector/generator `uses:` steps for the ones you picked in steps 1–2 above; each project's own README documents its exact action inputs and outputs, which evolve faster than this guide.

## Worked examples

Each cell is a copy-paste tutorial for that **source + output** combination. The collect and
normalize steps are the same across a row; only the generator step changes between columns.

| Source | → Markdown | → PDF |
|---|---|---|
| GitHub issues *(planned)* | [GitHub Issues → Markdown](../tutorials/gh-issues-to-markdown.md) | [Technical Project → PDF](../tutorials/technical-project-to-pdf.md) |
| GitHub source code (`.feature` files, header blocks) | [GitHub Source → Markdown](../tutorials/gh-source-to-markdown.md) | [GitHub Source → PDF](../tutorials/gh-source-to-pdf.md) |
| Azure DevOps work items *(planned)* | [Azure DevOps Work Items → Markdown](../tutorials/ado-workitems-to-markdown.md) | swap the generator step in the ADO tutorial for `generator-pdf` — same pattern as [Technical Project → PDF](../tutorials/technical-project-to-pdf.md) |

Source-code collection uses `collector-gh`'s `doc-source` / `ui-tests` modes (Available).

## Next steps

- Decide which [document types](living-doc-document-types.md) you need before building the pipeline
- Understand the data flow: [Architecture](../introduction/architecture.md)
