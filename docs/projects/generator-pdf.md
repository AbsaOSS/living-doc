# living-doc-generator-pdf

**Repo:** [github.com/AbsaOSS/living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf)
**Role:** Generator
**Type:** GitHub Action

## Purpose

Transforms structured JSON into professional PDF documents using customizable Jinja2 templates and WeasyPrint, with built-in support for user stories, UI test catalogs, and coverage matrices.

## Inputs / Outputs

- **Input:** canonical dataset (or structured JSON matching a supported template's shape)
- **Output:** PDF, rendered via a Jinja2 template + WeasyPrint

For the current set of built-in templates and exact action inputs, see the [project README](https://github.com/AbsaOSS/living-doc-generator-pdf).

## Where it fits

Final stage of the pipeline — the option to reach for when the deliverable needs to be a shareable/archivable document rather than a browsable site. See [Architecture](../introduction/architecture.md).

## Used in

- [Choosing a Generator](../guides/choosing-a-generator.md)
- [User Stories → PDF](../tutorials/user-stories-to-pdf.md)
