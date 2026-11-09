# Tutorial: GitHub Source Code → PDF

## Purpose

This page is the tutorial GitHub source code → PDF will be once PDF output lands.

## Contents

- [Status](#status)
- [What it will produce](#what-it-will-produce)
- [Related](#related)

## Status

**Planned:** PDF output is not in the `v0.1.0` pipeline, so this page carries no workflow ([generator-pdf](../projects/generator-pdf.md)). Today, use [GitHub Source Code → Markdown](gh-source-to-markdown.md).

## What it will produce

A **PDF** — a technical project, a UI test catalog or a coverage matrix — from the living-documentation header
blocks and Gherkin `.feature` files in your source tree:

1. The collect and normalize steps will be those of [GitHub Source Code → Markdown](gh-source-to-markdown.md),
   with the same inputs; only the generator step differs.
2. `living-doc-generator-pdf` will read a `toolkit` file, never raw collector output such as `ui-tests.json`, and
   render the template set its document type selects (`technical-project`, `ui-test-catalog` or `coverage-matrix`).
3. The workflow will upload the PDF as a workflow artifact; a publish or notify step can take it further.

The [coverage matrix](../guides/living-doc-document-types.md#coverage-matrix) needs **both** a technical project and
a test catalog for the same project, so the header blocks and the `.feature` files must use consistent AC IDs. A
technical project or test catalog on its own needs only its own inputs.

## Related

- [Technical Project → PDF](technical-project-to-pdf.md) — the same output from issues instead of code *(planned)*
- [GitHub Source → Markdown](gh-source-to-markdown.md) — same inputs, Markdown output
- [Build a pipeline — Choose a generator](../guides/build-a-pipeline.md#choose-a-generator)
- [Living Documentation Document Types](../guides/living-doc-document-types.md) — what each document contains and needs
