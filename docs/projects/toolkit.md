# living-doc-toolkit

## Purpose

This page is the card of `living-doc-toolkit`, the normalizer: its role, what it reads and writes, and where its
pages are.

- **Role:** normalizer, a GitHub Action and a Python CLI: the middle stage. It carries every transformation between
  a collector's file and a generator's: normalisation, validation, the view filter and cross-referencing, so a
  generator needs no source-specific logic.
- **Commands**, one step each:
  - `normalize-docs`: `doc-source.json` → `generator-ready.json`, in the inner or the release view;
  - `normalize-tests`: `ui-tests.json` → `ui-test-catalog.json`;
  - `coverage-matrix`: `doc-source.json` and `ui-tests.json` → `coverage-matrix.json`.
- **Reads:** the files [living-doc-collector-gh](collector-gh.md) writes: one documentation file, from the
  project's one documentation source, and its tests file.
- **Writes:** the three files [living-doc-generator-markdown](generator-markdown.md) renders
  ([Data flows — Commands](../reference/data-flows.md#commands)).
- **Pages:** [README](https://github.com/AbsaOSS/living-doc-toolkit) and its
  [action reference](https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/action.md).
