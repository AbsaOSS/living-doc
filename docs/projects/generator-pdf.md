# living-doc-generator-pdf

**Repo:** [github.com/AbsaOSS/living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf)
**Role:** Generator
**Type:** GitHub Action

## Purpose

Renders the canonical dataset into professional PDF documents using customizable Jinja2 templates and WeasyPrint, with built-in support for user stories, UI test catalogs, and coverage matrices.

## Inputs / Outputs

- **Input:** the canonical dataset produced by [living-doc-toolkit](toolkit.md) (`source-path`), plus a `document-type` selector (`user-stories` · `ui-test-catalog` · `coverage-matrix`)
- **Output:** PDF, rendered via a Jinja2 template + WeasyPrint

For the exact action inputs and the current built-in template set, see the [project README](https://github.com/AbsaOSS/living-doc-generator-pdf).

## Where it fits

Final stage of the pipeline — the option to reach for when the deliverable needs to be a shareable/archivable document rather than a browsable site. See [Architecture](../introduction/architecture.md).

## Used in

- [Choosing a Generator](../guides/choosing-a-generator.md)
- [User Stories → PDF](../tutorials/user-stories-to-pdf.md)
- [GitHub Source Code → PDF](../tutorials/gh-source-to-pdf.md)
