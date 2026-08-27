# Spec: Example Input Files for Mining

**Status:** Draft — 2026-08-27
**Related:** [Living Doc Glossary](../guides/living-doc-glossary.md), [Living Doc Header Types](../guides/living-doc-header-types.md), [Living Documentation Document Types](../guides/living-doc-document-types.md), [Data Flows & Schemas](data-flows.md)

## 1. Why this exists

Every format in this repo is described in prose (glossary, header types) but the repo ships **no
concrete example a reader can copy**. A contributor setting up a pipeline, or an implementer building
`collector-gh`'s `doc-source` / `ui-tests` modes, has to reconstruct a valid file from the field
tables. This spec defines a small, canonical set of **example input files** — the things a collector
mines, not the documents a generator produces — that live in the repo and are referenced from the
guides.

Scope note: these are *inputs* only. Generated Markdown/PDF output is not checked in as an example —
it changes with every generator version and is reproducible from these inputs.

## 2. Where they live

```
docs/examples/
  gh-issues/            # issue-body content, one file per level
    us-001-customer-login.md
    feat-001-login-page.md
    func-001-validate-password-strength.md
  gherkin/              # .feature files, for doc-source / ui-tests mining
    liv_doc_us/us-001-customer-login.feature
    liv_doc_func/func-001-validate-password-strength.feature
  pageobject/           # PageObject header example (Feature in a PageObject file)
    LoginPage.ts
  project-profile/      # tooling config + agent-memory examples
    .project-profile.yaml
    seed.yaml
```

Each example is deliberately minimal — one of each entity, one or two ACs, enough to show every
required field and one optional field, no more.

## 3. The catalog

| Example | Demonstrates | Feeds document type | Mined by | Format reference |
|---|---|---|---|---|
| `gh-issues/us-001-*.md` | A User Story as a GitHub issue body — actor/capability/value, AC block | Technical project | `collector-gh` `doc-issues` | [Header Types § User Story](../guides/living-doc-header-types.md#1-user-story-in-a-gherkin-feature-file) *(issue-body layout: pending — see §5)* |
| `gh-issues/feat-001-*.md` | A Feature as an issue body — surface type, owner, linked US | Technical project | `collector-gh` `doc-issues` | [Glossary § Feature](../guides/living-doc-glossary.md#feature) |
| `gh-issues/func-001-*.md` | A Functionality as an issue body — parent Feature, `func_type`, ACs | Technical project | `collector-gh` `doc-issues` | [Glossary § Functionality](../guides/living-doc-glossary.md#functionality-func) |
| `gherkin/liv_doc_us/us-001-*.feature` | A User Story feature file — full header block + one tagged scenario | Technical project (via `doc-source`) + test catalog (via `ui-tests`) | `collector-gh` `doc-source`, `ui-tests` | [Header Types § User Story](../guides/living-doc-header-types.md#1-user-story-in-a-gherkin-feature-file) |
| `gherkin/liv_doc_func/func-001-*.feature` | A Functionality feature file — header block + `@AC:` scenarios | Technical project + test catalog | `collector-gh` `doc-source`, `ui-tests` | [Header Types § Functionality](../guides/living-doc-header-types.md#3-functionality-in-a-gherkin-feature-file) |
| `pageobject/LoginPage.ts` | A full PageObject living-doc header | Technical project (Feature surface) | `collector-gh` `doc-source` | [Header Types § Feature in a PageObject File](../guides/living-doc-header-types.md#2-feature-in-a-pageobject-file) |
| `project-profile/.project-profile.yaml` | The config every skill reads | — (tooling) | — | [Header Types § Project Profile](../guides/living-doc-header-types.md#project-profile-config-driven-conventions) |
| `project-profile/seed.yaml` | Agent local memory shape | — (tooling) | — | [Header Types § seed.yaml](../guides/living-doc-header-types.md#seedyaml-business-seed) |

All examples use the same identifiers (`US-001`, `FEAT-001`, `FUNC-001`) so that, taken together,
they form **one coherent mini technical project** — and the two `.feature` files plus the entities
form a complete [coverage-matrix](../guides/living-doc-document-types.md#coverage-matrix) input (one
AC covered, one not, to show both verdicts).

## 4. Sync obligation

The example files encode the same format as [Living Doc Header Types](../guides/living-doc-header-types.md)
and [Living Doc Glossary](../guides/living-doc-glossary.md). When a field or rule on those pages
changes, the matching example must change in the same PR. Treat this the way the header-types page's
own "Source of truth" note treats the `agentic-toolkit` sync: one direction, canonical page wins.
A CI check (§6) should parse each example and fail on drift.

## 5. Open question — GitHub issue-body layout

The `.feature` / header-block format is fully specified in this repo. The **issue-body** format for a
US / Feature / Functionality authored as a GitHub issue (rather than in source code) is **not** —
`collector-gh`'s `doc-issues` mode defines it, and the authoritative description lives in that repo's
`doc_issues/` docs and `doc-issues-v1.0.0-schema.json`, not here. Before writing `gh-issues/*.md`,
confirm the expected heading set (the synonym table in `toolkit/docs/contracts.md` —
`description` / `business_value` / `preconditions` / `acceptance_criteria` / … — is the closest thing
to a spec today). If the issue-body layout turns out to be under-documented ecosystem-wide, that is a
finding for [Data Flows & Schemas § 9](data-flows.md#9-the-authoring-side-source-of-truth), and the
`gh-issues/` examples should be the artifact that pins it down.

## 6. Tasks

- [ ] Create `docs/examples/` with the tree in §2.
- [ ] Author the `.feature` examples first (format is fully specified here) — `us-001-customer-login.feature`, `func-001-validate-password-strength.feature`, one AC covered by a scenario and one AC left uncovered.
- [ ] Author `pageobject/LoginPage.ts` (full header) and `project-profile/` examples from the field tables in [Living Doc Header Types](../guides/living-doc-header-types.md).
- [ ] Resolve §5, then author the `gh-issues/*.md` examples.
- [ ] Link the relevant example from each format section of [Living Doc Header Types](../guides/living-doc-header-types.md) and from [Living Documentation Document Types](../guides/living-doc-document-types.md).
- [ ] Add a CI check that validates every example against its schema / header rules (parses, required fields present, IDs consistent across the set).
- [ ] Once `collector-gh`'s `doc-source` / `ui-tests` modes ship, add a CI job that runs the real collector over `docs/examples/gherkin/` and snapshot-tests the resulting JSON.
