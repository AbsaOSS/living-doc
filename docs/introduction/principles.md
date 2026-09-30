# Principles

## Purpose

The fixed frame of the Living Documentation ecosystem: what each part is for, what it must not do,
and the one place where the frame deliberately bends. Every change to any `living-doc-*` repository
is checked against this page — a pull request either stays inside the frame or names the exception
it adds (see [Checking a change against the frame](#checking-a-change-against-the-frame)).

## Contents

- [The frame](#the-frame)
- [Non-goals](#non-goals)
- [Deliberate exceptions](#deliberate-exceptions)
- [Checking a change against the frame](#checking-a-change-against-the-frame)

## The frame

| Id | Part | Does | Does not |
|---|---|---|---|
| **F1** | Entities | User Story, Feature, Functionality and Acceptance Criterion, each with a defined header format — see [Living Doc Glossary](../guides/living-doc-glossary.md) and [Living Doc Header Types](../guides/living-doc-header-types.md). | Carry meaning outside a typed header field — `## Notes` drives nothing. |
| **F2** | Collectors | Mine entity headers from issues / work items or from source code, and collect auditable data from the source system (tracker state, audit events, project state) as provenance for later use. | Interpret, merge or compute — a collector records what the source says. |
| **F3** | Toolkit | Carries every technical transformation between collector output and generator input: normalisation, validation, filtering and cross-referencing — including the coverage matrix. | Render output or talk to a source system. |
| **F4** | Generators | Convert a toolkit output into one target format (Markdown, PDF). | Transform or enrich data — a generator reads only toolkit outputs. |
| **F5** | Utilities | Share logic between repositories: the contract models, their generated schemas, and the authoring-format parsers. | Hold a pipeline stage of its own. |
| **F6** | Agentic | Accelerates authoring with AI agents and skills: entity headers and the BDD tests bound to them, including the test surface those tests need (PageObjects, test ids, gap reports). | Run in the pipeline — the pipeline is AI-free, and everything an agent writes can be written by hand. |
| **F7** | Pydantic models | Bind the rules: every contract is a Pydantic model, and its JSON Schema is generated from it. | Have a hand-written twin — no component mirrors a model or commits a schema copy. |

## Non-goals

- No part does more than its row in [The frame](#the-frame) says. Anything beyond it is either
  listed in [Deliberate exceptions](#deliberate-exceptions) or is drift.
- No inference from free text, tracker state or naming — behaviour comes only from typed fields.
- No AI anywhere downstream of authoring.

## Deliberate exceptions

| Id | Exception | Bends | Why |
|---|---|---|---|
| **E1** | A Feature's state and deprecation date are derived from its Functionalities, never authored. | F2, F3 — a value the author did not write appears in the dataset. | A Feature is the structural node of a surface; its behaviour lives in its Functionalities, so an authored Feature state would contradict them. Rule: [Living Doc Glossary — Feature](../guides/living-doc-glossary.md#feature). |

An exception is added only together with the pull request that introduces it, and removed when the
behaviour goes.

## Checking a change against the frame

Every pull request in the ecosystem carries one acceptance criterion: **the change stays inside the
frame, or it names the frame row it bends and adds that exception to this page.** The
[pull request template](../../.github/pull_request_template.md) asks for it, and review flags a
change that adds responsibility to a part without doing so.
