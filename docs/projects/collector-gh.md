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

First collection stage of the pipeline — feeds [living-doc-toolkit](toolkit.md) or a generator directly (e.g. [generator-mdoc](generator-mdoc.md)). Upstream of it, [agentic-toolkit](agentic-toolkit.md)'s `living-doc-bdd-copilot` agent is what authors the User Story/Feature/Functionality entities and `.feature` files this collector's `doc-issues`/`doc-source`/`ui-tests` modes are designed to mine — see [Architecture](../introduction/architecture.md) and [Data Flows & Schemas spec](../specs/data-flows.md) §9 for how closely (and, in places, how not-yet-closely) the two formats currently match.

## Used in

- [Collecting from GitHub](../guides/github-collection.md)
- [GitHub Issues → Markdown](../tutorials/gh-issues-to-markdown.md)
- [GitHub Issues → MDoc](../tutorials/gh-issues-to-mdoc.md)
- [User Stories → PDF](../tutorials/user-stories-to-pdf.md)
