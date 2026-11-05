# Tutorial: Azure DevOps Work Items → Markdown

## Purpose

This page is the tutorial Azure DevOps work items → Markdown will be once Azure DevOps as a documentation source
lands.

## Contents

- [Status](#status)
- [What it will produce](#what-it-will-produce)
- [Documentation from Azure DevOps, tests from GitHub](#documentation-from-azure-devops-tests-from-github)
- [Related](#related)

## Status

**Planned:** Azure DevOps work items as a documentation source are not in the `v0.1.0` pipeline, so this page carries no workflow; their layout is fixed already: [GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout). Today, use [GitHub Source Code → Markdown](gh-source-to-markdown.md).

## What it will produce

Markdown files from Azure DevOps work items, refreshed on a schedule:

1. `living-doc-collector-ad` will mine the work items into `doc-entities.json`
   ([Data flows — Planned](../reference/data-flows.md#planned)).
2. `toolkit` will normalize that into the file a generator reads.
3. `generator-markdown` will render the technical project, `technical-project.md` with its run report, and the
   workflow will commit any changes.

## Documentation from Azure DevOps, tests from GitHub

A project takes its documentation from one source only. Azure DevOps will be that source, and the test catalog may
still come from GitHub: `collector-gh`'s `ui-tests` mode mines the `.feature` files of any repository of the same
project ([Tests from another system](../guides/choosing-a-documentation-source.md#tests-from-another-system)). Two
documentation sources are never merged ([one documentation source per pipeline](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#one-project-one-pipeline-one-documentation-source)).

## Related

- [Collecting from Azure DevOps](../guides/azure-devops-collection.md)
- [Build a pipeline](../guides/build-a-pipeline.md)
