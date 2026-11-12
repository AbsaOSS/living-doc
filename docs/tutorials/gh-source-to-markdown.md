# Tutorial: GitHub Source Code → Markdown

## Purpose

This page is one complete workflow: GitHub source code to the technical project, the test catalog and the coverage
matrix in Markdown, refreshed on every push.

Use this when living documentation is authored [directly in code](../reference/authoring-formats.md) — today's
documentation source; issues are planned ([Choosing a documentation source](../guides/choosing-a-documentation-source.md)).

Read before: [Build a pipeline](../guides/build-a-pipeline.md) · Next: [Document types](../guides/living-doc-document-types.md)

## Contents

- [1. Prepare the inputs](#1-prepare-the-inputs)
- [2. Add the workflow](#2-add-the-workflow)
- [3. What happens on each run](#3-what-happens-on-each-run)
- [4. Verify](#4-verify)
- [Related](#related)

## 1. Prepare the inputs

| Document type you want | What must be in the repo |
|---|---|
| [Technical project](../guides/living-doc-document-types.md#technical-project) | User Story headers in `.feature` files under `features/liv_doc_us/`, Functionality headers under `features/liv_doc_func/`, and Feature headers in PageObjects under `pages/`, in the [documented format](../reference/authoring-formats.md) |
| [Test catalog](../guides/living-doc-document-types.md#test-catalog) | Gherkin scenarios in the `.feature` files under `features/`, with `@AC:` tags |
| [Coverage matrix](../guides/living-doc-document-types.md#coverage-matrix) | Both of the above, with the scenarios tagging the headers' acceptance-criterion IDs |

Other folders work too: change the paths in the collect step. `func-paths` and `pages-paths` are optional; drop
either if the folder does not exist, since every configured folder must
([repository entry](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/doc_source/README.md#repository-entry)).

## 2. Add the workflow

`.github/workflows/living-doc.yml`:

```yaml
name: Living Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

# A newer push replaces a refresh still running, so two runs never push over each other.
concurrency:
  group: living-doc
  cancel-in-progress: true

jobs:
  living-doc:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v7

      # toolkit and generator-markdown need Python 3.10 or later on the runner
      - uses: actions/setup-python@v7
        with:
          python-version: '3.14'

      # 1. COLLECT the headers (doc-source) and the scenarios (ui-tests) into output/collector-gh/
      - name: Collect from source
        uses: AbsaOSS/living-doc-collector-gh@v0.2.0
        with:
          project-id: your-project
          doc-source: true
          doc-source-repositories: |
            [{"organization-name": "${{ github.repository_owner }}",
              "repository-name": "${{ github.event.repository.name }}",
              "us-paths": ["${{ github.workspace }}/features/liv_doc_us"],
              "func-paths": ["${{ github.workspace }}/features/liv_doc_func"],
              "pages-paths": ["${{ github.workspace }}/pages"]}]
          ui-tests: true
          ui-tests-repositories: |
            [{"organization-name": "${{ github.repository_owner }}",
              "repository-name": "${{ github.event.repository.name }}",
              "paths": ["${{ github.workspace }}/features"]}]

      # 2. NORMALIZE: one toolkit step per document, into output/toolkit/
      - name: Normalize the documentation
        uses: AbsaOSS/living-doc-toolkit@v0.1.0
        with:
          command: normalize-docs
          input: output/collector-gh/doc-source/doc-source.json
          output: output/toolkit/generator-ready.json
          view: release
      - name: Normalize the tests
        uses: AbsaOSS/living-doc-toolkit@v0.1.0
        with:
          command: normalize-tests
          input: output/collector-gh/ui-tests/ui-tests.json
          output: output/toolkit/ui-test-catalog.json
      - name: Join them into a coverage matrix
        uses: AbsaOSS/living-doc-toolkit@v0.1.0
        with:
          command: coverage-matrix
          input: output/collector-gh/doc-source/doc-source.json
          tests-input: output/collector-gh/ui-tests/ui-tests.json
          output: output/toolkit/coverage-matrix.json
          view: release

      # 3. GENERATE one Markdown document per step, each with its run report, into docs/living-doc/
      - name: Render the technical project
        uses: AbsaOSS/living-doc-generator-markdown@v0.1.0
        with:
          document-type: technical-project
          source-path: output/toolkit/generator-ready.json
          output-path: docs/living-doc
      - name: Render the test catalog
        uses: AbsaOSS/living-doc-generator-markdown@v0.1.0
        with:
          document-type: ui-test-catalog
          source-path: output/toolkit/ui-test-catalog.json
          output-path: docs/living-doc
      - name: Render the coverage matrix
        uses: AbsaOSS/living-doc-generator-markdown@v0.1.0
        with:
          document-type: coverage-matrix
          source-path: output/toolkit/coverage-matrix.json
          output-path: docs/living-doc

      # 4. COMMIT each document together with its run report
      - name: Commit the documents
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add docs/living-doc
          git commit -m "docs: refresh living documentation" || echo "no changes"
          git push
```

Change `your-project` to your project's id
([Project id](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#project-id)).
To refresh nightly as well, add `schedule: [{cron: '0 4 * * *'}]` under `on:`.
The `inner` view keeps everything; drop both `view: release` lines to render it
([Rendering rules — Views](../reference/rendering-rules.md#views)).
Every input of each step: [`collector-gh`](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md#inputs),
[`toolkit`](https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/action.md#inputs),
[`generator-markdown`](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/docs/action.md#inputs).

## 3. What happens on each run

1. `collector-gh` parses the header blocks into `output/collector-gh/doc-source/doc-source.json` and the scenarios
   into `output/collector-gh/ui-tests/ui-tests.json`.
2. `toolkit` writes one file per document under `output/toolkit/`: `generator-ready.json`, `ui-test-catalog.json`
   and `coverage-matrix.json` ([Data flows — Commands](../reference/data-flows.md#commands)).
3. `generator-markdown` renders `technical-project.md`, `ui-test-catalog.md` and `coverage-matrix.md` into
   `docs/living-doc/`, each beside its `<document-type>.run-report.json`
   ([`generator-markdown` files](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/docs/action.md#files)).
4. The workflow commits `docs/living-doc/`: each document with its run report, which lists what the document shows,
   so the report's diff shows what changed. `output/` is not committed. A commit pushed with the job's token starts
   no new run.

## 4. Verify

After the first run, `docs/living-doc/` holds six files: three documents and their run reports. The technical project
lists your User Stories, the test catalog your scenarios, and the coverage matrix each criterion's verdict. A run
that warns or fails names a code: [Error codes](../reference/errors.md). The six documents these tags rendered over
the testbed, in both views, are in [`docs/_integration/MS3/testbed-core/`](../_integration/MS3/testbed-core/release/generator-markdown/technical-project.md).

## Related

- [GitHub Issues → Markdown](gh-issues-to-markdown.md) — the same output from issues instead of code *(planned)*
- [GitHub Source → PDF](gh-source-to-pdf.md) — same inputs, PDF output *(planned)*
- [Authoring formats](../reference/authoring-formats.md) — the source-code format being mined
- [Living Documentation Document Types](../guides/living-doc-document-types.md)
