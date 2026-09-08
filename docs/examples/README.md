# Example Input Files for Mining

A canonical, minimal corpus of the **input** files the living-doc pipeline mines — the things a
collector reads, not the documents a generator produces. For the formats these files follow, see
[Living Doc Header Types](../guides/living-doc-header-types.md) and
[Living Doc Glossary](../guides/living-doc-glossary.md).

All examples describe **one coherent mini technical project** — `US-001` / `FEAT-001` / `FUNC-001` —
so that, taken together, the two `.feature` files plus the entities form a complete
[coverage-matrix](../guides/living-doc-document-types.md#coverage-matrix) input: one AC covered by a
scenario, one left uncovered, to show both verdicts.

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

## GitHub issue-body layout (canonical)

The `.feature` / header-block format is fully specified in
[Living Doc Header Types](../guides/living-doc-header-types.md). The **issue-body** format for an
entity authored as a GitHub issue (mined by `collector-gh` `doc-issues`) was previously
under-specified ecosystem-wide — the closest reference was the `toolkit/docs/contracts.md` synonym
table (`description` / `business_value` / `preconditions` / `acceptance_criteria` / …). The
[`gh-issues/`](gh-issues/) files pin it down:

- Each entity is one GitHub issue. Entity type and ID come from the issue **labels**
  (`US` / `Feature` / `Functionality`) and the issue **title** (`US-001 · Customer Login`) — not from
  body headings.
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

- **Minimal.** Each file carries every required field plus at most one optional field — just enough
  to show one field extension, no more.
- **Field extensions**, one per file, spread across the corpus:
  - feature-level `Not In Scope` — `gh-issues/us-001-customer-login.md`
  - AC-level `preconditions` extension — `gherkin/liv_doc_us/us-001-customer-login.feature`
  - `Aspect:` — `gherkin/liv_doc_func/func-001-validate-password-strength.feature`
- **Coverage pair.** `AC:US-001-01` and `AC:FUNC-001-01` are covered by scenarios;
  `AC:US-001-02` and `AC:FUNC-001-02` are declared but have no scenario.

## Sync obligation

These files encode the same format as [Living Doc Header Types](../guides/living-doc-header-types.md)
and [Living Doc Glossary](../guides/living-doc-glossary.md). When a field or rule on those pages
changes, the matching example here must change in the same PR.

When a collector mode that mines these inputs (`collector-gh` `doc-source` / `ui-tests`, `doc-issues`)
is implemented or changed, the PR that does so must re-check this corpus and the guides above against
what the tooling actually mines, and correct any drift in the same PR.
