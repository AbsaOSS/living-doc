# Collecting from Azure DevOps

[living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad) mines an Azure DevOps organization for work items, boards, and pipeline metadata, and emits the same JSON shape used across the ecosystem.

## What it collects

- Work items (title, description, state, type, assigned board/area)
- Boards (structure and item placement)
- Pipeline metadata

## When to use it

Use this collector when work is tracked in Azure DevOps rather than GitHub issues, and you want the same generated-documentation experience — Markdown, MDoc site, or PDF — from that data.

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

Like the GitHub collector, output is JSON consumed by a generator directly or normalized first via [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) — useful when a documentation set needs to combine Azure DevOps and GitHub data in one output. See [Architecture](../introduction/architecture.md).
