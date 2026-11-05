# Tutorial: GitHub Issues → Markdown

## Purpose

This page is the tutorial GitHub issues → Markdown will be once GitHub issues as a documentation source land.

## Contents

- [Status](#status)
- [What it will produce](#what-it-will-produce)
- [Related](#related)

## Status

**Planned:** GitHub issues as a documentation source are not in the `v0.1.0` pipeline, so this page carries no workflow; their layout is fixed already: [GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout). Today, use [GitHub Source Code → Markdown](gh-source-to-markdown.md).

## What it will produce

The same documents as from source code, from a GitHub repository's issues, committed back into the repository:

1. `collector-gh`'s `doc-issues` mode will mine the issues and their labels into `doc-entities.json`
   ([Data flows — Planned](../reference/data-flows.md#planned)).
2. `toolkit` will normalize that into the file a generator reads.
3. `generator-markdown` will render the technical project, `technical-project.md` with its run report, matching the
   current state of your issue tracker.

The steps around the collector will be those of [GitHub Source Code → Markdown](gh-source-to-markdown.md).

## Related

- [Collecting from GitHub](../guides/github-collection.md)
- [Choosing a documentation source](../guides/choosing-a-documentation-source.md)
- [Architecture](../introduction/architecture.md)
