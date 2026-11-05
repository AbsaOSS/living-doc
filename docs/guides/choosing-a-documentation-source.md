# Choosing a documentation source

## Purpose

This page is how to choose the one documentation source a project's pipeline mines: source headers today, GitHub
issues and Azure DevOps once they land, where the tests may come from, and how to move a project onto one source.

Read before: [Living Documentation in 5 Minutes](../introduction/quickstart.md) · Next: [Build a pipeline](build-a-pipeline.md)

## Contents

- [One source per project](#one-source-per-project)
- [Source headers](#source-headers)
- [GitHub issues (planned)](#github-issues-planned)
- [Azure DevOps (planned)](#azure-devops-planned)
- [Tests from another system](#tests-from-another-system)
- [Moving a project to one source](#moving-a-project-to-one-source)
- [When sources mix](#when-sources-mix)

## One source per project

A pipeline documents one project. It mines that project's User Stories, Features and Functionalities from exactly
one documentation source, and its tests may come from elsewhere. A coverage matrix joins the two on their IDs, so an
ID must mean one entity everywhere it appears.

- The rule: [One project, one pipeline, one documentation source](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#one-project-one-pipeline-one-documentation-source).
- Why colliding IDs cannot be reconciled after mining: [Glossary — ID uniqueness](../reference/glossary.md#id-uniqueness).

| Source | Mined by | Status |
|---|---|---|
| Headers in source code: User Stories and Functionalities in `.feature` files, Features in PageObjects | `living-doc-collector-gh`, `doc-source` mode | Available |
| GitHub issues labelled as User Story, Feature or Functionality | `living-doc-collector-gh`, `doc-issues` mode | Planned |
| Azure DevOps work items | `living-doc-collector-ad` | Planned |

## Source headers

Today's documentation source. Each entity is a header block in a file your repository already holds, so it changes
in the same commit as the code it documents.

- The exact layouts: [Authoring formats](../reference/authoring-formats.md).
- How to write one the pipeline reads as you meant it: [Authoring documentation](authoring-documentation.md).
- One `living-doc-collector-gh` step mines every repository of the project, one entry each
  ([Collecting from GitHub](github-collection.md)).

## GitHub issues (planned)

**Planned:** GitHub issues as a documentation source are not in the `v0.1.0` pipeline; their layout is fixed already: [GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout).

The `doc-issues` mode that will mine them fails a run at start in this version. What it will write:
[Data flows — Planned](../reference/data-flows.md#planned).

## Azure DevOps (planned)

**Planned:** Azure DevOps work items as a documentation source are not in the `v0.1.0` pipeline; a work item will follow the [GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout).

How a work item maps onto that layout: [Authoring formats — Azure DevOps work items](../reference/authoring-formats.md#azure-devops-work-items).
What collecting from it will look like: [Collecting from Azure DevOps](azure-devops-collection.md).

## Tests from another system

The test catalog is mined from Gherkin scenarios in `.feature` files by `living-doc-collector-gh`'s `ui-tests` mode.
Those files may sit in any repository of the same project, apart from the documentation source.

- Once Azure DevOps lands, a project may take its documentation from Azure DevOps and its tests from GitHub.
- The scenarios tag the documentation source's acceptance-criterion IDs, so the coverage matrix can join them
  ([Document types — Coverage matrix](living-doc-document-types.md#coverage-matrix)).

## Moving a project to one source

A project whose entities live in two places, for example some as headers and some as issues, moves onto one:

1. Choose the source. In `v0.1.0` that is source headers.
2. Move each entity into it, keeping its ID and its criteria's IDs, so the test tags still match.
3. Delete the old copy. Do not prefix or namespace IDs per source to dodge a collision
   ([ID uniqueness](../reference/glossary.md#id-uniqueness)).
4. List every repository of the project in the one collector step.

## When sources mix

The pipeline never picks a winner between two sources. It stops with a code instead; each code's meaning and remedy
are in [Error codes](../reference/errors.md#codes):

- `MULTIPLE_DOCUMENTATION_SOURCES`: the `toolkit` `coverage-matrix` step was given more than one documentation file.
- `MIXED_DOCUMENTATION_SOURCES` (planned): documentation from an issue tracker and from source files would meet in
  one run.
- `DUPLICATE_ENTITY_ID` and `DUPLICATE_AC_ID`: the same ID appears twice within the one source.
