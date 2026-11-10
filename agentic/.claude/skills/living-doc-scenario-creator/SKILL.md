---
name: living-doc-scenario-creator
description: >
  Generate Gherkin scenarios and living-doc feature files from User Story and Functionality ACs.
  Covers full feature file output (@AC:-tagged scenarios, GWT bodies), Scenario Outline,
  Background, AC coverage report, anti-pattern detection, and step definition resolution.
  Two modes: entity (from US/FUNC) and standalone.
  Triggers on: "write a Gherkin/BDD scenario", "Given When Then", "Scenario Outline",
  "BDD anti-patterns", "review my feature file", "standalone or living-doc feature file",
  "convert acceptance criteria to Gherkin", "exploratory scenario", "map AC to scenarios",
  "scenario creator". An entity id is this skill's input, not a reason to defer: it triggers
  equally on "generate scenarios for US-123", "cover every AC of US-456", "scenario coverage
  for US-789", "how do I tag AC:US-123-02".
  Does NOT trigger for: implementing step definitions (use gherkin-step); writing unit tests.
  Pairs with living-doc-create-user-story, living-doc-pageobject-scan, and gherkin-step.
license: Apache-2.0
---

# Living Doc — Scenario Creator

> **Glossary:** User Story, AC, Feature, PageObject — see [living-doc-glossary](../shared/references/living-doc-glossary.md) ([remote](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/glossary.md)).
> **BDD schemas:** US and Functionality feature file templates — see [living-doc-bdd-schemas](../shared/references/living-doc-bdd-schemas.md) ([remote](https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/authoring-formats.md)).
> **Agentic formats:** Project Profile — see [agentic-formats — Project Profile](../shared/references/agentic-formats.md#project-profile-config-driven-conventions).

**Project Profile:** Read `<bdd_artifacts_dir>/.project-profile.yaml` (default `.copilot/bdd/.project-profile.yaml`) for feature directories (`feature_dirs.*`), the AC state vocabulary (`ac_states`), and scenario tag conventions. All paths and tags below show the reference-project defaults; profile values win.

**AC states:** lowercase with underscores per the profile `ac_states` (`active`, `planned`, `in_review`, `deprecated`). Only `active` ACs drive scenario generation; the coverage report (`coverage_report.py`) also counts `in_review` ACs as needing coverage.

---

## Two modes

| Mode | When to use |
|---|---|
| **Entity mode** | A User Story or Functionality entity exists - generate full feature file with header, `@AC:` tags, and step bodies. |
| **Standalone mode** | No US/FUNC entity - write Gherkin directly from business descriptions. Use `@AC:STANDALONE` as tag; `gherkin-living-doc-sync` will note it but not flag a traceability gap. |

---

## Entity mode workflow

### Step 1 — Read the entity

Load the User Story or Functionality. Confirm:
- ID follows `US-<nnn>` or `FUNC-<nnn>` format.
- Which ACs are `active` (eligible for generation).
- ACs are atomic — one input condition, one observable outcome.

Use only the ACs and states explicitly supplied by the entity or prompt. Do not invent extra active ACs. If the prompt lists one `active`, one `deprecated`, and one `planned` AC, generate a scenario only for the single `active` AC and show the other two only as skipped in the coverage report.

**What the prompt states is supplied input — use it.** When the prompt describes the features directory (which
scenarios carry which `@AC:` tags) or states that every active AC has a matching tag, derive the coverage
report from that description and label it `derived from your description, not from a coverage_report.py run`.
Refusing for want of a file name or id the conclusion does not depend on is as wrong as inventing one.

If no ACs are `active`, do not generate empty scenarios. Output a coverage report with state-specific skip reasons (`planned`: `skipped — not yet active`, `deprecated`: `skipped — deprecated AC`) and advise the user to re-run when an AC becomes `active`.

### Step 2 — Gap detection and merge policy

An AC is uncovered if no `.feature` file carries `@AC:<id>`. Use `living-doc-gap-finder` (bottom-up mode) to identify `active` ACs with no linked scenario before writing new files.

**If a scenario already exists for an AC**, apply this policy:

| Existing scenario state | Action |
|---|---|
| Matches AC intent; GWT correct | **Skip** — record `already covered` in the coverage report |
| Step text stale or AC description changed | **Update** - rewrite GWT in-place; keep `@AC:` tag and title stable |
| Tagged `@deprecated` or `@review-needed` | **Propose replacement** — draft new scenario; confirm with user before overwriting |
| Multiple scenarios for the same AC | **Flag** — list them; ask user: valid aspect split or consolidate? |

### Step 3 — Generate feature file

For each `active` AC, output `# AC:` comment, `@AC:` tag, `Scenario:` title, and full Given/When/Then step bodies. Emit scenarios in **ascending AC-id order**, grouped under section banners (happy day before negative), so re-generation is byte-stable.

**Scenario title by AC type:**
- `happy_path` → `Scenario: <positive outcome>`
- `error` → `Scenario: <US title> — <error condition>`
- `alternative` → `Scenario: <US title> — <alternative path>`

**Traceability format** (authoritative — `gherkin-living-doc-sync` validates against this definition):

```gherkin
# AC:US-1-01 (v1.0.0 - active) - customer places an order with a saved payment method
@AC:US-1-01
Scenario: Customer successfully places an order
  Given the customer has items in their cart
  When they confirm the order with their saved payment method
  Then the order confirmation is displayed
```

Variant values — one scenario per declared value, each tagged with that one value. The AC
declares its values once, in one of two spellings, and the tag uses **the AC's own name**:

```gherkin
# the AC declared `- Aspect: username-input, password-input`
# AC:US-1-01 (v1.0.0 - active) - displays the required field on the login screen
@AC:US-1-01/aspect:username-input
Scenario: Login form shows the username input field
```

```gherkin
# the AC named it in its text and declared `- channel: email, sms`
# AC:US-2-01 (v1.0.0 - active) - the reset link is sent to the customer's {channel}
@AC:US-2-01/channel:email
Scenario: Reset link is sent by email
```

Rules, from [AC variants](../shared/references/living-doc-bdd-schemas.md#ac-variants):

- **One parameter per tag.** A scenario covers one value; write one scenario per value. A tag
  carrying two (`@AC:US-1-01/aspect:a/field:b`) is `MALFORMED_AC`.
- **The parameter name is the AC's own.** `aspect` when the AC declared `- Aspect:`, otherwise
  the keyword's name, spelled the same in the AC text (`{channel}`), the declaration
  (`- channel:`) and the tag (`@AC:US-2-01/channel:email`). A name the AC does not declare is
  `STALE_AC_REF`.
- **A value the AC does not declare** is `STALE_AC_REF`. Add it to the AC's declaration first.
- **A bare `@AC:<id>`** covers the whole AC — every declared value at once, as a data-driven
  scenario does. Use it only when the scenario really does cover them all.

Multiple ACs per scenario - one comment + tag pair per AC:

```gherkin
# AC:US-1-01 (v1.0.0 - active) - invalid credentials show an error message
# AC:US-1-02 (v1.0.0 - active) - account lockout after 3 failed attempts
@AC:US-1-01
@AC:US-1-02
@Regression
Scenario: User is locked out after repeated failed logins
```

AC tag prefix matches the parent entity: `@AC:US-<n>-<nn>` for User Story, `@AC:FUNC-<nnn>-<nn>` for Functionality.

**Feature file types:**

| Type | Location (default) | Feature block |
|---|---|---|
| User Story (E2E) | `<feature_dirs.user_story>/us-<nnn>-<kebab>.feature` (e.g. `features/liv_doc_us/`) | `Feature: <US title>` with As-a/I-can/so-that + `@US_ID:US-<n>` |
| Functionality | `<feature_dirs.functionality>/func-<nnn>-<kebab>.feature` (e.g. `features/liv_doc_func/`) | `Feature: <Feature name> - <Functionality name>` + `@FUNC_ID:FUNC-<nnn>` — the Functionality entity's `name` already has this canonical form (e.g. `Login Page - Validate Password Strength`), so use it as-is; never prefix the Feature name a second time |

**Feature-level and scenario tags** (when `scenario_conventions` enables them in the profile):
- Feature-level: the entity tag (`@US_ID:US-<n>` / `@FUNC_ID:FUNC-<nnn>`) plus an optional domain tag, e.g. `@domain_create`.
- Scenario-level: the `@AC:<id>` tag(s), plus optional suite tags such as `@Regression`.
- Section banners may group scenarios, e.g. `# *** Happy day scenarios ***` and `# *** Negative scenarios ***`.

**US feature file example** — copy this skeleton verbatim and replace only the `<...>` placeholders and AC lines; do not reorder the header blocks or rename the tags. The header comment block follows the canonical schema in [living-doc-bdd-schemas.md](../shared/references/living-doc-bdd-schemas.md#1-user-story-in-a-gherkin-feature-file) exactly — do not shorten it:

```gherkin
# =============================================================================
# LIVING DOC — US-001 · Place an online order
# =============================================================================
# source:          <living_doc_url>/us/US-001
# status:          active
# business_value:
#   - Customers can complete an order without calling support.
#
# acceptance_criteria:
#
#   AC:US-001-01 (v1.0.0 - active)
#     - customer places an order with a saved payment method
#
#   AC:US-001-02 (v1.0.0 - active)
#     - order is rejected when the payment card is declined
# =============================================================================

@US_ID:US-001
@domain_orders
Feature: Place an online order
  As a registered customer
  I can place an order for in-stock items
  So that the items are delivered to my address

  # *** Happy day scenarios ***

  # AC:US-001-01 (v1.0.0 - active) - customer places an order with a saved payment method
  @AC:US-001-01
  @Regression
  Scenario: Customer successfully places an order
    Given the customer has items in their cart
    When they confirm the order with their saved payment method
    Then the order confirmation is displayed

  # *** Negative scenarios ***

  # AC:US-001-02 (v1.0.0 - active) - order is rejected when the payment card is declined
  @AC:US-001-02
  Scenario: Order rejected when payment card is declined
    Given the customer has items in their cart
    When they attempt to pay with a declined card
    Then an error message is shown and the order is not placed
```

**Functionality feature file example** — the header comment block follows the canonical schema in [living-doc-bdd-schemas.md](../shared/references/living-doc-bdd-schemas.md#3-functionality-in-a-gherkin-feature-file) exactly — do not start the file at the `@FUNC_ID:` tag:

```gherkin
# =============================================================================
# LIVING DOC — FUNC-001 · Login Page - Validate Password Strength
# =============================================================================
# status:    active
# parent:    FEAT-010
# func_type: field_validation
#
# acceptance_criteria:
#
#   AC:FUNC-001-01 (v1.0.0 - active)
#     - returns valid=true when password satisfies all rules
# =============================================================================

@FUNC_ID:FUNC-001
Feature: Login Page - Validate Password Strength

  # AC:FUNC-001-01 (v1.0.0 - active) - returns valid=true when password satisfies all rules
  @AC:FUNC-001-01
  Scenario: Password meets all complexity rules
    Given a password with at least 8 characters, one uppercase, one lowercase, and one number
    When password strength is validated
    Then the result is valid
```

### Step 4 — AC coverage report

> **Script paths are relative to this skill's own directory**, not to your working directory — a skill installs as a self-contained directory with its `scripts/` inside it. Commands are written as `python …`, which assumes an activated virtual environment; on a system where only `python3` exists, activate a venv first or substitute `python3`. A `../<skill-name>/scripts/…` path is another installed skill's script, since skills install as sibling directories.

Run `scripts/coverage_report.py <living_doc_dir> <features_dir>` for a full report. Append after the `.feature` code block:

```
AC COVERAGE REPORT — US-001
  AC:US-001-01 (active): ✅ covered
  AC:US-001-02 (active): ✅ covered
  AC:US-001-03 (active): ❌ NOT COVERED
  AC:US-001-04 (planned): ⏭  skipped — not yet active
```

This is the summary you write. `coverage_report.py` prints its own layout — one line per AC with its
`[state]`, a `↳ covered by:` line, and a `COVERAGE SUMMARY` block — and signals the result only through
its exit code, so report its figures, never present this template as its verbatim output. It matches
tags after zero-padding the parent id: `@AC:US-10-02` counts for `AC:US-010-02`.

Coverage-report closeout rules:
- If any `active` AC is not covered, say **`Exits with code 1.`** and label each `❌ NOT COVERED` row as **scenario generation queue input** (for example `❌ NOT COVERED — add to scenario generation queue`). Also include a summary line such as `Summary: Active ACs: 2. Covered by scenarios: 0. Gaps: 2.`
- If every `active` AC is covered, say **`Exits with code 0.`** and list the real `.feature` file name(s) inline under each covered AC entry (for example `✅ covered (us-007-place-an-online-order.feature)`). Include a summary line in the form `Active/Implemented ACs: 3. Covered by scenarios: 3 (100%). Gaps: 0.`
- When the features directory is empty, report every `active` AC as `❌ NOT COVERED`; do not invent placeholder scenarios or coverage.

### Step 5 — Step definition resolution

For each generated scenario step:

1. Narrow scope to the relevant PageObject first — check step files that import it for reuse candidates.
2. Match by purpose, not just pattern — confirm the implementation performs the same business action.
3. If purpose-matching step exists, reuse it; note the source file.
4. **Case A — PageObject method exists:** say that label explicitly, then generate a full thin step stub, name the PageObject candidate and Feature ID, and suggest the step file path (for example `tests/steps/checkout_steps.py`). Example:

   ```python
   # Case A — PageObject method exists
   # PageObject candidate: CheckoutPage (FEAT-<id>)
   # Suggested step file: tests/steps/checkout_steps.py
   @when('the customer confirms the order')
   def step_confirm_order(context):
       context.checkout_page.confirm_order()
   ```

5. **Case B — missing PageObject method:** say that label explicitly, then generate a stub that raises `NotImplementedError`, and make the error message name the step text, PageObject, Feature ID, and missing method. Also add an explicit action: invoke `living-doc-pageobject-scan` **Maintain mode** for that Feature to add the missing element/method. Example opening lines:

   ```python
   # Case B — missing PageObject method
   # PageObject candidate: CheckoutPage (FEAT-<id>)
   # Suggested step file: tests/steps/checkout_steps.py
   ```

In both cases, reference the owning **Feature ID** (for example `FEAT-003`) with the PageObject — never substitute the parent User Story ID in that slot.
Take the Feature ID from the entity, the PageObject header or the prompt. When none of them gives it, write a visible placeholder (`<Checkout Feature id>`) — never a guessed number.

### Step 6 — Validation gate (closeout — mandatory)

Before reporting done, prove traceability with the scripts — do not finish while an error remains:

```bash
# AC link health (missing/malformed @AC: tags, missing # AC: comments, duplicate links):
python ../gherkin-living-doc-sync/scripts/scan_ac_links.py <features_dir> \
  --us-dir <feature_dirs.user_story> --func-dir <feature_dirs.functionality>
# AC coverage (every active AC mapped to a scenario):
python scripts/coverage_report.py <living_doc_dir> <features_dir>
```

**Regression-coverage rule:** for the goal of covering every User Story's happy-day path, each
`active` `happy_path` AC must have exactly one scenario — or, for an AC that declares variant values,
one per declared value — carrying both its `@AC:<id>` tag and a `@Regression` suite tag, placed under the `# *** Happy day scenarios ***` banner. The coverage
report must show **0 NOT COVERED** happy-path ACs before the session closes. Fix gaps and re-run
until `scan_ac_links` exits 0 and the coverage report is clean.

If the user says **"write feature tests for US-007"**, **"full coverage of all acceptance criteria"**, or similar, treat that as a direct Entity-mode generation request. Load the entity, filter to `active` ACs, generate one scenario per `active` AC, then append the coverage report with skip reasons for `planned` / `deprecated` ACs.

After any coverage report with gaps, the uncovered `active` AC rows become the **scenario generation queue**. Invoke `living-doc-scenario-creator` for each uncovered `active` AC **in report order**, generate one scenario per AC, then re-run `coverage_report.py` until gaps reach 0.

---

## Indentation is significant

A header is read part by part, and indentation decides where each part ends. Full rule:
[Indentation](../shared/references/living-doc-bdd-schemas.md#indentation). What bites while
writing one:

- **Every header line carries its marker** — `# ` in a `.feature` header. A line with text and
  no marker is not read, and the file is reported.
- **A key sits at the key level**, the indent of the header's first key. A line shaped `key:`
  any deeper is content of the part above it, never a new key.
- **A deeper line belongs to the item above it** — wrapped text or a nested item, never a
  sibling and never a new key.
- **One criterion level.** Every `AC:` line sits at the same indent, the first one setting it
  (template: 2), with nothing but spaces after the `# `.
- **A one-token value takes one line** — a state, a date, an id, a URL, a route, a file name, a
  surface type. A further line under it is not read.
- **Nest only in a bullet-list field** (`business_value`, `preconditions`, `not_in_scope`,
  `rationale`, `notes`) — never in an id-list field (`user_stories`, `functionalities`,
  `feature_dependencies`, `parent`, `superseded_by`), which holds one id per entry.
- **A blank line is layout**: it ends nothing — not an item, not a key, not a criterion.
- Indent with spaces. Levels are relative, so no column is fixed, and a flat layout where
  items sit at their key's own indent stays valid.

## Gherkin quality rules

### Write in the ubiquitous language

Scenarios must use business domain language. Anyone on the product team must be able to read and verify them without implementation knowledge.

```gherkin
# ✅
Given a customer with a gold membership
When they place an order for 2 units of "SKU-100"
Then the order is confirmed and the total is £160.00

# ❌ — implementation details
Given the database contains a row in users with tier="gold"
When a POST request is sent to /api/orders
Then the response status is 201
```

### GWT keyword rules

| Keyword | Purpose | Rule |
|---|---|---|
| **Given** | System state before the action | Preconditions only — no actions, no assertions |
| **When** | The action the actor takes | Exactly one meaningful action per scenario |
| **Then** | Observable outcome | Assertions only — no actions |
| **And / But** | Continuation | Never as the first step in a block |

One behaviour per scenario. If the scenario name contains "and", it likely tests two behaviours — split it.

### Scenario Outline

Use for data-driven variations. Show concrete outcome values in `Examples:`, not raw percentages:

```gherkin
Scenario Outline: Discount applied correctly for each membership tier
  Given a customer with a <tier> membership
  When they purchase an item costing £100.00
  Then the total is £<total>

  Examples:
    | tier   | total |
    | gold   | 80.00 |
    | silver | 90.00 |
```

### Background

Use only when every scenario in the file shares the precondition. Keep to 3 steps or fewer. If only 2–3 scenarios share a precondition, duplicate the `Given` step — prefer clarity over abstraction. `Background` must use only `Given` steps.

When the feature-level `preconditions:` block is present, use it as the `Background` — one `Given` step per bullet. If an individual AC has AC-level `preconditions:`, extend the Background with those additional `Given` steps **only for that scenario** — do not apply AC-level preconditions to other scenarios in the file. This keeps scenarios independent and makes AC-level constraints visible in the scenario itself rather than the file-wide Background.

**Example:** Feature-level preconditions (Background for all scenarios):
```gherkin
# preconditions:
#   - User is logged in

Background:
  Given the user is logged in

# AC:FUNC-001-01 (v1.0 - active)
#   preconditions:
#     - User has admin role
Scenario: Admin can create a new user
  Given the user is logged in              ← inherited from Background (feature-level)
  Given the user has admin role            ← extends feature-level preconditions (AC-level)
  When they submit the create user form
  Then a new user is created
```

### Anti-patterns

| Anti-pattern | Fix |
|---|---|
| UI selectors in steps (`I click the "Submit" button`) | Domain action (`the customer submits the order`) |
| Imperative style (`I enter "alice@example.com" in Email field`) | Declarative (`the customer logs in as Alice`) |
| Multiple `When` per scenario | Split into separate scenarios |
| Assertions in Given/When | Move all assertions to `Then` |
| Scenario depends on prior scenario state | Make every scenario fully self-contained |

When reviewing an existing scenario, check for a missing `@AC:` tag above each `Scenario:` - call that out as a traceability defect.

---

## Standalone mode

When no User Story or Functionality entity exists, generate scenarios directly from business descriptions:

- Apply all GWT rules and ubiquitous language rules above.
- Use `@AC:STANDALONE` as an optional tag to signal intentionally unlinked scenarios.
- Omit the header block (`# status:`, `# business_value:`, `# acceptance_criteria:`, `@US_ID:`) — start directly with `Feature:`.
- File location is at the user's discretion; `gherkin-living-doc-sync` will note `@AC:STANDALONE` but not flag a traceability gap.

---

## Output format

Output all generated Gherkin in a single fenced `gherkin` code block — starting with the file's header block in Entity mode, or directly with `Feature:` in Standalone mode. Besides the header comments and tags, use only `Feature:`, `Scenario:`, `Scenario Outline:`, `Background:`, `Given`, `When`, `Then`, `And`, `But`, `Examples:` inside the block.

---

## Out-of-scope routing

| Request | Correct skill |
|---|---|
| Implementing step definition code | `gherkin-step` |
| Writing unit tests | Use your project's test framework directly |
| Syncing `@AC:` tags and traceability in existing feature files | `gherkin-living-doc-sync` |
