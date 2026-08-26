# living-doc-collector-gh

**Repo:** [github.com/AbsaOSS/living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh)
**Role:** Collector
**Type:** GitHub Action

## Purpose

Mines a GitHub repository for issues, labels, and other metadata, and emits it as machine-readable JSON for the rest of the Living Documentation pipeline.

## Inputs / Outputs

- **Input:** a GitHub repository (via token/API access)
- **Output:** JSON describing issues, labels, and associated metadata

For the exact, current list of action inputs/outputs, see the [project README](https://github.com/AbsaOSS/living-doc-collector-gh).

## Where it fits

First collection stage of the pipeline — feeds [living-doc-toolkit](toolkit.md) or a generator directly. Upstream of it, [agentic-toolkit](agentic-toolkit.md)'s `living-doc-bdd-copilot` agent is what authors the User Story/Feature/Functionality entities and `.feature` files this collector's `doc-issues`/`doc-source`/`ui-tests` modes are designed to mine, using the header format described in [Living Doc Header Types](../guides/living-doc-header-types.md). See [Architecture](../introduction/architecture.md) for where this collector sits in the pipeline.

## Used in

- [Collecting from GitHub](../guides/github-collection.md)
- [Living Doc Glossary](../guides/living-doc-glossary.md)
- [Living Doc Header Types](../guides/living-doc-header-types.md)
- [GitHub Issues → Markdown](../tutorials/gh-issues-to-markdown.md)
- [User Stories → PDF](../tutorials/user-stories-to-pdf.md)
