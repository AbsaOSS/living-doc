# Tutorial: Technical Project → PDF

## Purpose

This page is the tutorial GitHub issues → PDF will be once GitHub issues as a documentation source and PDF output
land.

## Contents

- [Status](#status)
- [What it will produce](#what-it-will-produce)
- [Related](#related)

## Status

**Planned:** GitHub issues as a documentation source and PDF output are not in the `v0.1.0` pipeline, so this page carries no workflow; the issue layout is fixed already: [GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout). Today, use [GitHub Source Code → Markdown](gh-source-to-markdown.md).

## What it will produce

A PDF report — a technical project, a UI test catalog or a coverage matrix — from collected issue data, to share
or archive as a deliverable:

1. `collector-gh`'s `doc-issues` mode will mine the issues into `doc-entities.json`
   ([Data flows — Planned](../reference/data-flows.md#planned)).
2. `toolkit` will normalize that into the file a generator reads.
3. `living-doc-generator-pdf` will render it with the template set its document type selects (`technical-project`,
   `ui-test-catalog` or `coverage-matrix`), and the workflow will upload the PDF as a workflow artifact
   ([generator-pdf](../projects/generator-pdf.md)).

A PDF is typically a point-in-time deliverable, so such a workflow runs by hand rather than on every push. The
template set, and how to customize a template: the
[project README](https://github.com/AbsaOSS/living-doc-generator-pdf).

## Related

- [Collecting from GitHub](../guides/github-collection.md)
- [Build a pipeline — Choose a generator](../guides/build-a-pipeline.md#choose-a-generator)
