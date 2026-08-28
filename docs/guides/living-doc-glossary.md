# Living Doc Glossary

Core entity contracts: IDs, status vocabulary, relationships, and AC format. Every `living-doc-*` repo and `agentic-toolkit`'s `living-doc-bdd-copilot` agent operate on this canonical entity model.

For the file-header schemas that carry these entities (feature file headers, PageObject headers, Project Profile, seed.yaml, manifest.json), see [Living Doc Header Types](living-doc-header-types.md).

> **Source of truth.** This page is the canonical definition of the entity model. `agentic-toolkit`'s `skills/shared/references/living-doc-glossary.md` is synced from it.

---

## Contents

- [Core entities](#core-entities)
  - [User Story (US)](#user-story-us)
  - [Feature](#feature)
  - [Functionality (FUNC)](#functionality-func)
  - [Acceptance Criterion (AC)](#acceptance-criterion-ac)
- [Relationship diagram](#relationship-diagram)
- [What each `living-doc-bdd-copilot` skill creates or consumes](#what-each-living-doc-bdd-copilot-skill-creates-or-consumes)

---

## Core entities

### User Story (US)

A business-level requirement expressed from the perspective of a named actor.

```
As a <actor>,
I can <capability>,
so that <business outcome>.
```

- ID format: `US-<nnn>` (e.g. `US-001`)
- Name: short imperative title (e.g. "Customer Login")
- Owns: end-to-end **Acceptance Criteria (AC)**
- Links to: one or more **Features** (system surfaces the User Story touches)
- Status: `planned | in_review | active | deprecated` (lowercase with underscores per the Project Profile `ac_states`)
- Deprecation metadata (set when `status: deprecated`):
  - `deprecated_at` — date the entity was deprecated
  - `deprecation_reason` — why it was deprecated
  - `superseded_by` — ID of the replacement entity (optional)

> Feature file template: see [Living Doc Header Types — User Story in a Gherkin Feature File](living-doc-header-types.md#1-user-story-in-a-gherkin-feature-file).

### Feature

A named system surface — the structural layer between User Stories and atomic behaviors.

- ID format: `FEAT-<nnn>` (e.g. `FEAT-001`)
- Name: noun phrase identifying the surface (e.g. "Login Page")
- Surface types:

| Type | Description | Test abstraction |
|---|---|---|
| `UI` | A web page, modal, or named screen | **PageObject** design pattern — class encapsulating selectors and user interactions for one screen. Selector preference: `getByTestId()` (resolves to the Project Profile `test_id_attribute`, default `data-cy`) > `aria-label`/role > CSS class. |
| `API` | A REST/GraphQL endpoint or endpoint group. A backend service is documented as an API Feature representing its public contract. | **Annotated endpoint method** — the endpoint method with its API documentation header (OpenAPI annotation, JSDoc, etc.) serves as the living contract anchor. |

- Owns: one or more **Functionalities**
- Links to: one or more **User Stories**
- `owners`: team or person responsible for this Feature
- Status: `planned | in_review | active | deprecated` (lowercase with underscores per the Project Profile `ac_states`)
- Deprecation metadata (set when `status: deprecated`):
  - `deprecated_at` — date the entity was deprecated
  - `deprecation_reason` — why it was deprecated
  - `superseded_by` — ID of the replacement entity (optional)
- Ownership change metadata (set when `owners` changes):
  - `owner_changed_at` — date of ownership transfer
  - `owner_change_reason` — reason for the transfer

> PageObject file header schemas (full header, cross-reference, operational notes, common mistakes): see [Living Doc Header Types — Feature in a PageObject File](living-doc-header-types.md#2-feature-in-a-pageobject-file).

### Functionality (FUNC)

An atomic, fast-testable behavior — a single verb phrase describing one responsibility.

- ID format: `FUNC-<nnn>` (e.g. `FUNC-001`)
- Name: `<parent Feature name> – <behavior phrase>` (e.g. "Login Page – Validate Password Strength")
- Belongs to: one parent **Feature**
- Owns: **Functionality-level Acceptance Criteria** (atomic input to output statements)
- Test anchor: a **Functionality feature file** under `features/liv_doc_func/` — one file per
  Functionality, containing all AC-linked system-test scenarios once implemented.
  File name pattern: `func-<nnn>-<feature-name-kebab>-<behavior-kebab>.feature`
  e.g. `func-001-authentication-screen-credential-based-login.feature`
- Status: `planned | in_review | active | deprecated` (lowercase with underscores per the Project Profile `ac_states`)
- Deprecation metadata (set when `status: deprecated`):
  - `deprecated_at` — date the entity was deprecated
  - `deprecation_reason` — why it was deprecated
  - `superseded_by` — ID of the replacement entity (optional)

Functionalities differ from User Story ACs: they are atomic and fast-testable, not end-to-end.
A single User Story may trigger multiple Functionalities.

#### User Story vs Functionality — decision boundary

| Dimension | User Story | Functionality |
|---|---|---|
| Perspective | End user observing a business outcome | Developer / component behavior |
| Scope | Full E2E flow across one or more surfaces | Single function, method, or UI behavior |
| AC example | "Order is confirmed and confirmation email is sent" | "Returns discounted total when a valid membership tier is applied" |
| Test type | E2E / integration scenario | Unit or fast system test |
| Trigger question | *"Would a product owner write this as a business requirement?"* → **User Story** | *"Would a developer write this as a function contract?"* → **Functionality** |

**When in doubt:** if the behavior is observable only by looking at the code or component output (not by a user clicking through the UI), it is a Functionality. If it describes what a user can do or see across one or more screens, it is a User Story.

If an AC belongs to the wrong entity type, redirect:
- AC too atomic / technical inside a US → move to a **Functionality**
- AC describes a full user journey inside a FUNC → move to a **User Story**

> Feature file template and `func_type` values: see [Living Doc Header Types — Functionality in a Gherkin Feature File](living-doc-header-types.md#3-functionality-in-a-gherkin-feature-file).

### Acceptance Criterion (AC)

A binary pass/fail statement that defines a verifiable condition.

Each AC is:
- **Atomic** — one input condition, one observable outcome
- **Binary** — clear pass/fail; no "usually" or "typically"
- **Single placeholder** — at most ONE `{placeholder}` per AC statement. If two aspects vary independently, write a separate AC for each.

**AC identifier and state format** (in file header and entity files):

```
AC:<parent-id>-<nn> (v<version> - <State>)
   - <atomic description, with at most one {placeholder} for a variable value>
   - <Placeholder>: value1, value2, ...
   - Rationale: <business context, policy reference, or design decision>  ← optional
```

State values: `planned | in_review | active | deprecated` (lowercase with underscores per the Project Profile `ac_states`).

**Scenario traceability:** living-doc scenarios (US and Functionality feature files) carry two
complementary annotations — a human-readable `# AC:` comment and a machine-readable `@AC:` tag:

```gherkin
# AC:US-1-01 (v1.0.0 - active) — customer places an order with a saved payment method
@AC:US-1-01
Scenario: Customer successfully places an order
  ...
```

When a scenario covers only **one aspect** of a multi-aspect AC, encode the aspect directly in
the `@AC:` tag using the `/param:value` param syntax, and mirror it in the comment:

```gherkin
# AC:US-1-01 (v1.0.0 - active) — displays {required field} on login screen | aspect: username input
@AC:US-1-01/aspect:username-input
Scenario: Login form shows the username input field
  ...
```

Multiple ACs — one comment + tag pair per AC:

```gherkin
# AC:US-1-01 (v1.0.0 - active) — invalid credentials show an error message
# AC:US-1-02 (v1.0.0 - active) — account lockout after 3 failed attempts
@AC:US-1-01
@AC:US-1-02
@Regression
Scenario: User is locked out after repeated failed logins
  ...
```

**Tag format:** `@AC:<id>[/param:value...]`

| Param | Purpose | Example |
|---|---|---|
| `/aspect:<kebab-value>` | Names the specific aspect of the AC this scenario covers | `@AC:US-1-01/aspect:username-input` |

Additional `/param:value` segments can be appended as needed — the format is open for extension.

- The `# AC:` comment is human-readable context: AC ID, version, state, description, optional aspect.
- The `@AC:` Cucumber tag is machine-readable: drives script scanning, coverage reports, and sync checks.
- US scenarios: `@AC:US-<n>-<nn>` (e.g. `@AC:US-1-01`)
- Functionality scenarios: `@AC:FUNC-<nnn>-<nn>` (e.g. `@AC:FUNC-001-01`)
- Both annotations are required for living-doc feature files (`feature_dirs.user_story` and `feature_dirs.functionality`, defaults `features/liv_doc_us/` and `features/liv_doc_func/`).
- Feature files outside the living-doc directories (smoke tests, regression suites, exploratory probes,
  tutorial walkthroughs) do not require `@AC:` tags.
- **Tutorial walkthroughs** are long-run, feature-based walkthroughs kept for tutorial capture, not living
  documentation. They live in one or more folders *parallel* to the living-doc directories (named
  `tutorials/` or `tutorial_<group>/`), carry a `@tutorial` scenario flag, and are out of scope for every
  collector mode — no collector mines them. See [Roadmap](../specs/roadmap.md)'s Post-v1 section.

Deprecated ACs include a removal note:

```
AC:<parent-id>-<nn> (v<version> – DEPRECATED – removal planned v<version>)
```

**Descoped ACs** (deferred mid-sprint — state stays `PLANNED`):

```
AC:<parent-id>-<nn> (v<version> – PLANNED)
   – <description>
   – descoped_at: <date>           ← date AC was deferred out of the current sprint
   – descoped_reason: <text>
   – future_release: <sprint/tag>  ← optional; target sprint or release
```

**User Story AC examples** (in the `# Acceptance Criteria:` file header block):

```
AC:US-001-01 (v1.0.0 - active)
   - The login screen displays {required field}.
   - Required field: username input, password input, login button
   - Rationale: Accessibility standard — all interactive controls must be visible on load.

AC:US-001-02 (v1.1.0 - active)
   - An inline field validation message is shown when invalid credentials are submitted.

AC:US-001-03 (v2.1.0 - deprecated - removal planned v3.0.0)
   - A "Remember me" checkbox retains the session across browser restarts.
   - Rationale: Deprecated due to security policy change in v2.0 — persistent sessions no longer permitted.
```

**Functionality AC examples** (in the `# Acceptance Criteria:` file header block):

```
AC:FUNC-001-01 (v1.0.0 - active)
   - Returns valid=true when the password satisfies all complexity rules.

AC:FUNC-001-02 (v1.0.0 - active)
   - Raises {error code} when the credential check fails.
   - Error code: INVALID_PASSWORD, USER_NOT_FOUND, ACCOUNT_LOCKED
   - Rationale: Distinct error codes per failure reason, required by the global auth error contract.

AC:FUNC-001-03 (v1.0.0 - active)
   - Rejects passwords shorter than 8 characters.
```

---

> `seed.yaml` and `manifest.json` schemas: see [Living Doc Header Types — manifest.json (Exploration Manifest)](living-doc-header-types.md#manifestjson-exploration-manifest).

---

## Relationship diagram

```
User Story (US)
  └── links to: Feature (FEAT)
                    └── owns: Functionality (FUNC)
                                    └── owns: Functionality ACs
                                    └── maps to: Functionality feature file (system test)
                                    |              <feature_dirs.functionality>/func-<nnn>-<kebab>.feature
                                    |              @FUNC_ID tag + @AC:FUNC-nnn-nn tagged scenarios
                                    |              └── implemented by: Step Definitions
                                    └── can map to: unit/integration tests
  └── owns: User Story ACs (in # Acceptance Criteria: header block)
                  └── linked via: @AC:US-n-nn tags on Scenarios
                  └── can map to: E2E BDD Scenarios (<feature_dirs.user_story>/*.feature)
                                       @US_ID tag + @AC:US-n-nn tagged scenarios
                                       └── implemented by: Step Definitions
                                                               └── delegates to: PageObjects
                  └── can map to: API coverage / contract tests
```

---

## What each `living-doc-bdd-copilot` skill creates or consumes

| Skill | Creates | Reads |
|---|---|---|
| `living-doc-create-user-story` | User Story entity | Feature entities |
| `living-doc-create-feature` | Feature entity | User Story entities |
| `living-doc-create-functionality` | Functionality entity + Functionality feature file stub | Feature entity |
| `living-doc-pageobject-scan` | PageObject files + Functionality feature file stubs + fixture entries in `seed.yaml` | App URL or test suite; `seed.yaml form_fixtures` |
| `living-doc-scenario-creator` | E2E BDD scenario files (US) + Functionality feature files (FUNC) | US / FUNC entities, PageObjects |
| `living-doc-gap-finder` | Gap report | All of the above |
