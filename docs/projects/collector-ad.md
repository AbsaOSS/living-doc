# living-doc-collector-ad

## Purpose

This page is the card of `living-doc-collector-ad`, the Azure DevOps collector: its role, what it reads and writes,
and where its pages are.

- **Status:** planned as a documentation source; not in the `v0.1.0` pipeline
  ([Collecting from Azure DevOps](../guides/azure-devops-collection.md)).
- **Role:** collector, a GitHub Action: the first stage for a project whose documentation lives in Azure DevOps.
- **Reads:** an Azure DevOps organization's work items through its API, with an access token: the `work-items`
  mode. Boards, pipelines, test plans and release notes are planned modes, specced but not built.
- **Writes:** JSON describing the work items: `doc-entities.json` once [living-doc-toolkit](toolkit.md) reads it
  ([Data flows — Planned](../reference/data-flows.md#planned)).
- **Pages:** [README](https://github.com/AbsaOSS/living-doc-collector-ad), its current inputs and outputs.
