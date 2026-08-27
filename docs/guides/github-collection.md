# Collecting from GitHub

[living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) is a GitHub Action that mines a repository into the JSON shape the rest of the ecosystem consumes. It has three independently toggleable modes — enable one or several in the same workflow step.

## What it collects

- **Documentation Issues** (`doc-issues`): issue title, body, labels, state, and audit history for issues used as standalone documentation tickets — optionally enriched with linked **GitHub Projects** state.
- **Documentation Source** (`doc-source`): User Story / Feature / Functionality header blocks from repository source code — in `.feature` files and TypeScript PageObject files. See [Living Doc Header Types](living-doc-header-types.md) for the format.
- **UI Tests** (`ui-tests`): Gherkin test scenarios from `.feature` files, as a test catalog keyed by `@US_ID` / `@AC` tags.

See [living-doc-collector-gh](../projects/collector-gh.md) for the mode-by-mode breakdown.

## When to use it

Use this collector when your project tracks living documentation — User Stories, Features, and Functionalities — as:

- Issues (optionally organized in GitHub Projects)
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

Each mode is enabled by its own boolean input (`doc-issues`, `doc-source`, `ui-tests`) paired with a repository list (`doc-issues-repositories`, and so on); the snippet above is the issue-collection shorthand. Refer to the [project README](https://github.com/AbsaOSS/living-doc-collector-gh) for the current, authoritative list of inputs and outputs — they evolve with the action.

## Feeding it forward

Collector output is JSON. It always passes through [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit)'s normalize step next — generators consume toolkit's canonical dataset, not raw collector output. See [Architecture](../introduction/architecture.md).
