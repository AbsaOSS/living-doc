# Tutorial: GitHub Source Code → Markdown

> **Forward-looking.** This pipeline relies on `collector-gh`'s `doc-source` and `ui-tests` modes,
> which are specified in `collector-gh/SPEC.md` but **not yet implemented**
> ([Data Flows & Schemas](../specs/data-flows.md) §2). Treat the collector step below as the intended
> shape; check the [project README](https://github.com/AbsaOSS/living-doc-collector-gh) for the real
> inputs once the modes ship.

Goal: turn the **User Story / Feature / Functionality header blocks and Gherkin `.feature` files that
live in your source tree** (not issues) into Markdown, refreshed on every push.

Use this when living documentation is authored [directly in code](../guides/living-doc-header-types.md)
— the preferred authoring path — rather than as issues.

## 1. Prepare the inputs

| Document type you want | What must be in the repo |
|---|---|
| [Technical project](../guides/living-doc-document-types.md#technical-project) | US / Feature / Functionality header blocks and PageObject headers in the [documented format](../guides/living-doc-header-types.md) |
| [Test catalog](../guides/living-doc-document-types.md#test-catalog) | `.feature` files under `features/liv_doc_us/` and `features/liv_doc_func/` with `@AC:` tags |

## 2. Add the workflow

`.github/workflows/living-doc-source.yml`:

```yaml
name: Living Documentation (source)

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
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

      # 3. GENERATE Markdown
      - name: Generate Markdown
        uses: AbsaOSS/living-doc-generator-markdown@v1
        with:
          source-path: generator-ready.json
          output-path: docs/generated

      # 4. COMMIT
      - name: Publish
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add docs/generated
          git commit -m "docs: refresh living documentation" || echo "no changes"
          git push
```

## 3. What happens on each run

1. `collector-gh` parses the header blocks and `.feature` files into `doc-source.json` (+ `ui-tests.json` for the test catalog).
2. `toolkit` normalizes that into the canonical dataset.
3. `generator-markdown` renders `.md` files under `docs/generated/`.
4. The workflow commits any changes.

## Related

- [GitHub Issues → Markdown](gh-issues-to-markdown.md) — the same output from issues instead of code
- [GitHub Source → PDF](gh-source-to-pdf.md) — same inputs, PDF output
- [Living Doc Header Types](../guides/living-doc-header-types.md) — the source-code format being mined
- [Living Documentation Document Types](../guides/living-doc-document-types.md)
