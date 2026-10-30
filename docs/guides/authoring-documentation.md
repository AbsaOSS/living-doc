# Authoring documentation

## Purpose

This page shows how to write a `.feature` or PageObject header that the pipeline reads as you meant it: the
canonical form, the variants it corrects, the mistakes it never guesses at, and how to check before you push. The
normative parsing rules are `living-doc-utilities`'
[Authoring](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/authoring.md) pages; a GitHub issue
body is a planned source, so its [layout](../reference/authoring-formats.md#github-issue-body-layout) is linked
here, not taught.

Read before: [README](../../README.md) · Next: [Authoring formats](../reference/authoring-formats.md)

## Contents

- [Write it like this](#write-it-like-this)
- [What the pipeline also accepts](#what-the-pipeline-also-accepts)
- [What it never guesses](#what-it-never-guesses)
- [How to check before you push](#how-to-check-before-you-push)

## Write it like this

Each entity is a header block at the top of its file, under a title that carries its id. Every field of each type
is in [Authoring formats](../reference/authoring-formats.md); the examples below are cut from the
[example corpus](../examples/README.md).

**User Story**: the header of a `.feature` file, then the `@US_ID` tag and `Feature:`
([template](../reference/authoring-formats.md#1-user-story-in-a-gherkin-feature-file)).

```gherkin
# =============================================================================
# LIVING DOC — US-001 · Customer Login
# =============================================================================
# status:          active
# business_value:
#   - Registered customers can reach their account area, so returning users
#     convert without friction.
#
# acceptance_criteria:
#
#   AC:US-001-01 (v1.0.0 - active)
#     - A customer who submits valid credentials lands on the account dashboard.
# =============================================================================

@US_ID:US-001
Feature: Customer Login
```

**Feature**: the header comment of a PageObject file. It has no status: a Feature's state is derived from its
Functionalities ([template](../reference/authoring-formats.md#2-feature-in-a-pageobject-file)).

```typescript
/* =============================================================================
 * LIVING DOC — FEAT-001 · Login Page
 * =============================================================================
 * surface_type:          UI
 * route:                 /login
 * owners:                Identity Team
 * purpose:               The screen where a registered customer enters an email and password to sign in.
 * user_stories:          US-001
 * functionalities:       FUNC-001, FUNC-002
 * external_dependencies: auth-api
 * page-object:           LoginPage.ts
 * ============================================================================= */
```

**Functionality**: the header of a `.feature` file, under its parent Feature, then the `@FUNC_ID` tag and
`Feature:` ([template](../reference/authoring-formats.md#3-functionality-in-a-gherkin-feature-file)).

```gherkin
# =============================================================================
# LIVING DOC — FUNC-001 · Login Page - Validate Password Strength
# =============================================================================
# status:    active
# parent:    FEAT-001
# func_type: field_validation
#
# acceptance_criteria:
#
#   AC:FUNC-001-02 (v1.0.0 - active)
#     - Returns valid=true when the candidate password satisfies every complexity rule.
# =============================================================================

@FUNC_ID:FUNC-001
Feature: Login Page - Validate Password Strength
```

**Acceptance criterion**: a header `AC:<id> (v<x.y.z> - <state>)`, or `AC:<id> (planned)` for the backlog, with
its description as the first bullet ([grammar](../reference/glossary.md#acceptance-criterion-ac)). A criterion that
must hold for several values declares them once, with a keyword: one name, written the same three times, as
`{field}` in the text, as the bullet `- field:` that lists the values, and on each scenario's tag as
`@AC:<id>/field:<value>` ([AC variants](../reference/authoring-formats.md#ac-variants)). In the corpus the name is
`rule`:

```gherkin
#   AC:FUNC-001-03 (v1.0.0 - active)
#     - Shows the failed {rule} under the password field.
#     - rule: minimum-length, character-classes, no-username
```

```gherkin
  # AC:FUNC-001-03 (v1.0.0 - active) - shows the failed rule | rule: minimum length
  @AC:FUNC-001-03/rule:minimum-length
  Scenario: Password shorter than the minimum length shows the minimum-length rule
```

## What the pipeline also accepts

A collector corrects small formatting variants before it reads a header, so each one below reaches the document in
its canonical form. Each pair is a case of `living-doc-utilities`'
[`normalisation_cases.yaml`](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/living_doc_utilities/authoring/normalisation_cases.yaml)
at `v0.8.0`, named by its id: the case's `input` before, its `expected` after. What each rule rewrites, and what it
never touches, is in
[Normalisation — Rules](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/authoring/normalisation.md#rules).
These are corrections, not alternatives: write the canonical form.

### Bullet markers

**`rule1_bullet_marker_star_rationale_feature_header`**: A `*` bullet becomes `-`.

```text before
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# rationale:
#   * Password strength is checked client-side for immediate feedback.
# =====
```

```text after
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# rationale:
#   - Password strength is checked client-side for immediate feedback.
# =====
```

**`rule1_bullet_marker_plus_not_in_scope_feature_header`**: A `+` bullet becomes `-`.

```text before
# =====
# LIVING DOC — US-001 · Customer Login
# =====
# not_in_scope:
#   + Social-identity (OAuth) sign-in.
# =====
```

```text after
# =====
# LIVING DOC — US-001 · Customer Login
# =====
# not_in_scope:
#   - Social-identity (OAuth) sign-in.
# =====
```

**`rule1_bullet_marker_bullet_dot_notes_page_object`**: A `•` bullet in a PageObject `notes:` list becomes `-`, so the two notes stay two.

```text before
/* =============================================================================
 * LIVING DOC — FEAT-001 · Login Page
 * =====
 * page-object:           LoginPage.ts
 * notes:
 *   • The sign-in form markup comes from the shared identity template.
 *   - The screen is called "Sign in" to customers.
 * ============================================================================= */
```

```text after
/* =============================================================================
 * LIVING DOC — FEAT-001 · Login Page
 * =====
 * page-object:           LoginPage.ts
 * notes:
 *   - The sign-in form markup comes from the shared identity template.
 *   - The screen is called "Sign in" to customers.
 * ============================================================================= */
```

### Criterion headers

**`rule2_ac_header_separator_em_dash_feature_header`**: An em dash between the version and the state becomes ` - `.

```text before
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# acceptance_criteria:
#   AC:FUNC-001-01 (v1.0.0 — active)
#     - Returns valid=false when the candidate password fails a complexity rule.
# =====
```

```text after
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# acceptance_criteria:
#   AC:FUNC-001-01 (v1.0.0 - active)
#     - Returns valid=false when the candidate password fails a complexity rule.
# =====
```

**`rule3_state_casing_status_key_feature_header`**: `In Review` becomes `in_review`.

```text before
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# status:          In Review
# =====
```

```text after
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# status:          in_review
# =====
```

**`rule3_state_casing_ac_header_feature_header_keeps_indent`**: A capitalised state becomes lowercase; the line keeps its indent.

```text before
# =====
# LIVING DOC — US-001 · Customer Login
# =====
# acceptance_criteria:
# AC:US-001-01 (v1.0.0 - Active)
# - Valid credentials land on the dashboard.
# =====
```

```text after
# =====
# LIVING DOC — US-001 · Customer Login
# =====
# acceptance_criteria:
# AC:US-001-01 (v1.0.0 - active)
# - Valid credentials land on the dashboard.
# =====
```

**`rule4_version_form_bare_numeric_feature_header`**: A version without its `v` gains it.

```text before
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# acceptance_criteria:
#   AC:FUNC-001-02 (1.0.0 - active)
#     - Returns valid=true when the candidate password satisfies every rule.
# =====
```

```text after
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# acceptance_criteria:
#   AC:FUNC-001-02 (v1.0.0 - active)
#     - Returns valid=true when the candidate password satisfies every rule.
# =====
```

**`rule7_inline_ac_description_feature_header_split`**: A description on the header line moves onto its own bullet.

```text before
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# acceptance_criteria:
#   AC:FUNC-001-01 (v1.0.0 - active) - rejects a weak password
# =====
```

```text after
# =====
# LIVING DOC — FUNC-001 · Validate Password Strength
# =====
# acceptance_criteria:
#   AC:FUNC-001-01 (v1.0.0 - active)
#     - rejects a weak password
# =====
```

### Titles

**`rule5_entity_name_dash_functionality_title`**: An en dash between a Functionality's Feature name and its behaviour becomes ` - `.

```text before
# =============================================================================
# LIVING DOC — FUNC-001 · Login Page–Validate Password Strength
# =============================================================================
# status:    active
```

```text after
# =============================================================================
# LIVING DOC — FUNC-001 · Login Page - Validate Password Strength
# =============================================================================
# status:    active
```

**`rule5b_title_id_separator_hyphen_feature_header`**: A hyphen after the id becomes ` · `.

```text before
# =============================================================================
# LIVING DOC — US-001 - Customer Login
# =============================================================================
# status:    active
```

```text after
# =============================================================================
# LIVING DOC — US-001 · Customer Login
# =============================================================================
# status:    active
```

**`rule5b_title_id_separator_colon_page_object`**: A colon after the id becomes ` · `.

```text before
/* =============================================================================
 * LIVING DOC — FEAT-001: Login Page
 * =============================================================================
 * surface_type:          UI
 * ============================================================================= */
```

```text after
/* =============================================================================
 * LIVING DOC — FEAT-001 · Login Page
 * =============================================================================
 * surface_type:          UI
 * ============================================================================= */
```

### Indentation

The "before" blocks below hold real tab and no-break-space characters, which a browser shows as blanks.

**`rule6_whitespace_tab_indentation_feature_header`**: Each tab in an indent becomes one space, so the levels stay relative.

```text before
# =====
# LIVING DOC — US-001 · Customer Login
# =====
# business_value:
#	- Fewer support calls.
#		A wrapped line.
# =====
```

```text after
# =====
# LIVING DOC — US-001 · Customer Login
# =====
# business_value:
# - Fewer support calls.
#  A wrapped line.
# =====
```

**`rule6_whitespace_nbsp_indentation_feature_header`**: A no-break space in an indent becomes a space.

```text before
# =====
# LIVING DOC — US-001 · Customer Login
# =====
# business_value:
#   - Fewer support calls.
# =====
```

```text after
# =====
# LIVING DOC — US-001 · Customer Login
# =====
# business_value:
#   - Fewer support calls.
# =====
```

**`rule6_whitespace_tab_indentation_page_object`**: A tab after ` * ` becomes a space.

```text before
/* =============================================================================
 * LIVING DOC — FEAT-001 · Login Page
 * =====
 *	surface_type:          UI
 * ============================================================================= */
```

```text after
/* =============================================================================
 * LIVING DOC — FEAT-001 · Login Page
 * =====
 * surface_type:          UI
 * ============================================================================= */
```

### Scenario comments

**`rule7_inline_ac_description_scenario_file_inline`**: A `# AC:` comment keeps its description on the line; only the dash before it becomes ` - `.

```text before
# AC:US-001-01 (v1.0.0 - active) — valid credentials land on the account dashboard
@AC:US-001-01
Scenario: Customer signs in with valid credentials
```

```text after
# AC:US-001-01 (v1.0.0 - active) - valid credentials land on the account dashboard
@AC:US-001-01
Scenario: Customer signs in with valid credentials
```

**`rule2_rule3_rule4_scenario_file_combined`**: The separator, the state's case and the version are fixed together; the `| aspect:` suffix stays.

```text before
# AC:FUNC-001-01 (v1.0 – ACTIVE) - rejects a weak password | aspect: minimum length
@AC:FUNC-001-01/aspect:minimum-length
```

```text after
# AC:FUNC-001-01 (v1.0.0 - active) - rejects a weak password | aspect: minimum length
@AC:FUNC-001-01/aspect:minimum-length
```

## What it never guesses

A collector corrects form, never meaning. Where a header lacks something only its author knows, the pipeline does
not guess it: it drops what it cannot read and reports a warning with the file and the line
([codes](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/errors.md#codes)).

| You wrote | The warning | What happens |
|---|---|---|
| A criterion with no version, `AC:US-001-01 (active)`, or a short one, `(v1 - active)` | `MALFORMED_AC` | The criterion is dropped. Only `planned` goes without a version, and `v1` has no minor part to complete. |
| A misspelt state in a criterion header, `(v1.0.0 - actve)` | `MALFORMED_AC` | The criterion is dropped. Case and separators are corrected; spelling never is. |
| A misspelt status, `status: actve` | `MALFORMED_STATUS`, then `MISSING_STATUS` | The value is dropped, and the status is derived from the entity's own criteria. |
| A title with no id, `LIVING DOC — Customer Login` | `MISSING_ENTITY_ID` | Nothing in the header is read, and the entity is not in the document. |
| A criterion header with no id, `AC: (v1.0.0 - active)` | `MALFORMED_AC` | The criterion is dropped. |
| `- Aspect:` and a keyword on one criterion | `MALFORMED_AC` | The criterion is dropped until you keep one of the two. |

Each line of a dropped criterion is reported too, as `AUTHORING_WARNING`.

## How to check before you push

- Run `collector-gh`'s `doc-source` mode on your branch, as a workflow step on the pull request or by hand
  ([action reference](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md)).
- Read the `warnings[]` of its `doc-source.json`: each warning names the file and the line, and links that line at
  your commit ([Documentation Source mode — Errors](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/doc_source/README.md#errors)).
- The inner view of the generated document shows the same warnings under their entity
  ([What was not loaded](../reference/rendering-rules.md#what-was-not-loaded)).
- `tests/examples/examples_check.py` checks this repository's example corpus, `docs/examples/`, only; it does not
  read your project.
