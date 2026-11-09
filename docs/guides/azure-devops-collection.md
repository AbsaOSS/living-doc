# Collecting from Azure DevOps

## Purpose

This page is what collecting from Azure DevOps will be: a planned documentation source, authored in the same layout
as a GitHub issue body, with tests that may still come from GitHub.

Read before: [Choosing a documentation source](choosing-a-documentation-source.md) · Next: [Build a pipeline](build-a-pipeline.md)

## Contents

- [Status](#status)
- [What it collects](#what-it-collects)
- [When to use it](#when-to-use-it)
- [Authoring in Azure DevOps](#authoring-in-azure-devops)
- [Feeding it forward](#feeding-it-forward)

## Status

**Planned:** Azure DevOps work items as a documentation source are not in the `v0.1.0` pipeline, and no pipeline here runs `living-doc-collector-ad`; their layout is fixed already: [GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout).

## What it collects

[living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad) mines an Azure DevOps organization for
work items and emits JSON.

- Work items (title, description, state, type, assigned board/area): the `work-items` mode.
- Boards, pipelines, test plans and release notes are planned modes, specced in the
  [project README](https://github.com/AbsaOSS/living-doc-collector-ad), not yet built.

Its inputs and outputs: the [project README](https://github.com/AbsaOSS/living-doc-collector-ad).

## When to use it

Once it lands: when work is tracked in Azure DevOps rather than in source code, and you want the same
generated-documentation experience from that data.

## Authoring in Azure DevOps

A work item is authored with the same `##` sections as a GitHub issue body
([Authoring formats — Azure DevOps work items](../reference/authoring-formats.md#azure-devops-work-items)).
The tests may still come from GitHub: `living-doc-collector-gh`'s `ui-tests` mode mines the `.feature` files of any
repository of the same project ([Tests from another system](choosing-a-documentation-source.md#tests-from-another-system)).

## Feeding it forward

Like the GitHub collector, its output will pass through [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit)'s
normalize step next — generators consume `toolkit`'s canonical dataset, not raw collector output. A pipeline never
combines Azure DevOps and GitHub documentation: it mines one documentation source
([One project, one pipeline, one documentation source](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#one-project-one-pipeline-one-documentation-source)).
