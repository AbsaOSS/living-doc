# Getting Started

This guide walks through assembling your first Living Documentation pipeline: pick a source, pick an output, chain the actions.

## 1. Pick a collector

| Your source | Use |
|---|---|
| GitHub repository issues/labels | [living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) |
| Azure DevOps work items/boards/pipelines | [living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad) |

See [Collecting from GitHub](github-collection.md) or [Collecting from Azure DevOps](azure-devops-collection.md) for setup details.

## 2. Pick a generator

| You want | Use |
|---|---|
| Plain Markdown files | [living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown) |
| PDF reports (user stories, test catalogs, coverage matrices) | [living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf) |

See [Choosing a Generator](choosing-a-generator.md) for a full comparison.

## 3. Chain them in a workflow

A minimal pipeline is a GitHub Actions workflow that runs the collector, then the generator, on a schedule:

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

      - name: Collect
        uses: AbsaOSS/living-doc-collector-gh@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          # collector-specific inputs — see the collector's README

      - name: Generate
        uses: AbsaOSS/living-doc-generator-markdown@v1
        with:
          # generator-specific inputs — see the generator's README

      - name: Publish
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add .
          git commit -m "docs: update living documentation" || echo "no changes"
          git push
```

Replace the collector/generator steps and their inputs with the ones you picked in steps 1–2; each project's own README documents its action inputs and outputs in detail.

## 4. Add a normalization step (optional)

If you're combining multiple collectors, or feeding a generator that expects the canonical shape, insert [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) between collect and generate. See [Architecture](../introduction/architecture.md) for where it fits.

## Next steps

- Walk through a full worked example: [Tutorials](../tutorials/)
- Understand the data flow: [Architecture](../introduction/architecture.md)
