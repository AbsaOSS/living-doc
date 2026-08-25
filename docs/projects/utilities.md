# living-doc-utilities

**Repo:** [github.com/AbsaOSS/living-doc-utilities](https://github.com/AbsaOSS/living-doc-utilities)
**Role:** Shared library
**Type:** Python package

## Purpose

Provides the core data models and transformation/serialization logic shared across every collector, the toolkit, and every generator in the ecosystem — the contract that lets independently-built projects interoperate through one JSON shape.

## Where it fits

Not a pipeline stage on its own — it's a dependency of every other project. See [Architecture](../introduction/architecture.md) for how it underlies collect, normalize, and generate.

## Used by

- [collector-gh](collector-gh.md), [collector-ad](collector-ad.md)
- [toolkit](toolkit.md)
- [generator-markdown](generator-markdown.md), [generator-mdoc](generator-mdoc.md), [generator-pdf](generator-pdf.md)
