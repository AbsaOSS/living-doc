# agentic-toolkit

**Repo:** [github.com/AbsaOSS/agentic-toolkit](https://github.com/AbsaOSS/agentic-toolkit)
**Role:** Authoring acceleration (optional — AI agent + skills)
**Type:** AI Agent Skills library (Copilot/Claude/Cursor-compatible)

> **Not a dependency.** The Living Documentation pipeline (collect → normalize → generate) runs entirely AI-free — every `living-doc-*` repo is deterministic Python/JSON/template tooling. `agentic-toolkit` accelerates the one step upstream of all of it (authoring User Stories, Features, Functionalities, and their Gherkin scenarios); a human writing the identical content by hand is an equally valid, fully-supported path. See [Architecture](../specs/architecture.md) §4.5.

## Purpose

A general-purpose, curated library of AI-agent skills for software engineering — most of it (`pr-review`, `test-unit-write`, `python-standards`, `token-saving`, …) is generic practice, unrelated to Living Documentation. One skill family within it is directly part of this ecosystem: the `@living-doc-bdd-copilot` agent, which dispatches across 12 task skills plus one non-task companion skill, `shared` (the canonical entity-ID and AC-tag grammar every other skill in the family imports).

That agent is what an engineer runs to **author** User Story, Feature, and Functionality entities and their Gherkin `.feature` files — using the same entity-ID scheme (`US-<nnn>`, `FEAT-<nnn>`, `FUNC-<nnn>`), the same `liv_doc_us`/`liv_doc_func` directory convention, and the same `@AC:` tag grammar that [living-doc-collector-gh](collector-gh.md)'s planned `doc-source` and `ui-tests` modes are designed to mine. In other words: it's the stage upstream of everything else in this ecosystem — content gets authored here before any collector ever mines it.

## Where it fits

First stage of the pipeline, upstream of [collector-gh](collector-gh.md). See [Architecture](../specs/architecture.md) §4.5.

## Why it matters to this ecosystem specifically

Its `skills/shared/references/living-doc-glossary.md` and `living-doc-bdd-schemas.md` are the current, actively-maintained description of the entity/AC/header-block format — more complete than `living-doc-collector-gh/SPEC.md`'s version of the same thing (missing fields: `not_in_scope`, AC-level precondition extensions, deprecation metadata, the `@AC:<id>/aspect:<value>` tag param syntax, and any mining path for Functionality-level header blocks). See [Data Flows & Schemas](../specs/data-flows.md) §9 for the full comparison.

## Used in

- [Architecture](../specs/architecture.md) §4.5
- [Data Flows & Schemas](../specs/data-flows.md) §9
- [Roadmap](../specs/roadmap.md) Phase 2 (the format-reconciliation task)
