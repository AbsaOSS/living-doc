# Tutorial: User Stories → PDF

Goal: produce a PDF report — user stories, a UI test catalog, or a coverage matrix — from collected issue/work-item data, suitable for sharing or archiving as a deliverable.

## 1. Add the workflow

`.github/workflows/living-doc-pdf.yml`:

```yaml
name: Living Documentation (PDF)

on:
  workflow_dispatch:

jobs:
  generate-pdf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Collect from GitHub
        uses: AbsaOSS/living-doc-collector-gh@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          repository: ${{ github.repository }}

      # NORMALIZE — required: generator-pdf consumes toolkit's canonical dataset, not raw collector output
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Normalize (toolkit)
        run: |
          pip install living-doc-toolkit
          living-doc normalize-issues --input doc-issues.json --output pdf_ready.json   # renamed to generator-ready.json in a coming release

      - name: Generate PDF
        uses: AbsaOSS/living-doc-generator-pdf@v1
        with:
          source-path: pdf_ready.json
          document-type: user-stories
          output-path: reports/user-stories.pdf

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: user-stories-pdf
          path: reports/user-stories.pdf
```

This example triggers manually (`workflow_dispatch`) since PDF reports are typically point-in-time deliverables rather than continuously refreshed docs — switch to a `schedule` trigger if you want it regenerated automatically.

## 2. What happens on each run

1. `collector-gh` mines issues into `doc-issues.json`.
2. `toolkit` normalizes that into the canonical dataset.
3. `generator-pdf` renders it to a PDF with the `user-stories` template set (`document-type` also accepts `ui-test-catalog` and `coverage-matrix`).
4. The PDF is uploaded as a workflow artifact — attach a publish/notify step if it needs to reach a wider audience.

## 3. Other report types

Swap the `document-type` input to `ui-test-catalog` or `coverage-matrix` instead — see the [project README](https://github.com/AbsaOSS/living-doc-generator-pdf) for the current set of built-in templates and how to customize one with `template-path`.

## Related

- [Collecting from GitHub](../guides/github-collection.md)
- [Choosing a Generator](../guides/choosing-a-generator.md)
