# living-doc-collector-ad

**Repo:** [github.com/AbsaOSS/living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad)
**Role:** Collector
**Type:** Python tool

## Purpose

Extracts project metadata from Azure DevOps and emits it as machine-readable JSON for the rest of the Living Documentation pipeline. The `work-items` mode is implemented; `boards`, `pipelines`, `test_plans`, and `release_notes` are planned modes, specced but not yet built — Azure DevOps scope for v1 is re-evaluated after the v1 pre-release (see [Roadmap](../specs/roadmap.md)).

## Inputs / Outputs

- **Input:** an Azure DevOps organization/project (via PAT/API access)
- **Output:** JSON describing work items

For the exact, current list of inputs/outputs, see the [project README](https://github.com/AbsaOSS/living-doc-collector-ad).

## Where it fits

First stage of the pipeline — its JSON output feeds [living-doc-toolkit](toolkit.md), which normalizes it into the canonical dataset generators consume. See [Architecture](../introduction/architecture.md).

## Used in

- [Collecting from Azure DevOps](../guides/azure-devops-collection.md)
- [Azure DevOps Work Items → Markdown](../tutorials/ado-workitems-to-markdown.md)
