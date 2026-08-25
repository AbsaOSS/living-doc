# living-doc-generator-mdoc

**Repo:** [github.com/AbsaOSS/living-doc-generator-mdoc](https://github.com/AbsaOSS/living-doc-generator-mdoc)
**Role:** Generator
**Type:** GitHub Action

## Purpose

Generates living documentation in Markdown formatted for an MDoc viewer, extracting project data from GitHub repository issues and labels — producing a continuously updated, browsable documentation site.

## Inputs / Outputs

- **Input:** GitHub issue/label data (currently consumed directly, without a separate toolkit normalization step)
- **Output:** MDoc-viewer-formatted Markdown

For the exact, current list of action inputs/outputs, see the [project README](https://github.com/AbsaOSS/living-doc-generator-mdoc).

## Where it fits

Final stage of the pipeline. Unlike the other generators, it currently reads collector output directly rather than through [living-doc-toolkit](toolkit.md) — see the note in [Architecture](../introduction/architecture.md).

## Used in

- [Choosing a Generator](../guides/choosing-a-generator.md)
- [GitHub Issues → MDoc](../tutorials/gh-issues-to-mdoc.md)
