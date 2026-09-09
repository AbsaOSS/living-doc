# Example Input Files for Mining

A canonical, minimal corpus of the **input** files the living-doc pipeline mines — the things a
collector reads, not the documents a generator produces. For the formats these files follow, see
[Living Doc Header Types](../guides/living-doc-header-types.md) and
[Living Doc Glossary](../guides/living-doc-glossary.md).

All examples describe **one coherent mini technical project** — `US-001` / `FEAT-001` / `FUNC-001` —
so that, taken together, the two `.feature` files plus the entities form a complete
[coverage-matrix](../guides/living-doc-document-types.md#coverage-matrix) input: in each `.feature`
file one AC is covered by a scenario and one is left uncovered, so the matrix shows both verdicts.

## Files

| Path | Format reference |
|---|---|
| [gherkin/liv_doc_us/us-001-customer-login.feature](gherkin/liv_doc_us/us-001-customer-login.feature) | [Header Types § User Story](../guides/living-doc-header-types.md#1-user-story-in-a-gherkin-feature-file) |
| [gherkin/liv_doc_func/func-001-validate-password-strength.feature](gherkin/liv_doc_func/func-001-validate-password-strength.feature) | [Header Types § Functionality](../guides/living-doc-header-types.md#3-functionality-in-a-gherkin-feature-file) |
| [pageobject/LoginPage.ts](pageobject/LoginPage.ts) | [Header Types § Feature in a PageObject File](../guides/living-doc-header-types.md#2-feature-in-a-pageobject-file) |
| [project-profile/.project-profile.yaml](project-profile/.project-profile.yaml) | [Header Types § Project Profile](../guides/living-doc-header-types.md#project-profile-config-driven-conventions) |
| [project-profile/seed.yaml](project-profile/seed.yaml) | [Header Types § seed.yaml](../guides/living-doc-header-types.md#seedyaml-business-seed) |
| [gh-issues/us-001-customer-login.md](gh-issues/us-001-customer-login.md) | [GitHub issue-body layout](#github-issue-body-layout-canonical) |
| [gh-issues/feat-001-login-page.md](gh-issues/feat-001-login-page.md) | [GitHub issue-body layout](#github-issue-body-layout-canonical) |
| [gh-issues/func-001-validate-password-strength.md](gh-issues/func-001-validate-password-strength.md) | [GitHub issue-body layout](#github-issue-body-layout-canonical) |

## What the corpus mines to (`_expected/`)

[`_expected/`](_expected/) holds the JSON this `gherkin/` corpus produces when the **real**
`living-doc-collector-gh` (`doc-source` + `ui-tests`) and `living-doc-toolkit` `coverage-matrix`
are run over it — `doc-source.json`, `ui-tests.json`, `coverage-matrix.json`, normalized so only
the mined content is compared. `.github/workflows/real-collector-snapshot.yml` regenerates them on
every PR touching `docs/examples/**` and fails on any diff, so a parser or schema change in the
pinned collector that alters the mined output surfaces here. These files double as a worked
reference for anyone integrating the collector. To regenerate after an intended change, see
[CONTRIBUTING.md § Regenerating the collector snapshots](../../CONTRIBUTING.md#regenerating-the-collector-snapshots).

## GitHub issue-body layout (canonical)

The `.feature` / header-block format is fully specified in
[Living Doc Header Types](../guides/living-doc-header-types.md). The **issue-body** format for an
entity authored as a GitHub issue (mined by `collector-gh` `doc-issues`) was previously
under-specified ecosystem-wide — the closest reference was the `toolkit/docs/contracts.md` synonym
table (`description` / `business_value` / `preconditions` / `acceptance_criteria` / …). The
[`gh-issues/`](gh-issues/) files pin it down:

- Each entity is one GitHub issue. Entity **type** comes from the issue **label** —
  `DocumentedUserStory` / `DocumentedFeature` / `DocumentedFunctionality`, the same values
  `collector-gh` writes into each item's `tags` — and the entity **ID** (`US-001` / `FEAT-001` /
  `FUNC-001`) from the prefix of the issue **title** (`US-001 · Customer Login`); neither is repeated
  as a body heading. (`collector-gh` also records every issue under its own `owner/repo#number` item
  ID; the entity ID above is what links the issue to the matching `.feature` file and PageObject.)
- Section headings are `##`-level and map 1:1 to the fields of the equivalent feature-file header;
  the heading text is the Title-Case form of the synonym-table key.
- AC blocks are `###` sub-headings using the same `AC:<id> (v<version> - <state>)` grammar as the
  [glossary](../guides/living-doc-glossary.md#acceptance-criterion-ac). Feature-level `Preconditions`
  / `Not In Scope` are inherited by all ACs; AC-level extensions go under the AC sub-heading.
- Anything outside this heading set is treated as free prose and ignored by the miner.

| Entity | Required headings | Optional headings |
|---|---|---|
| User Story | `## Description`, `## Business Value`, `## Acceptance Criteria` | `## Preconditions`, `## Not In Scope` |
| Feature | `## Description`, `## Surface Type`, `## Owners`, `## Status`, `## User Stories`, `## Functionalities` | `## External Dependencies` |
| Functionality | `## Description`, `## Parent Feature`, `## Func Type`, `## Acceptance Criteria` | `## Rationale`, `## Preconditions`, `## Not In Scope` |

## Conventions used by this corpus

- **Minimal.** Each entity file carries every required field plus one optional field — just enough to
  show one field extension, no more. (`.project-profile.yaml` is shown complete: it is pure config
  with no optional-field layer.)
- **Field extensions**, spread across the corpus so each is shown once in isolation — one per file,
  no file carrying two:
  - AC-level `preconditions` extension — `gherkin/liv_doc_us/us-001-customer-login.feature`
  - feature-level `Not In Scope` — `gh-issues/us-001-customer-login.md`
  - `External Dependencies` — `gh-issues/feat-001-login-page.md`
  - `Aspect:` on an AC — `gherkin/liv_doc_func/func-001-validate-password-strength.feature`
  - `Rationale` — `gh-issues/func-001-validate-password-strength.md`
- **`@domain_*` tag** — `.project-profile.yaml` sets `scenario_conventions.domain_tag: true`, and both
  `.feature` files carry `@domain_authentication` as the optional second feature-level tag.
- **Coverage pair.** `AC:US-001-01` and `AC:FUNC-001-01` are covered by scenarios;
  `AC:US-001-02` and `AC:FUNC-001-02` are declared but have no scenario (a deliberate gap, so the
  coverage matrix shows both the covered and the uncovered verdict).
- **Feature status vs surface status.** `FEAT-001` is an `active` entity (delivered, linked to
  `US-001`), while its PageObject *surface* is `status: candidate` — the login template is not yet
  instrumented for test automation. These are independent axes; see
  [Header Types § status: candidate](../guides/living-doc-header-types.md#2-feature-in-a-pageobject-file).

## Sync obligation

This corpus is part of the persisted product documentation and does not depend on any planning spec.
Two rules keep it truthful, both enforced **in the same PR** as the change that triggers them:

1. **Format change.** When a field or rule on [Living Doc Header Types](../guides/living-doc-header-types.md)
   or [Living Doc Glossary](../guides/living-doc-glossary.md) changes, update the matching example here.
2. **Implementation change (last check).** When a collector mode that mines these inputs
   (`collector-gh` `doc-source` / `ui-tests` / `doc-issues`) is implemented or changed, re-check this
   corpus **and** the guides above against what the tooling actually mines, and correct any drift.
   This is the checkpoint that catches divergence between the documented format and the shipped state.
