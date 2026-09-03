# Tutorial: GitHub Source Code → PDF

> **Forward-looking.** This pipeline relies on `collector-gh`'s `doc-source` and `ui-tests` modes,
> which are specified in `collector-gh/SPEC.md` but **not yet implemented**
> ([Data Flows & Schemas](../specs/data-flows.md) §2). Treat the collector step below as the intended
> shape; check the [project README](https://github.com/AbsaOSS/living-doc-collector-gh) for the real
> inputs once the modes ship.

Goal: produce a **PDF** — a technical project, a UI test catalog, or a coverage matrix — from the
living-documentation header blocks and Gherkin `.feature` files in your source tree.

Same inputs as [GitHub Source → Markdown](gh-source-to-markdown.md); only the generator step differs.

## 1. Prepare the inputs

The [coverage matrix](../guides/living-doc-document-types.md#coverage-matrix) needs **both** a
technical project and a test catalog for the same repo — so the header blocks and the `.feature`
files must use consistent AC IDs. A technical project or test catalog PDF on its own needs only its
own inputs.

## 2. Add the workflow

`.github/workflows/living-doc-source-pdf.yml`:

```yaml
name: Living Documentation (source, PDF)

on:
  workflow_dispatch:

jobs:
  generate-pdf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 1. COLLECT from source code — doc-source + ui-tests modes
      #    (exact input names TBD — see collector-gh SPEC.md / README)
      - name: Collect from source
        uses: AbsaOSS/living-doc-collector-gh@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          repository: ${{ github.repository }}
          modes: doc-source,ui-tests

      # 2. NORMALIZE
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Normalize (toolkit)
        run: |
          pip install living-doc-toolkit
          living-doc normalize-issues --input doc-source.json --output generator-ready.json

      # 3. GENERATE PDF — pick the document-type for the document you want
      - name: Generate PDF
        uses: AbsaOSS/living-doc-generator-pdf@v1
        with:
          source-path: generator-ready.json
          document-type: user-stories        # or: ui-test-catalog | coverage-matrix
          output-path: reports/living-doc.pdf

      # 4. UPLOAD
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: living-doc-pdf
          path: reports/living-doc.pdf
```

## 3. What happens on each run

1. `collector-gh` parses the header blocks and `.feature` files into `doc-source.json` / `ui-tests.json`.
2. `toolkit` normalizes that into the canonical dataset (for a coverage matrix, `toolkit coverage-matrix` joins the two).
3. `generator-pdf` renders the chosen template to a PDF.
4. The PDF is uploaded as a workflow artifact — add a publish/notify step if it needs a wider audience.

## 4. Other report types

Swap `document-type:` to `ui-test-catalog` or `coverage-matrix` — see the
[project README](https://github.com/AbsaOSS/living-doc-generator-pdf) for the current template set,
and [Living Documentation Document Types](../guides/living-doc-document-types.md) for what each one
contains and needs.

## Related

- [User Stories → PDF](user-stories-to-pdf.md) — the same output from issues instead of code
- [GitHub Source → Markdown](gh-source-to-markdown.md) — same inputs, Markdown output
- [Choosing a Generator](../guides/choosing-a-generator.md)
