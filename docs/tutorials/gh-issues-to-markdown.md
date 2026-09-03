# Tutorial: GitHub Issues → Markdown

> `living-doc-generator-markdown` is early stage; treat the generator step below as illustrative until its action inputs stabilize. Check the [project README](https://github.com/AbsaOSS/living-doc-generator-markdown) before running this for real.

Goal: turn a GitHub repository's issues into Markdown files committed back into the repo, refreshed nightly.

## 1. Add the workflow

`.github/workflows/living-doc.yml`:

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

      # NORMALIZE — required: generators consume toolkit's canonical dataset, not raw collector output
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Normalize (toolkit)
        run: |
          pip install living-doc-toolkit
          living-doc normalize-issues --input doc-issues.json --output generator-ready.json

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

1. `collector-gh` mines issues and labels from the current repository into `doc-issues.json`.
2. `toolkit` normalizes that into the canonical dataset generators consume.
3. `generator-markdown` renders it as `.md` files under `docs/generated`.
4. The workflow commits any changes.

## 3. Verify

After the first run, check that `docs/generated/` contains one Markdown file (or section) per issue category your labels define, and that content matches the current state of your issue tracker.

## Related

- [Collecting from GitHub](../guides/github-collection.md)
- [Choosing a Generator](../guides/choosing-a-generator.md)
- [Architecture](../introduction/architecture.md)
