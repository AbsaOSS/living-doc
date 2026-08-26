# Collecting from GitHub

[living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) is a GitHub Action that mines a repository's issues, labels, and other metadata into the JSON shape the rest of the ecosystem consumes.

## What it collects

- Issues (title, body, state, assignees, milestones)
- Labels (including any structured/semantic labels used to categorize documentation content)
- Repository metadata needed to attribute and link generated output back to source issues

## When to use it

Use this collector when your project tracks work — features, bugs, user stories — as GitHub issues, and you want documentation (Markdown or PDF reports) generated from that backlog.

## Basic setup

Add it as a step in a workflow (see [Getting Started](getting-started.md) for a full pipeline example):

```yaml
- name: Collect from GitHub
  uses: AbsaOSS/living-doc-collector-gh@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    repository: ${{ github.repository }}
```

Refer to the [project README](https://github.com/AbsaOSS/living-doc-collector-gh) for the current, authoritative list of inputs and outputs — they evolve with the action.

## Feeding it forward

Collector output is JSON. Pass it directly to a generator, or through [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) first if you need to normalize it alongside another source. See [Architecture](../introduction/architecture.md).
