# Collecting from Azure DevOps

[living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad) mines an Azure DevOps organization for work items and emits the same JSON shape used across the ecosystem.

## What it collects

- Work items (title, description, state, type, assigned board/area)

Boards, pipelines, test plans, and release notes are planned collector modes — specced in the project README, not yet built. Azure DevOps scope for v1 is re-evaluated after the v1 pre-release (see [Roadmap](../specs/roadmap.md)).

## When to use it

Use this collector when work is tracked in Azure DevOps rather than GitHub issues, and you want the same generated-documentation experience — Markdown or PDF — from that data.

## Basic setup

```yaml
- name: Collect from Azure DevOps
  uses: AbsaOSS/living-doc-collector-ad@v1
  with:
    organization: my-ado-org
    project: my-project
    pat: ${{ secrets.ADO_PAT }}
```

Refer to the [project README](https://github.com/AbsaOSS/living-doc-collector-ad) for the current, authoritative list of inputs and outputs.

## Feeding it forward

Like the GitHub collector, the output is JSON that always passes through [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit)'s normalize step next — generators consume `toolkit`'s canonical dataset, not raw collector output. Normalizing is also where Azure DevOps and GitHub data get combined into one documentation set. See [Architecture](../introduction/architecture.md).
