# living-doc-toolkit

**Repo:** [github.com/AbsaOSS/living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit)
**Role:** Normalizer
**Type:** Python CLI services

## Purpose

Transforms and normalizes collector output into a single canonical dataset that generators consume — acting as the generic builder step between "raw data from one source" and "data ready to render."

## Why it exists

Collectors from different sources (GitHub, Azure DevOps) don't naturally agree on shape or coverage. The toolkit reconciles them into one canonical dataset so a generator doesn't need source-specific logic.

## Inputs / Outputs

- **Input:** JSON output from one or more collectors
- **Output:** canonical dataset, ready for a generator

For the exact CLI usage and current data contract, see the [project README](https://github.com/AbsaOSS/living-doc-toolkit).

## Where it fits

Middle stage of the pipeline. See [Architecture](../introduction/architecture.md).

## Used in

- [Getting Started](../guides/getting-started.md)
- [Azure DevOps Work Items → Markdown](../tutorials/ado-workitems-to-markdown.md) (when combining sources)
