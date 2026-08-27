# agentic-toolkit

**Repo:** [github.com/AbsaOSS/agentic-toolkit](https://github.com/AbsaOSS/agentic-toolkit)
**Role:** Authoring acceleration (optional — AI agent + skills)
**Type:** AI Agent Skills library (Copilot/Claude/Cursor-compatible)

> **Not a dependency.** The Living Documentation pipeline (collect → normalize → generate) runs entirely AI-free — every `living-doc-*` repo is deterministic Python/JSON/template tooling. `agentic-toolkit` accelerates the one step upstream of all of it (authoring User Stories, Features, Functionalities, and their Gherkin scenarios); a human writing the identical content by hand is an equally valid, fully-supported path. See [Architecture](../specs/architecture.md) §4.

## Purpose

A general-purpose, curated library of AI-agent skills for software engineering — most of it (`pr-review`, `test-unit-write`, `python-standards`, `token-saving`, …) is generic practice, unrelated to Living Documentation. One skill family within it is directly part of this ecosystem: the `@living-doc-bdd-copilot` agent, which dispatches across 12 task skills plus one non-task companion skill, `shared` (the canonical entity-ID and AC-tag grammar every other skill in the family imports).

That agent is what an engineer runs to **author** User Story, Feature, and Functionality entities and their Gherkin `.feature` files — using the same entity-ID scheme (`US-<nnn>`, `FEAT-<nnn>`, `FUNC-<nnn>`), the same `liv_doc_us`/`liv_doc_func` directory convention, and the same `@AC:` tag grammar that [living-doc-collector-gh](collector-gh.md)'s planned `doc-source` and `ui-tests` modes are designed to mine. In other words: it's the stage upstream of everything else in this ecosystem — content gets authored here before any collector ever mines it.

## Where it fits

First stage of the pipeline, upstream of [collector-gh](collector-gh.md). See [Architecture](../specs/architecture.md) §4.

## Why it matters to this ecosystem specifically

`living-doc` (this docs repo) is the source of truth for the entity/AC/header-block format the whole ecosystem shares: [Living Doc Glossary](../guides/living-doc-glossary.md) (entity definitions, IDs, AC/tag grammar) and [Living Doc Header Types](../guides/living-doc-header-types.md) (the three living-doc header types — **User Story in a Gherkin Feature File**, **Feature in a PageObject File**, **Functionality in a Gherkin Feature File** — plus the Project Profile and `seed.yaml`/`manifest.json`). `agentic-toolkit`'s non-task companion skill, `shared` (`skills/shared/references/living-doc-glossary.md` and `living-doc-bdd-schemas.md`), is synced from these two pages, and every other skill in the family imports it.

## Used in

- [Architecture](../specs/architecture.md)
- [Living Doc Glossary](../guides/living-doc-glossary.md)
- [Living Doc Header Types](../guides/living-doc-header-types.md)
- [Roadmap](../specs/roadmap.md) Phase 2 (implementing `collector-gh`'s `doc-source`/`ui-tests` modes against this format)
