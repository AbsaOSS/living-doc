# living-doc-generator-pdf

## Purpose

This page is the card of `living-doc-generator-pdf`, the PDF generator: its role, what it will read and write, and
where its pages are.

- **Status:** planned: PDF output is not in the `v0.1.0` pipeline.
- **Role:** generator, a GitHub Action: a final stage for a deliverable that must be a shareable or archivable
  document rather than a browsable page.
- **Reads:** the files [living-doc-toolkit](toolkit.md) writes, with a document type selecting the template:
  `technical-project`, `ui-test-catalog` or `coverage-matrix`.
- **Writes:** a PDF, rendered from customizable Jinja2 templates with WeasyPrint.
- **Pages:** [README](https://github.com/AbsaOSS/living-doc-generator-pdf), its action inputs and built-in
  template set.
