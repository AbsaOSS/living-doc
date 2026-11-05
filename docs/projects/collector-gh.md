# living-doc-collector-gh

## Purpose

This page is the card of `living-doc-collector-gh`, the GitHub collector: its role, what it reads and writes, and
where its pages are.

- **Role:** collector, a GitHub Action: the pipeline's first stage. It records what the source says, and interprets
  nothing.
- **Reads:** the repositories checked out earlier in the job: living-doc headers in `.feature` files and TypeScript
  PageObjects (`doc-source` mode), Gherkin scenarios in `.feature` files (`ui-tests` mode).
- **Writes:** `doc-source.json` and `ui-tests.json`, one per mode, under `output/collector-gh/<mode>/`, which
  [living-doc-toolkit](toolkit.md) reads.
- **Planned:** the `doc-issues` mode, mining GitHub issues, their labels and GitHub Projects state into
  `doc-entities.json`.
- **Format it mines:** [Authoring formats](../reference/authoring-formats.md), [Glossary](../reference/glossary.md).
- **Pages:** [README](https://github.com/AbsaOSS/living-doc-collector-gh) and its
  [action reference](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md); how to use it:
  [Collecting from GitHub](../guides/github-collection.md).
