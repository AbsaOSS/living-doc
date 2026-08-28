# Getting Started

This guide walks through assembling your first Living Documentation pipeline: pick a source, pick an output, chain the actions.

## 1. Pick a collector

| Your source | Use |
|---|---|
| GitHub repository issues/labels | [living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) |
| Azure DevOps work items | [living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad) |

See [Collecting from GitHub](github-collection.md) or [Collecting from Azure DevOps](azure-devops-collection.md) for setup details.

## 2. Pick a generator

| You want | Use |
|---|---|
| Plain Markdown files | [living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown) |
| PDF reports (user stories, test catalogs, coverage matrices) | [living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf) |

See [Choosing a Generator](choosing-a-generator.md) for a full comparison.

## 3. Chain them in a workflow

A pipeline is three stages, always in this order: **collect → normalize → generate**. The normalize step — [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) — is **not optional**: generators consume the canonical dataset toolkit produces, not raw collector output, even when you only have one collector. See [Architecture](../introduction/architecture.md) for why the pipeline is shaped this way.

Unlike the collector and generator, `toolkit` isn't packaged as a GitHub Action — it's a Python CLI, invoked with `pip install` + `run` in its own step. Here's a full pipeline running nightly against a GitHub repository's issues, normalizing them, and committing the rendered Markdown:

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

      - name: Collect from GitHub
        uses: AbsaOSS/living-doc-collector-gh@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          repository: ${{ github.repository }}
          # writes doc-issues.json into the workspace

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Normalize (toolkit)
        run: |
          pip install living-doc-toolkit
          living-doc normalize-issues --input doc-issues.json --output pdf_ready.json   # renamed to generator-ready.json in a coming release

      - name: Generate Markdown
        uses: AbsaOSS/living-doc-generator-markdown@v1
        with:
          source-path: pdf_ready.json
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

- `doc-issues.json` / `pdf_ready.json` are `collector-gh`'s and `toolkit`'s current documented file names (`pdf_ready.json` is slated to be renamed `generator-ready.json` — see [Data Flows & Schemas](../specs/data-flows.md) §5 — but that migration hasn't shipped yet, so use `pdf_ready.json` today).
- `living-doc normalize-issues` is `toolkit`'s actual CLI command, taking `--input`/`--output` file paths — this is a workflow step like any other, not a local-only affordance.
- Swap the collector/generator `uses:` steps for the ones you picked in steps 1–2 above; each project's own README documents its exact action inputs and outputs, which evolve faster than this guide.

## Worked examples

Each cell is a copy-paste tutorial for that **source + output** combination. The collect and
normalize steps are the same across a row; only the generator step changes between columns.

| Source | → Markdown | → PDF |
|---|---|---|
| GitHub issues | [GitHub Issues → Markdown](../tutorials/gh-issues-to-markdown.md) | [User Stories → PDF](../tutorials/user-stories-to-pdf.md) |
| GitHub source code (`.feature` files, header blocks) | [GitHub Source → Markdown](../tutorials/gh-source-to-markdown.md) † | [GitHub Source → PDF](../tutorials/gh-source-to-pdf.md) † |
| Azure DevOps work items | [Azure DevOps Work Items → Markdown](../tutorials/ado-workitems-to-markdown.md) | swap the generator step in the ADO tutorial for `generator-pdf` — same pattern as [User Stories → PDF](../tutorials/user-stories-to-pdf.md) |

† Source-code collection depends on `collector-gh`'s `doc-source` / `ui-tests` modes, which are
specified but not yet built ([Data Flows & Schemas](../specs/data-flows.md) §2). Those two tutorials
describe the intended workflow and are marked accordingly.

## Next steps

- Decide which [document types](living-doc-document-types.md) you need before building the pipeline
- Understand the data flow: [Architecture](../introduction/architecture.md)
