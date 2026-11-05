# living-doc-generator-markdown

## Purpose

This page is the card of `living-doc-generator-markdown`, the Markdown generator: its role, what it reads and writes,
and where its pages are.

- **Role:** generator, a GitHub Action: the final stage. It renders one document per step as plain Markdown, meant
  to be committed alongside code and rendered by whatever already renders a repository's Markdown (GitHub, a wiki, a
  static site generator).
- **Document types**, each with the file it reads and the [living-doc-toolkit](toolkit.md) command that writes it:
  - `technical-project`: `generator-ready.json`, from `normalize-docs`;
  - `ui-test-catalog`: `ui-test-catalog.json`, from `normalize-tests`;
  - `coverage-matrix`: `coverage-matrix.json`, from `coverage-matrix`.
- **Reads** only a `toolkit` file, never raw collector output, and renders the view that file records.
- **Writes:** `<document-type>.md` and `<document-type>.run-report.json`, into `output/generator-markdown/` by
  default.
- **Pages:** [README](https://github.com/AbsaOSS/living-doc-generator-markdown) and its
  [action reference](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/docs/action.md).
