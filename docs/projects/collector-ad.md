# living-doc-collector-ad

**Repo:** [github.com/AbsaOSS/living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad)
**Role:** Collector
**Type:** Python tool

## Purpose

Extracts project metadata from Azure DevOps — work items, boards, and pipelines — and emits it as machine-readable JSON for the rest of the Living Documentation pipeline.

## Inputs / Outputs

- **Input:** an Azure DevOps organization/project (via PAT/API access)
- **Output:** JSON describing work items, boards, and pipeline metadata

For the exact, current list of inputs/outputs, see the [project README](https://github.com/AbsaOSS/living-doc-collector-ad).

## Where it fits

First stage of the pipeline — feeds [living-doc-toolkit](toolkit.md) or a generator directly. See [Architecture](../introduction/architecture.md).

## Used in

- [Collecting from Azure DevOps](../guides/azure-devops-collection.md)
- [Azure DevOps Work Items → Markdown](../tutorials/ado-workitems-to-markdown.md)
