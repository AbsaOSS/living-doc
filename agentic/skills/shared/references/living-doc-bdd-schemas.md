<!-- generated from docs/reference/authoring-formats.md by agentic/scripts/sync-canon-copies.sh — do not edit -->
<!-- Generated file — do not edit by hand. CI re-runs the sync and fails on any diff. -->

# Authoring formats

## Purpose

This page defines the headers an author writes: the `.feature` User Story and Functionality headers, the
PageObject Feature header and the rules they share, then the layouts of two planned sources. Anyone can write a
header by hand; the optional agentic layer in [`agentic/`](https://github.com/AbsaOSS/living-doc/blob/master/agentic/README.md) writes the same format, and
keeps its own Project Profile, `seed.yaml` and `manifest.json` formats in
[agentic-formats.md](https://github.com/AbsaOSS/living-doc/blob/master/agentic/skills/shared/references/agentic-formats.md). The layer reads a copy generated
from this page, and a rule changed here changes its example in [`docs/examples/`](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/README.md) in the
[same PR](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/README.md#sync-obligation).

Read before: [Authoring documentation](https://github.com/AbsaOSS/living-doc/blob/master/docs/guides/authoring-documentation.md) · Next: [Glossary](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md)

## Contents

- [Repository adoption scope](#repository-adoption-scope)
- [Indentation](#indentation)
- [AC variants](#ac-variants)
- [1. User Story in a Gherkin Feature File](#1-user-story-in-a-gherkin-feature-file)
- [2. Feature in a PageObject File](#2-feature-in-a-pageobject-file)
- [3. Functionality in a Gherkin Feature File](#3-functionality-in-a-gherkin-feature-file)
- [GitHub issue-body layout](#github-issue-body-layout)
- [Azure DevOps work items](#azure-devops-work-items)

---

## Repository adoption scope

A repository does not have to adopt all three entity types. Pick the depth that matches how much
structure the team wants to maintain — each scope is a superset of the one above it:

| Scope | Headers you maintain | What it gives you |
|---|---|---|
| **User Stories only** | User Story feature file headers | Business requirements and their end-to-end acceptance criteria, tracked by version and status. No mapping to concrete system surfaces. |
| **User Stories + Features** | + Feature (PageObject) file headers | Every User Story is traced to the UI/API surfaces that satisfy it. Surfaces with no User Story and uncovered User Stories show up in gap reports. |
| **User Stories + Features + Functionalities** | + Functionality feature file headers | Full atomic-behavior coverage: each surface is broken into fast-testable Functionalities, each with its own ACs and system-test scenarios. |

Moving up a scope never invalidates what you already wrote — adding Features later does not change
existing User Story headers, and adding Functionalities does not change Feature headers.

---

## Indentation

Indentation is significant in every input you author: a `.feature` header, a PageObject header and
a GitHub issue body (see the [issue-body layout](#github-issue-body-layout)).
One rule covers all three:

**A line indented deeper than an open item's `- ` belongs to that item**, as wrapped text or as a
nested item. It is never a sibling of the item and never a new key.

- **Levels are relative.** A line only has to be deeper than its parent; no column is fixed. Indent
  with spaces. A tab or a no-break space in an indent is normalised to spaces when the input is read.
- **Flat layout.** Items written at their key's own indent stay valid and are read in line order.
- **Canonical levels in the corpus.** The example corpus uses the canonical levels only; the flat
  layout stays valid for authors.
- **Nesting.** A nested item may sit in a bullet-list field (`business_value`, `preconditions`,
  `not_in_scope`, `rationale`, `notes`), never in an id-list field (`user_stories`, `functionalities`,
  `feature_dependencies`, `parent`, `superseded_by`). It stays part of its parent's entry: the field
  still holds one string per top-level item.

**Where a part starts and ends.** A header is read part by part, and each part starts on a clear line:

- **A header names its entity.** It exists only when its title — the first line after the opening rule —
  carries the entity's id (`LIVING DOC — US-<n> · <title>`). An id is the minimum that identifies an
  entity: without one nothing in the header is read or normalised, and the file is reported.

- **A key sits at the key level** — the indent of the header's first key. A line shaped `key:` any
  deeper is content of the part above it, never a new key.
- **A blank line is layout.** A blank line, with its comment marker or without it, ends nothing: not
  an item, not a key, not a criterion.
- **A part ends where the next one starts.** A key's part ends at the next key at the key level. A
  criterion ends at the next `AC:` header, at a key at the key level, or at a `# =====` rule; a rule
  inside the header is an optional end of a block, and the last rule ends the header.
- **One criterion level.** In a `.feature` header every `AC:` line sits at the same indent — the first
  one sets it (template: 2), with nothing but spaces after the `# `. An `AC:` line anywhere else is read
  as text and reported.
- **Every header line carries its marker** (`# ` in a `.feature` header, ` * ` in a PageObject
  header). A line with text and no marker inside a header breaks the format: it is not read, and it is
  reported as an error. Above `Feature:`, Gherkin itself rejects such a line.
- **A value's type decides whether it may wrap.** A key whose value is one token — a state, a date, an
  id, a URL, a route, a file name, a surface type — takes one line; a further line under it is not read
  and is reported as an error. A text value and an id list may wrap onto deeper lines.
- **Recommended order.** Write the keys in the template's order, with `acceptance_criteria:` last. The
  order is a recommendation only: the reader never relies on it, because indentation decides.

Every line the reader does not take into a field is reported, so nothing an author writes is lost
without a word. A report names its entity, its criterion when the criterion has a valid id, its line
number and, for a source file, the file. The inner view of the generated document shows it under that
entity; the release view never does (see
[Rendering rules — What was not loaded](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/rendering-rules.md#what-was-not-loaded)).

**`.feature` header** — levels counted after `# `; the template levels are the canonical ones:

| Line | Level |
|---|---|
| Entity key (`status:`, `business_value:`, …) and `acceptance_criteria:` | 0 |
| Item of an entity bullet field | deeper than its key (template: 2) |
| Criterion header `AC:<id> (…)` — every one at the same level | 2 |
| Criterion item, and the criterion sub-keys `preconditions:` / `not_in_scope:` | 4 |
| Item of a criterion sub-key | 6 |
| An item's wrapped text or nested item | deeper than its `- ` |

**PageObject header** — levels counted after ` * `:

| Line | Level |
|---|---|
| Key (`route:`, `purpose:`, `notes:`, …) | the banner's base level |
| Item under a key (the `notes:` items) | deeper than the key |
| Wrapped value (the cross-reference `purpose:`) | deeper than the key; the value column is the usual choice |

A nested item, in a `.feature` header:

```gherkin
# preconditions:
#   - A registered customer account exists.
#     - It is not locked, and its email address is verified.
#   - The login screen is reachable.
```

`preconditions` holds two entries here; the nested line is part of the first.

---

## AC variants

An acceptance criterion that must hold for several values (fields, rules, roles) declares them in one
bullet, and its scenarios cover them value by value. One rule covers the User Story and the
Functionality template:

- **One variant declaration per AC.** Either `- Aspect: <value1>, <value2>`, or one named keyword
  `- <placeholder-name>: <value1>, <value2>`. The keyword is the other spelling of `Aspect:`: it names
  what varies, and the AC text shows that name as `{placeholder-name}`. An AC that declares both, two
  keywords, or `Aspect:` twice is `MALFORMED_AC`: the pipeline drops the criterion until the author
  picks one.
- **The name** is lowercase kebab-case and is written the same in the AC text (`{field}`), the bullet
  (`- field:`) and the scenario tag (`@AC:<id>/field:<value>`). Names are compared case-insensitively,
  with `-`, `_` and space equal. `aspect` is reserved.
- **A bullet is a keyword only when the text names it.** Apart from `Aspect:` and `Rationale:`, a
  `- <name>:` bullet whose name is not a `{<name>}` in the AC text is not a keyword: it is reported as
  `UNPARSED_AC_LINE`.
- **Coverage is per value.** The AC is `covered` when every declared value has a scenario,
  `not_covered` when none has, and `partially_covered` otherwise, shown as covered/declared, e.g.
  **1/3**, with the per-value breakdown. A bare `@AC:<id>` tag covers the whole AC, every value at once —
  a data-driven scenario, for example; review confirms that it really does. A tag value the AC does not
  declare is `STALE_AC_REF`, and a tag carries at most one variant parameter: a tag with two is
  `MALFORMED_AC`.

The same rule, with the tag format, is in
[Glossary — Acceptance Criterion](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#acceptance-criterion-ac).

---

## 1. User Story in a Gherkin Feature File

Header comment block at the top of every User Story feature file —
`<feature_dirs.user_story>/us-<nnn>-<kebab>.feature` (default `features/liv_doc_us/`).
Holds all US metadata and is mined during living documentation output generation.
Indentation in this header is significant — see [Indentation](#indentation). An AC declares its
variants with `Aspect:` or one named keyword, never both — see [AC variants](#ac-variants).

```gherkin
# =============================================================================
# LIVING DOC — US-<n> · <US Title>
# =============================================================================
# source:          https://github.com/<org>/<repo>/issues/<n>    ← optional
# status:          active        ← one of profile `ac_states` (planned | in_review | active | deprecated)
# deprecated_at:   <date>                                        ← optional; with status: deprecated
# deprecation_reason: <why the User Story was deprecated>        ← optional; with status: deprecated
# superseded_by:   US-<n>                                        ← optional; replacement entity
# business_value:
#   - <bullet describing the business outcome>
# preconditions:                                                 ← optional; inherited by all ACs
#   - <system state required before test>
# not_in_scope:                                                  ← optional; inherited by all ACs
#   - <item excluded from this US>
# notes:                                                         ← optional; human context
#   - <a fact worth recording that drives nothing>
#
# acceptance_criteria:
#
#   AC:US-<n>-01 (v<version> - <state>)          ← `(planned)` with no version = backlog
#     - <description of the AC>
#     - Aspect: <value1>, <value2>        ← optional; one variant declaration per AC — no {placeholder-name} needed in AC text
#     preconditions:                      ← optional; extends feature-level preconditions for this AC only
#       - <AC-specific precondition>
#     not_in_scope:                       ← optional; extends feature-level not_in_scope for this AC only
#       - <AC-specific exclusion>
#
#   AC:US-<n>-02 (v<version> - <state>)
#     - <description of the AC with one {placeholder-name} for parameterised variants>
#     - <placeholder-name>: <value1>, <value2>  ← optional; named keyword, the other spelling of `Aspect:` — never both on one AC; name = {placeholder-name} in AC text, lowercase kebab-case, not `aspect`
# =============================================================================

@US_ID:US-<n>
Feature: <US Title>
  As a <actor>, I can <capability>, so that <business outcome>.

  Background:                              ← optional
    Given <shared precondition>

  # AC:US-<n>-01 (v<version> - <state>) - <AC description>
  @AC:US-<n>-01
  Scenario: <scenario title>             ← a bare tag covers the whole AC, every declared value at once
    ...

  # - when Aspect values are declared, one scenario per value:
  @AC:US-<n>-01/aspect:<value1>
  Scenario: <scenario title for value1 branch>
    ...

  # - when a named keyword is declared, one scenario per value, tagged with the keyword's name;
  #   covered once every value has one, partially_covered shows covered/declared (e.g. 1/3):
  @AC:US-<n>-02/<placeholder-name>:<value1>
  Scenario: <scenario title for value1>
    ...

  @AC:US-<n>-02/<placeholder-name>:<value2>
  Scenario: <scenario title for value2>
    ...
```

**Header fields:**

| Field | Required | Purpose |
|---|---|---|
| `# source:` | Optional | Link to the original issue tracker entry or the pre-BDD living doc location |
| `# status:` | Yes | `planned` · `in_review` · `active` · `deprecated` (lowercase with underscores per profile `ac_states`). A User Story always carries an authored status. |
| `# deprecated_at:` | Optional | Date the User Story was deprecated; authored with `status: deprecated` |
| `# deprecation_reason:` | Optional | Why it was deprecated |
| `# superseded_by:` | Optional | ID of the replacement entity |
| `# business_value:` | Yes | Why this User Story exists (bullets) |
| `# preconditions:` | Optional | System-level state required before test execution; inherited and extended by all ACs |
| `# not_in_scope:` | Optional | Explicit exclusions at US level; inherited and extended by all ACs |
| `# notes:` | Optional | Human context at User Story level — a bullet list, one note per bullet; see [Glossary — Core entities](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#core-entities) |
| `# acceptance_criteria:` | Yes | Full AC listing with IDs, versions, and states; each AC may extend inherited preconditions and not_in_scope |
| `@US_ID:US-<n>` tag | Yes | Machine-parseable User Story ID (feature-level tag) |

**Example:** [`docs/examples/gherkin/liv_doc_us/us-001-customer-login.feature`](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/gherkin/liv_doc_us/us-001-customer-login.feature) — required fields, one covered AC and one uncovered AC, plus the one optional extension for that file (AC-level `preconditions`).

---

## 2. Feature in a PageObject File

Every PageObject file opens with a living-doc header block. Use this format so each file is self-describing and traceable without opening a separate registry.

**In this section:** [Required fields](#required-fields) · [Full vs cross-reference headers](#two-header-formats-full-vs-cross-reference) · [Maintaining the header](#maintaining-a-pageobject-header) · [Where operational notes belong](#where-operational-notes-belong) · [Common mistakes](#common-mistakes)

**Example:** [`docs/examples/pageobject/LoginPage.ts`](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/pageobject/LoginPage.ts) — full header with the `stub-reason:` optional field. [`docs/examples/pageobject/RegistrationPage.ts`](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/pageobject/RegistrationPage.ts) — an instrumented surface, full header with the `feature_dependencies:` optional field.

> **No surface status.** A PageObject header carries **no `status:` field**. The Feature it documents
> has no authored status either — a Feature's state is derived from its Functionalities (see
> [Glossary — Feature](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#feature)). A surface that is known but not
> yet instrumented for test automation says so with `stub-reason:`, not with a status value.

### Required fields

| Field | Canonical values |
|---|---|
| `surface_type` | `UI` — a PageObject is the test abstraction for a UI surface only (see [Glossary — Feature](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#feature)); an API surface has no PageObject and [carries no header here](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#feature) |
| `route` | URL path — use `{param}` for dynamic segments |
| `owners` | Team name(s), comma-separated |
| `purpose` | One-to-two sentence description in business language |
| `user_stories` | `US-N` IDs, comma-separated — or `none` (gap reports flag a Feature with no User Story) |
| `functionalities` | `FUNC-N` IDs, comma-separated — or `none` (triggers a reminder to define FUNCs) |
| `external_dependencies` | Names of systems this surface calls that are **not** Features themselves — or `none`. A system that has a canonical anchor is an `API` Feature instead, and the call is declared as `feature_dependencies` on the same header (see [Glossary — Feature](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#feature)) |
| `page-object` | Filename of this PageObject |

**Optional fields:**

| Field | When |
|---|---|
| `feature_dependencies` | The surface calls a documented `API` Feature — `FEAT-<nnn>` IDs, comma-separated. Any Feature may carry it, `UI` or `API`; each target must be an `API` Feature. Only the caller writes it; the reverse direction is not authored. Omit the key when the Feature calls nothing — there is no `none` value. See [Glossary — Feature](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#feature). |
| `wizard-steps` | Multi-step wizard UI — list the named steps in order |
| `stub-reason` | The surface is documented but not yet fully instrumented — one-to-two sentence statement of **why**; treated as tech-debt resolvable by instrumenting the template and re-scanning. Its presence *is* the marker; there is no status value for this. |
| `notes` | Human context at Feature level — a bullet list under the key, one note per bullet; see [Glossary — Core entities](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#core-entities). Not a scan diary — the rows under [Where operational notes belong](#where-operational-notes-belong) keep their homes. |
| `deprecation_reason` | The surface is being retired — one-to-two sentences on **why**; human intent, which nothing can derive. It drives no state: the Feature's state still comes from its Functionalities. See [Glossary — Feature](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#feature). |
| `superseded_by` | The surface is being retired in favour of another — the replacement's `FEAT-<nnn>` ID, a typed entity link the pipeline traverses as a relation edge. It drives no state. See [Glossary — Feature](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#feature). |

### Two header formats: Full vs Cross-reference

A PageObject file uses one of two formats depending on whether it is the **primary surface owner** or a **secondary file** that implements part of a surface already owned elsewhere.

| Situation | Format |
|---|---|
| One PageObject = one distinct navigable surface (URL or modal) | **Full header** |
| Multiple PageObjects share one URL (e.g. wizard steps, sub-pages, dialogs) — one file is the primary owner, the others are implementation helpers | **Cross-reference header** — secondary files only |

**Rule:** exactly one file per Feature carries the full header. Every other file that contributes to the same Feature carries a cross-reference header with `parent-feat` pointing to the Feature ID. This keeps traceability fields (`user_stories`, `functionalities`, `external_dependencies`) in a single authoritative location.

**Wizard example:** FEAT-042 (Account Setup Wizard) lives at one URL. `AccountSetupWizardPage.ts` is the primary file and carries the full header. `AccountSetupWizardProfilePage.ts`, `AccountSetupWizardPreferencesPage.ts`, and the other step files each carry a cross-reference header pointing `parent-feat: FEAT-042`. Adding a wizard step never requires editing the Feature registry or duplicating traceability data.

---

**Full header example:**

```typescript
/* =============================================================================
 * LIVING DOC — FEAT-042 · Account Setup Wizard
 * =============================================================================
 * surface_type:          UI
 * route:                 /app/accounts/setup
 * owners:                Platform Team
 * wizard-steps:          Profile · Preferences · Review · Confirm
 * purpose:               Multi-step wizard for creating and configuring a new account.
 * user_stories:          US-10, US-12
 * functionalities:       FUNC-005, FUNC-006
 * external_dependencies: accounts-api
 * feature_dependencies:  FEAT-051
 * page-object:           AccountSetupWizardPage.ts
 * notes:
 *   - Step order is fixed; the review step cannot be skipped even for a returning customer.
 * ============================================================================= */
```

---

**Cross-reference header required fields:**

| Field | Canonical values |
|---|---|
| `parent-feat` | `FEAT-<nnn>` — ID of the primary Feature that owns this surface. **Required.** |
| `route` | URL path of this specific sub-surface — use `{param}` for dynamic segments |
| `owners` | Team name(s), comma-separated |
| `purpose` | One sentence: what this step or sub-surface does, in business language — no FEAT IDs |
| `page-object` | Filename of this PageObject |
| `functionalities` | Optional: `FUNC-<nnn>, ...` — subset of parent Feature's Functionalities that this step implements. Omit if all sub-pages equally implement all parent Feature Functionalities. |
| `notes` | Optional: human context about this page, a bullet list as on the full header. The notes stay with this page and its data; they are never merged into the parent Feature's notes. |

The following fields are **intentionally omitted** from the cross-reference header — they belong only on the primary Feature file: `surface_type`, `user_stories`, `external_dependencies`, `feature_dependencies`, `deprecation_reason`, `superseded_by`.

**Optional inclusion of `functionalities`:** You may list this field in a cross-reference header to scope step-specific atomic behaviors to that sub-page. Use this when a step implements distinct Functionalities not shared across the entire Feature. If the sub-page's Functionality list is identical to the parent Feature's, omit this field to avoid duplication and keep the primary Feature as the authoritative source.

**Cross-reference header example:**

```typescript
/* =============================================================================
 * LIVING DOC — FEAT-042 · Account Setup Wizard  [cross-reference]
 * =============================================================================
 * This file implements Step 1 (Profile) of the Account Setup Wizard.
 * The authoritative Feature header is in AccountSetupWizardPage.ts.
 *
 * parent-feat:     FEAT-042
 * route:           /app/accounts/setup  (wizard stays on this URL)
 * owners:          Platform Team
 * functionalities: FUNC-005              ← Step 1 (Profile) implements profile-specific field validation
 * purpose:         Step 1 (Profile) — user profile fields: display name, email address,
 *                  and role selection.
 * page-object:     AccountSetupWizardProfilePage.ts
 * ============================================================================= */
```

### Maintaining a PageObject header

**By hand.** The header block *is* the registry — there is no separate file to keep in sync. Edit
the fields in place as the surface changes: keep `owners:`, `user_stories:`, and
`functionalities:` current, and when a surface is known but its template carries no `data-cy`
attributes yet, add a one-line `stub-reason:`. None of this needs
`seed.yaml` or `manifest.json` — those back the scan workflow only. Maintained by hand, the rule for
scan-style detail (scan dates, gap lists, open-issue references) is simply: it has no home in the
file — leave it out.

**With the `agentic-toolkit` skills.** The
[`living-doc-bdd-copilot`](https://github.com/AbsaOSS/living-doc/blob/master/docs/projects/agentic-toolkit.md) skills are large maintenance helpers here
and produce the identical header format — nothing about a scanned header differs from a hand-written
one. `living-doc-pageobject-scan` writes and refreshes the header and locators from a live scan of
the running app; `data-cy-instrument` adds the missing `data-cy` attributes a `stub-reason:` surface
is waiting on; `living-doc-gap-finder` reports surfaces with no User Story and uncovered User Stories. They are
accelerators, not a requirement.

### Where operational notes belong

The PageObject **header block and class JSDoc are living-doc contracts** — they encode identity and traceability. They are not a changelog, scan diary, or issue tracker.

When the scan workflow *is* in use, scan-derived detail has a home outside the header — the table
below says where, and [agentic-formats.md](https://github.com/AbsaOSS/living-doc/blob/master/agentic/skills/shared/references/agentic-formats.md#manifestjson-exploration-manifest)
defines `manifest.json`. (Without the scan workflow, none of these rows apply: the data simply is not
produced, and the header stays clean by default.)

| Information type | Correct location | NOT in |
|---|---|---|
| Missing `data-cy` attributes discovered during a scan | `manifest.json` → `coverage_gaps[]` | Header or class JSDoc |
| Reason a surface is not yet fully instrumented | Header field `stub-reason:` (one or two lines) | Free-text NOTE block |
| Proposed `data-cy` names for missing elements | `manifest.json` → `coverage_gaps[].suggested_test_id` (normalized; maps to root `test_id_attribute`) | Header or class body |
| Open issue reference (e.g. OI-08, P1) | `manifest.json` → `coverage_gaps[].note` | Header or class JSDoc |
| Scan date or scan session tag | `manifest.json` → `last_scanned` | Header or class JSDoc |
| `@stub` / `@pending` JSDoc tags on the class | — (use `stub-reason:`) | Class JSDoc |
| Implementation note explaining a locator strategy | Inline code comment on the locator or method | Header block |

**`stub-reason:` as resolvable tech-debt**

A surface carrying `stub-reason:` is **not in a permanent state** — it is a living-doc tech-debt item. The surface is known, documented, and linked to User Stories; what is missing is template instrumentation (`data-cy` attributes) that would allow full PageObject locators to be written. `stub-reason:` is the instrumentation marker: while it is present the surface is not fully instrumented, and removing it is what records that it now is. The resolution path is always:

1. Instrument the component template with the `data-cy` values listed in `manifest.json` `coverage_gaps[]` (use the `data-cy-instrument` skill).
2. Re-scan — the scan session updates the PageObject locators.
3. Remove `stub-reason:` — the surface is instrumented.

`stub-reason:` records the factual state at time of discovery (≤ two lines). The value must be free of:
- internal tool or file references (e.g. `issue-missing-data-cy.md`)
- data-cy attribute names or implementation detail
- action items ("raise with dev team", "will resolve once…")
- scan session tags except as a factual date anchor (e.g. `discovered [scan: 2026-05-28-b]`)

**`@pending` JSDoc on an individual locator property** is acceptable — it explains why that specific locator uses a fallback strategy and what resolves it. It is implementation-level, not an operational note on the surface as a whole.

### Common mistakes

| Anti-pattern | Correct |
|---|---|
| `type: screen` | `surface_type: UI` |
| `owner: Team` | `owners: Team` (plural key) |
| `status:` on a PageObject header (any value) | Remove it — a surface has no status; a Feature's state is derived from its Functionalities |
| `status: STUB` / `status: candidate` | Remove `status`, keep `stub-reason:` |
| `deprecated_at:` on a PageObject header | Remove it — a Feature has no `deprecated_at`; keep `deprecation_reason:` / `superseded_by:` if the surface is being retired |
| `# feature_dependencies:` on a Functionality header | Move it to the parent Feature's full header |
| `feature_dependencies: none` | Omit the key — the field has no `none` value |
| `functionalities:` omitted | `functionalities: none` |
| `user_stories:` omitted | `user_stories: none` |
| `external_dependencies:` omitted | `external_dependencies: none` |
| `parent-feat:` omitted from cross-reference file | Every secondary file for a shared Feature must declare `parent-feat` |
| `page-object:` omitted from cross-reference file | `page-object:` is required in both formats — it names the file being read |
| `user_stories:` or `feature_dependencies:` in cross-reference file | These fields live only on the primary Feature file; omit from cross-references |
| Multiple files claiming the same Feature without `[cross-reference]` tag | Only one file carries the full header; all others must use `[cross-reference]` format |
| NOTE block in header about missing `data-cy` or open issues | Move to `manifest.json` `coverage_gaps[]`; keep only `stub-reason:` in the header |
| `@stub` or `@pending` on the class JSDoc | Use `stub-reason:` in the header instead |
| `purpose: Step 1 of FEAT-006 — ...` | `purpose` must not contain FEAT IDs — use `Step 1 (About) — ...` instead; the ID is already in the title line and `parent-feat` |
| `purpose:` contains "NOT a …" or "Accessed via …" | Purpose describes what the surface does; exclude defensive statements and navigation instructions |
| `route:` contains a `data-cy` attribute name (e.g. `btn-import-domain`) | `route:` is a URL path or "modal overlay — no dedicated URL"; locator IDs belong in the PageObject body |
| `wizard-steps:` contains `[scan: …]` tag | `wizard-steps:` is a clean ordered list; scan provenance belongs in `manifest.json` |
| Non-spec field added to header (e.g. `query_params:`) | Only use fields defined in the Required or Optional tables; extra fields are ignored by miners and silently dropped |
| Cross-reference prose mentions FUNC IDs or file names | Cross-reference prose is mined as-is — keep it to one human-readable sentence: which step/sub-surface this file implements and where the authoritative header lives |
| `stub-reason:` contains action items, internal tool refs, or data-cy names | `stub-reason:` states only the factual reason (≤ two lines); action items go in `manifest.json` `coverage_gaps[]` |

---

## 3. Functionality in a Gherkin Feature File

Header comment block at the top of every Functionality feature file —
`<feature_dirs.functionality>/func-<nnn>-<kebab>.feature` (default `features/liv_doc_func/`).
Indentation in this header is significant — see [Indentation](#indentation). An AC declares its
variants with `Aspect:` or one named keyword, never both — see [AC variants](#ac-variants).

**Example:** [`docs/examples/gherkin/liv_doc_func/func-001-validate-password-strength.feature`](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/gherkin/liv_doc_func/func-001-validate-password-strength.feature) — required fields plus the one optional extension for that file in both its spellings: `Aspect:` on one AC, split across three scenarios (covered), and a named keyword on another, one value of three with a scenario (partly covered, 1/3); and one uncovered AC. [`func-002-reject-breached-password.feature`](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/gherkin/liv_doc_func/func-002-reject-breached-password.feature) shows a `planned` Functionality with no scenario yet.

```gherkin
# =============================================================================
# LIVING DOC — FUNC-<nnn> · <Feature Name> - <Functionality Name>
# =============================================================================
# source:    https://github.com/<org>/<repo>/issues/<n>          ← optional
# status:    planned | in_review | active | deprecated
# deprecated_at:      <date>                                     ← optional; with status: deprecated
# deprecation_reason: <why this Functionality was deprecated>    ← optional; with status: deprecated
# superseded_by:      FUNC-<nnn>                                 ← optional; replacement entity
# parent:    FEAT-<nnn>
# func_type: component_state | component_action | button_action |
#            field_validation | calculation | visibility | navigation_rule
# rationale:                                                     ← optional
#   - <why this FUNC is scoped this way — business or design decision context>
# preconditions:                                                 ← optional; inherited by all ACs
#   - <system state required before test>
# not_in_scope:                                                  ← optional; inherited by all ACs
#   - <exclusion>
# notes:                                                         ← optional; human context
#   - <a fact worth recording that drives nothing>
#
# acceptance_criteria:
#
#   AC:FUNC-<nnn>-01 (v<version> - <state>)      ← `(planned)` with no version = backlog
#     - <description in business language — no data-cy IDs in AC text>
#     - Aspect: <value1>, <value2>        ← optional; one variant declaration per AC — no {placeholder-name} needed
#     preconditions:                      ← optional; extends feature-level preconditions for this AC only
#       - <AC-specific precondition>
#     not_in_scope:                       ← optional; extends feature-level not_in_scope for this AC only
#       - <AC-specific exclusion>
#
#   AC:FUNC-<nnn>-02 (v<version> - <state>)
#     - <description — may contain one {placeholder-name} for parameterised variants>
#     - <placeholder-name>: <value1>, <value2>  ← optional; named keyword, the other spelling of `Aspect:` — never both on one AC; name = {placeholder-name} in AC text, lowercase kebab-case, not `aspect`
# =============================================================================

@FUNC_ID:FUNC-<nnn>
Feature: <Feature Name> - <Functionality Name>
  <Purpose: one-to-two sentences describing what this FUNC covers, in business
  language. Present only when purpose adds context beyond the title.>   ← optional

  # No scenarios yet — uncovered ACs flagged by coverage_report.py.
  # When adding scenarios: include # AC:<id> comment and @AC:<id>, @AC:<id>/aspect:<value> or @AC:<id>/<placeholder-name>:<value> tag above each Scenario.
  # An AC with variants is covered once every declared value has a scenario — a bare @AC:<id> scenario covers them all; partially_covered shows covered/declared (e.g. 1/3).
```

**Header fields:**

| Field | Required | Purpose |
|---|---|---|
| `# source:` | Optional | Link to the original issue tracker entry or the pre-BDD living doc location |
| `# status:` | Yes | `planned` · `in_review` · `active` · `deprecated` (lowercase with underscores per profile `ac_states`). A Functionality always carries an authored status. |
| `# deprecated_at:` | Optional | Date the Functionality was deprecated; authored with `status: deprecated` |
| `# deprecation_reason:` | Optional | Why it was deprecated |
| `# superseded_by:` | Optional | ID of the replacement entity |
| `# parent:` | Yes | Parent Feature ID (`FEAT-<nnn>`) |
| `# func_type:` | Yes | Category of behavior this Functionality represents (see table below) |
| `# rationale:` | Optional | **Why** this FUNC is scoped the way it is — business context, a deliberate design decision, or a constraint that explains the boundary. Not for implementation notes. |
| `# preconditions:` | Optional | System-level state required before test execution; inherited and extended by all ACs |
| `# not_in_scope:` | Optional | Explicit exclusions at FUNC level; inherited and extended by all ACs |
| `# notes:` | Optional | Human context at Functionality level — a bullet list, one note per bullet; see [Glossary — Core entities](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#core-entities) |
| `# acceptance_criteria:` | Yes | Full AC listing in business language — do not include `data-cy` IDs or implementation names in AC text; each AC may extend inherited preconditions and not_in_scope |
| `@FUNC_ID:FUNC-<nnn>` tag | Yes | Machine-parseable Functionality ID (feature-level tag) |
| Feature description (below `Feature:`) | Optional | One-to-two sentence purpose in business language. Use when the title alone is not self-explanatory. |

**`func_type` values:**

| Value | What it documents | PageObject anchor |
|---|---|---|
| `component_state` | Visible state of elements on load (presence, enabled/disabled, default text) AND what a data-bound component renders per data state (populated, empty, error) | `constructor` locators, data-bearing locators |
| `component_action` | Observable response within a self-contained component to an internal interaction — no discrete button, no system-level side effect (e.g. live search, autocomplete, accordion, carousel, tab content) | Component input/state locators |
| `button_action` | Observable outcome(s) after a specific discrete control is triggered — may span multiple resulting steps (e.g. redirect, entity created, dialog opened) | `btn-*` locators |
| `field_validation` | Rule enforced on a single field's value — inline error, enabled state, accepted/rejected input | `input-*` locators |
| `calculation` | Value computed and displayed from one or more inputs, independent of form submission | Display-only locators |
| `visibility` | Element presence, content, or enabled state conditional on a runtime state — condition is optional context and may be role, prior action, data presence, or config (e.g. owner sees action buttons, section appears after step complete) | Any conditional locator |
| `navigation_rule` | When and where the app routes, driven by action or system state — only when routing has a distinct precondition or business rule | Route assertion |

**Scoping rules:**

- **One FUNC, one cause.** If two behaviors share a trigger, they are one FUNC with two ACs. If two behaviors have different triggers, they are two FUNCs.
- **`component_state`** — scope to a logical group, not individual elements. "Login form controls on load" is one FUNC. Do not write one FUNC per locator. For data-bound components, each distinct data state (populated / empty / error) is an AC on the same FUNC, not a separate FUNC.
- **`component_action`** — one FUNC per distinct component behavior. If the same component has multiple independent internal behaviors (live search AND column sort), they are separate FUNCs.
- **`button_action`** — one FUNC per distinct button. A button that produces multiple observable steps is still one FUNC; the steps become multiple ACs. Two buttons = two FUNCs. Form submission is `button_action` — the trigger is the submit control.
- **`field_validation`** — one FUNC per distinct validation rule, not one per field. The same rule applied to multiple fields = one FUNC with a `{field}` placeholder AC.
- **`calculation`** — only when the derived value is observable independently of a submission. If the result only appears after a form submit, it is an AC on the `button_action` FUNC.
- **`visibility`** — use when an element's presence or state depends on a condition. The condition is descriptive context in the AC, not a required field. Distinct from `component_state` (always-true on load) and `component_action` (response to interaction).
- **`navigation_rule`** — only for routing behaviors with a distinct precondition or business rule. A redirect that is always the result of a button action is an AC on that `button_action` FUNC, not a separate `navigation_rule`.

> `test_type` (unit vs integration vs system) is not a living-doc field — not on a FUNC header, and not a
> tag this documentation defines. How a test is executed is a test-framework concern. A `@test_type:` tag
> written by a test framework may appear in a scenario file; the pipeline does not interpret it — it
> travels with the scenario's other tags, and nothing in living-doc reads it.

---

## GitHub issue-body layout

> **Planned.** GitHub issues as a documentation source are planned: `collector-gh`'s `doc-issues` mode, which mines them, is not available yet.

An entity authored as a GitHub issue follows this layout; the [`gh-issues/`](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/gh-issues/) files of
the example corpus show each entity in it.

- Each entity is one GitHub issue. Entity **type** comes from the issue **label** —
  `DocumentedUserStory` / `DocumentedFeature` / `DocumentedFunctionality`, the same values
  `collector-gh` writes into each item's `tags` — and the entity **ID** (`US-001` / `FEAT-001` /
  `FUNC-001`) from the prefix of the issue **title** (`US-001 · Customer Login`); neither is repeated
  as a body heading. (`collector-gh` also records every issue under its own `owner/repo#number` item
  ID; the entity ID above is what links the issue to the matching `.feature` file and PageObject.)
- Section headings are `##`-level and map 1:1 to the fields of the equivalent feature-file header;
  `living-doc-utilities` names the field each heading fills
  ([Parsers — Issue body](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/authoring/parsers.md#issue-body)).
- AC blocks are `###` sub-headings using the same `AC:<id> (v<version> - <state>)` grammar as the
  [glossary](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#acceptance-criterion-ac) — including the version-less
  backlog form `AC:<id> (planned)`. Feature-level `Preconditions` / `Not In Scope` are inherited by
  all ACs; AC-level extensions go under the AC sub-heading.
- Bullet sections are ordinary Markdown lists. An item indented under another item's text is that
  item's child and stays part of it. A nested item may sit under a bullet-list heading
  (`## Business Value`, `## Preconditions`, `## Not In Scope`, `## Rationale`, `## Notes`), never
  under an id-list heading (`## User Stories`, `## Functionalities`, `## Feature Dependencies`,
  `## Parent Feature`, `## Superseded By`). A flat list stays valid. The shared rule is
  [Indentation](#indentation).
- Anything outside this heading set is treated as free prose and ignored by the miner.

| Entity | Required headings | Optional headings |
|---|---|---|
| User Story | `## Description`, `## Status`, `## Business Value`, `## Acceptance Criteria` | `## Preconditions`, `## Not In Scope`, `## Deprecated At`, `## Deprecation Reason`, `## Superseded By`, `## Notes` |
| Feature | `## Description`, `## Surface Type`, `## Owners`, `## User Stories`, `## Functionalities` | `## External Dependencies`, `## Feature Dependencies`, `## Deprecation Reason`, `## Superseded By`, `## Notes` |
| Functionality | `## Description`, `## Status`, `## Parent Feature`, `## Func Type`, `## Acceptance Criteria` | `## Rationale`, `## Preconditions`, `## Not In Scope`, `## Deprecated At`, `## Deprecation Reason`, `## Superseded By`, `## Notes` |

**`## Status` and `## Deprecated At` have no place on a Feature**, and `## Notes` is available on
every entity as a bullet list of human context. The rules, and why, are in
[Glossary — Feature](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#feature) and
[Core entities](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md#core-entities): a Feature's status is derived from its
Functionalities, and a Feature has no deprecation date.

**`## User Stories` and `## Functionalities` take `none`** — the same value and the same meaning as the
matching PageObject header fields (see
[Feature in a PageObject File](#required-fields)).
The heading stays required; `none` is how a Feature says it has no link of that kind documented yet.

---

## Azure DevOps work items

> **Planned.** Azure DevOps as a documentation source is planned: `living-doc-collector-ad` is not available yet.

A work item is authored with the same `##` sections as a GitHub issue body: the same headings and the same
acceptance-criterion grammar ([GitHub issue-body layout](#github-issue-body-layout)). Its HTML is converted to
Markdown and then read by the issue-body rules
([Normalisation — Source formats](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/authoring/normalisation.md#source-formats)).

---

## Layer-local additions

*Not part of the canon above — contracts and formats that belong to the agentic layer.*

**Formats owned by the layer:** the Project Profile, `seed.yaml` and `manifest.json` formats, and
the matrix of what each skill creates or consumes, are documented in
[agentic-formats.md](./agentic-formats.md).

**Schema reference:** for JSON schema validation, see the [schemas/](./schemas/) directory:

- [project-profile.schema.json](./schemas/project-profile.schema.json) — Project Profile validation
- [seed.schema.json](./schemas/seed.schema.json) — seed.yaml validation
- [manifest.schema.json](./schemas/manifest.schema.json) — manifest.json validation
