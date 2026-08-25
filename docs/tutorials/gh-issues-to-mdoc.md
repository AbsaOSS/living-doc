# Tutorial: GitHub Issues → MDoc

Goal: publish a browsable MDoc-viewer documentation site generated directly from a GitHub repository's issues and labels.

## 1. Add the workflow

`.github/workflows/living-doc-mdoc.yml`:

```yaml
name: Living Documentation (MDoc)

on:
  schedule:
    - cron: '0 4 * * *'
  workflow_dispatch:

jobs:
  generate-mdoc:
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

      - name: Generate MDoc output
        uses: AbsaOSS/living-doc-generator-mdoc@v1
        with:
          output-path: site/

      - name: Commit output
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add site/
          git commit -m "docs: refresh MDoc site" || echo "no changes"
          git push
```

## 2. What happens on each run

1. `collector-gh` mines issues and labels into JSON.
2. `generator-mdoc` renders that JSON directly as MDoc-viewer-formatted Markdown under `site/` (no toolkit normalization step needed for this generator today — see the note in [Architecture](../introduction/architecture.md)).

## 3. Serve the site

Point your MDoc viewer at the `site/` directory, or add a follow-up deploy step (e.g. to GitHub Pages) once the content is committed.

## Related

- [Collecting from GitHub](../guides/github-collection.md)
- [Choosing a Generator](../guides/choosing-a-generator.md)
