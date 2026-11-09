# living-doc-utilities

## Purpose

This page is the card of `living-doc-utilities`, the shared library: its role, what it holds, and where its pages
are.

- **Role:** shared library, a Python package: not a pipeline stage, but a dependency of every other repository, so
  independently built components interoperate through one JSON shape.
- **Holds:** the contract models of the six documentation contracts, their generated JSON Schemas and the code
  registry, and the authoring-format parsers with the acceptance-criterion grammar.
- **Used by:** [collector-gh](collector-gh.md), [collector-ad](collector-ad.md), [toolkit](toolkit.md),
  [generator-markdown](generator-markdown.md), [generator-pdf](generator-pdf.md).
- **Here:** the contracts, with the component that writes and reads each: [Contracts](../reference/contracts.md);
  the files they carry: [Data flows](../reference/data-flows.md); the codes it registers, with what to do about
  each: [Error codes](../reference/errors.md).
- **Pages:** [README](https://github.com/AbsaOSS/living-doc-utilities).
