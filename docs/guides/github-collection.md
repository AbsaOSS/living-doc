# Collecting from GitHub

[living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) is a GitHub Action that mines a repository's issues into the JSON shape the rest of the ecosystem consumes.

## What it collects

- Issues: issue title, issue body.
- Source code: User Story / Feature / Functionality header blocks, Gherkin test scenarios (`.feature` files) — see [Living Doc Header Types](living-doc-header-types.md) for the format.

## When to use it

Use this collector when your project tracks living documentation — User Stories, Features, and Functionalities — as:

- Issues
- Source code, including Gherkin test scenarios (`.feature` files)

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

Collector output is JSON. It always passes through [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit)'s normalize step next — generators consume toolkit's canonical dataset, not raw collector output. See [Architecture](../introduction/architecture.md).
