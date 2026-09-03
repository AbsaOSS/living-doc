# Tutorial: Azure DevOps Work Items → Markdown

> **Forward-looking.** `living-doc-generator-markdown` is early stage, and `toolkit`'s adapter for
> `collector-ad` output is still being built (see [Roadmap](../specs/roadmap.md)). Treat the collect
> and normalize steps below as the intended shape; check each project's README before running this
> for real.

Goal: turn Azure DevOps work items into Markdown files, refreshed nightly.

## 1. Add the workflow

`.github/workflows/living-doc-ado.yml`:

```yaml
name: Living Documentation (ADO)

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

      - name: Collect from Azure DevOps
        uses: AbsaOSS/living-doc-collector-ad@v1
        with:
          organization: my-ado-org
          project: my-project
          pat: ${{ secrets.ADO_PAT }}

      # NORMALIZE — required: generators consume toolkit's canonical dataset, not raw collector output
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Normalize (toolkit)
        run: |
          pip install living-doc-toolkit
          living-doc normalize-issues --input work-items.json --output generator-ready.json

      - name: Generate Markdown
        uses: AbsaOSS/living-doc-generator-markdown@v1
        with:
          source-path: generator-ready.json
          output-path: docs/generated

      - name: Commit output
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add docs/generated
          git commit -m "docs: refresh generated documentation" || echo "no changes"
          git push
```

## 2. What happens on each run

1. `collector-ad` mines work items into `work-items.json`.
2. `toolkit` normalizes that into the canonical dataset generators consume.
3. `generator-markdown` renders it as `.md` files under `docs/generated`.
4. The workflow commits any changes.

## 3. Combining with GitHub data

If the same documentation set needs both Azure DevOps and GitHub sources, run both collectors and let the single `toolkit` normalize step merge their output before the generator — see [Architecture](../introduction/architecture.md).

## Related

- [Collecting from Azure DevOps](../guides/azure-devops-collection.md)
- [Choosing a Generator](../guides/choosing-a-generator.md)
