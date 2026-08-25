# living-doc-generator-markdown

**Repo:** [github.com/AbsaOSS/living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown)
**Role:** Generator
**Type:** GitHub Action
**Status:** Early stage — the repository does not yet have implementation beyond its initial template; treat inputs/outputs below as directional, not authoritative.

## Purpose

Renders the canonical Living Documentation dataset as plain Markdown files — output meant to be committed alongside code and rendered by whatever already renders a repo's Markdown (GitHub, a wiki, a generic static site generator).

## Where it fits

Final stage of the pipeline, consuming output from [living-doc-toolkit](toolkit.md) (or a collector directly). See [Architecture](../introduction/architecture.md).

## Used in

- [Choosing a Generator](../guides/choosing-a-generator.md)
- [GitHub Issues → Markdown](../tutorials/gh-issues-to-markdown.md)
- [Azure DevOps Work Items → Markdown](../tutorials/ado-workitems-to-markdown.md)
