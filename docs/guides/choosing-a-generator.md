# Choosing a Generator

All generators consume the same upstream data (canonical dataset or, in one case, collector output directly) and differ only in what they render. Pick based on where the output needs to live.

| Generator | Output | Best for | Status |
|---|---|---|---|
| [living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown) | Plain `.md` files | Docs committed alongside code, rendered by whatever already renders your repo's Markdown (GitHub, a wiki, a generic static site generator). | Early stage — API not yet stable. |
| [living-doc-generator-mdoc](https://github.com/AbsaOSS/living-doc-generator-mdoc) | Markdown formatted for an MDoc viewer | A dedicated, browsable documentation site with MDoc-specific navigation/structure, generated straight from GitHub issues and labels. | **Deprecated** — was an ABSA-internal solution, no longer supported. |
| [living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf) | PDF | Point-in-time deliverables: user stories, UI test catalogs, coverage matrices — documents meant to be shared or archived as a file, not browsed as a site. | Available. |

## Decision guide

- **Need something to browse online, structured like a docs site?** → `generator-mdoc` is deprecated (ABSA-internal, no longer supported); `generator-markdown` is the closest actively-supported alternative today.
- **Need docs to live as plain files in a repo, editable/diffable like code?** → `generator-markdown` (note: still early stage).
- **Need a static, shareable document — a report, a sign-off artifact?** → `generator-pdf`.

Nothing stops you from running more than one generator off the same collected data if you need multiple output formats for the same source — see [Architecture](../introduction/architecture.md).
