# Tutorial: Azure DevOps Work Items → Markdown

> `living-doc-generator-markdown` is early stage; treat the generator step below as illustrative until its action inputs stabilize. Check the [project README](https://github.com/AbsaOSS/living-doc-generator-markdown) before running this for real.

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

      - name: Generate Markdown
        uses: AbsaOSS/living-doc-generator-markdown@v1
        with:
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

1. `collector-ad` mines work items, boards, and pipeline metadata into JSON.
2. `generator-markdown` renders that JSON as `.md` files under `docs/generated`.
3. The workflow commits any changes.

## 3. Combining with GitHub data

If the same documentation set needs both Azure DevOps and GitHub sources, run both collectors and merge their output through [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) before the generator step — see [Architecture](../introduction/architecture.md).

## Related

- [Collecting from Azure DevOps](../guides/azure-devops-collection.md)
- [Choosing a Generator](../guides/choosing-a-generator.md)
