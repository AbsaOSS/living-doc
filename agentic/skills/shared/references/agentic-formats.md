# Agentic layer formats

The formats the agentic layer owns: the Project Profile, `seed.yaml`, `manifest.json`, and the
matrix of what each skill creates or consumes. The `living-doc-bdd-copilot` agent and its skills
create and maintain these files as configuration and as durable local memory between runs; they
are not part of the living-doc canon and nothing in the living-doc pipeline reads them.

**This page is hand-maintained and owned by the layer.** It is not generated, unlike
`living-doc-glossary.md` and `living-doc-bdd-schemas.md` next to it, which are regenerated from
this repository's `docs/` by `agentic/scripts/sync-canon-copies.sh`. The entity model those two
describe is the canon; the formats below are the layer's own.

It lives in `shared/references/` so that a skill installed on its own gets it:

```bash
npx skills add https://github.com/AbsaOSS/living-doc -g --skill <skill>
npx skills add https://github.com/AbsaOSS/living-doc -g --skill shared
```

## Contents

- [Project Profile (config-driven conventions)](#project-profile-config-driven-conventions)
- [seed.yaml (Business Seed)](#seedyaml-business-seed)
- [manifest.json (Exploration Manifest)](#manifestjson-exploration-manifest)
- [What each `living-doc-bdd-copilot` skill creates or consumes](#what-each-living-doc-bdd-copilot-skill-creates-or-consumes)

---

## Project Profile (config-driven conventions)

**Every value a skill could otherwise hardcode — directory names, the test-id attribute,
state-casing, tag conventions — lives in one Project Profile file.** Tooling reads the profile at
session start and never assumes defaults. This keeps the format portable across projects that use
different directory layouts or naming. the `living-doc-bdd-copilot` agent creates it on first run from the
defaults below (confirming each value with the user) and loads it as-is thereafter — it is not a file
you are expected to write from scratch.

**Location:** `<bdd_artifacts_dir>/.project-profile.yaml` (default `.copilot/bdd/.project-profile.yaml`).

**Example:** [`docs/examples/project-profile/.project-profile.yaml`](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/project-profile/.project-profile.yaml).

```yaml
# .copilot/bdd/.project-profile.yaml — defaults shown match the reference (AUL) project.
test_id_attribute: data-cy            # what page.getByTestId() resolves to (Playwright testIdAttribute)

feature_dirs:
  user_story:    features/liv_doc_us      # E2E User Story feature files
  functionality: features/liv_doc_func    # Functionality (system-test) feature files

paths:
  bdd_artifacts:  .copilot/bdd            # seed.yaml, manifest.json, breaking-changes.md
  pageobjects:    playwright/pages
  steps:          playwright/steps

# AC state vocabulary as written inside `# AC:` blocks and feature-file headers (lowercase with underscores).
ac_states: [planned, in_review, active, deprecated]

# Scenario tagging conventions (see "Feature file tags" below).
scenario_conventions:
  feature_tag:        true     # @US_ID:<id> / @FUNC_ID:<id> on the Feature
  domain_tag:         true     # optional second feature-level tag, e.g. @domain_create
  suite_tags:         ["@Regression"]   # additional scenario-level tags allowed beside @AC:
  section_banners:    true     # "# *** Happy day scenarios ***" / "# *** Negative scenarios ***"

manifest_shape: object         # manifest is an object with routes array (see Manifest schema)
```

| Field | Used by | Default (AUL) |
|---|---|---|
| `test_id_attribute` | pageobject-scan, data-cy-instrument, gherkin-step | `data-cy` |
| `feature_dirs.user_story` | scenario-creator, gherkin-living-doc-sync, gap-finder, scripts | `features/liv_doc_us` |
| `feature_dirs.functionality` | scenario-creator, pageobject-scan, gap-finder, scripts | `features/liv_doc_func` |
| `paths.bdd_artifacts` | pageobject-scan, data-cy-instrument | `.copilot/bdd` |
| `paths.pageobjects` / `paths.steps` | pageobject-scan, gherkin-step | `playwright/pages` / `playwright/steps` |
| `ac_states` | all catalog skills, scenario-creator, gherkin-living-doc-sync | `active` etc. (lowercase with underscores) |
| `scenario_conventions` | scenario-creator, gherkin-living-doc-sync | as shown |

> **Casing rule:** AC and entity states use **lowercase with underscores** inside `# AC:` blocks,
> entity files and issue bodies (e.g. `active`, `in_review`). Wherever a skill shows `ACTIVE` or
> `PLANNED` in upper-case prose, it refers to the *logical* state; the *written* form is always
> lowercase with underscores. There is no PageObject `status:` field — see
> [Feature in a PageObject File](https://github.com/AbsaOSS/living-doc/blob/master/docs/guides/living-doc-header-types.md#2-feature-in-a-pageobject-file).

---

## seed.yaml (Business Seed)

`seed.yaml` lives at `<paths.bdd_artifacts>/seed.yaml` (default `.copilot/bdd/seed.yaml`). It is **the
agent's local memory, not a human-authored file** — its durable record of the app's business surface
between scan sessions: app entry point, business domains → routes, known entities for parameterised
routes, test-user roles, and pre-declared form values. The agent creates it, re-reads it in full at
the start of every scan session, and appends to it as it discovers entities. A human may pre-seed
known values or correct them, but is not expected to write the file.

**Example:** [`docs/examples/project-profile/seed.yaml`](https://github.com/AbsaOSS/living-doc/blob/master/docs/examples/project-profile/seed.yaml) — required keys plus one optional `form_fixtures` entry.

```yaml
# .copilot/bdd/seed.yaml
# Business Seed — last verified <date> (app <version>)

app:
  name: <App Name>
  base_url: https://<host>
  auth_entry_path: /auth/dashboard        # landing route after auth

credentials_source: <path/to/.env>        # file holding TEST_USERID / TEST_PASSWORD etc.

test_id_attribute: data-cy                # mirrors the Project Profile value

business_domains:                         # business surface → route → Feature entity
  - name: Authentication
    route_prefix: /login
    feature_id: FEAT-001
  - name: Create Domain Wizard
    route_prefix: /auth/all-domains/create-domain/about
    feature_id: FEAT-006
  - name: Edit Domain
    route_prefix: /auth/all-domains/{domainId}/{version}/edit-domain
    feature_id: FEAT-UNKNOWN              # no Feature yet — flagged for living-doc-create-feature
    note: "RE-SCAN [<date>]. Reuses the shared stepper in edit mode."

user_roles:
  - role: standard_user
    description: Default E2E test user — covers most flows
    note: Items that do not navigate for this role

# known_entities — real entity IDs observed during scans. Copyable values for
# parameterised routes ({domainId}/{version}) and form fields. Never store prod IDs.
known_entities:
  domains:
    - id: <uuid>
      version: 1
      name: "E2E Domain ..."
      status: Draft
      owner: <test-user>
      note: "Primary owned domain for the test user."
      next_scan_targets:                  # optional: queued sub-routes/tabs to scan next
        - tab: Version management
          url: /auth/all-domains/<uuid>/1/about
          action: "Click 'Version management' tab — scan for data-cy elements."
      data_feeds:                         # optional nested entities
        - id: <uuid>
          version: 1
          name: "test csv"

# form_fixtures — pre-declared field values for form/wizard traversal, keyed by route path.
# Read before falling back to the sourcing cascade below.
form_fixtures:
  /auth/all-domains/create-domain/about:
    - field: domain-name
      value: "E2E Test Domain"
      source: seed_declared               # seed_declared | user_provided | agent_observed
      note: "Append a timestamp suffix at runtime to avoid duplicate rejection."
    - field: cost-center
      value: "SA345678"
      source: seed_declared
      note: "HEALED [<date>] — format must be 2 alpha + 6 digits per component validator."
```

**Top-level keys:**

| Key | Required | Purpose |
|---|---|---|
| `app` | Yes | `name`, `base_url`, `auth_entry_path` |
| `credentials_source` | Yes | Path to the env file holding test credentials — **never inline literals** |
| `test_id_attribute` | Yes | Mirrors the Project Profile (`data-cy` by default) |
| `business_domains[]` | Yes | `name`, `route_prefix`, `feature_id` (+ optional `note`). Use `FEAT-UNKNOWN` when no Feature entity exists yet |
| `user_roles[]` | Yes | `role`, `description` (+ optional `note`) |
| `known_entities` | No | Real IDs harvested during scans for parameterised routes; `domains[]` with `id/version/name/status/owner/note`, optional `next_scan_targets[]` and nested `data_feeds[]` |
| `form_fixtures` | No | Map of `route → [ {field, value, source, note?} ]`. `source`: `seed_declared` \| `user_provided` \| `agent_observed` |

**Credential rule:** credentials are referenced via `credentials_source` (an env file) or `env:VAR_NAME`
placeholders. A literal credential value anywhere in `seed.yaml` is a **security violation** — the file must be
corrected before proceeding.

### form_fixtures sourcing cascade (how a field value is resolved)

1. **`seed.yaml form_fixtures`** — pre-declared (`source: seed_declared`) or written in a prior session (`agent_observed`).
2. **Existing app entities** — navigate to the entity list; read a real field value; copy it, or derive (e.g. append a suffix to avoid duplicate rejection).
3. **Field context inference** — read label + placeholder + tooltip → infer a plausible value (`"Domain name"` → `"E2E Test Domain"`, `email` → `"test@example.com"`).
4. **User-assist pause** — for a value that must exist in the real environment and none of the above suffices → show the form, request the value, record it back with `source: user_provided`.

> **Optional advanced fields.** For complex forms a fixture entry may also carry `value_class`
> (`copyable` / `derived` / `fake` / `real-world`), a `values[]` array of labelled traversal branches
> (each `{label, value, source}`, `label: default` = happy path), or a `condition`
> (`{when_field, when_value}`) that gates the fill. These are optional extensions to the base
> `{field, value, source}` shape — omit them unless the form requires branch exploration or conditional fields.

### Input validation probing

After a successful form fill and submission, probe each text input and scan the form after each probe
to capture error `data-cy` elements visible only in the invalid state:

| Probe | Input | What to observe |
|---|---|---|
| Special characters | `<>'"&\` | Inline error, silent strip, or truncation |
| Oversized input | 200+ characters | Character counter, truncation, or rejection message |
| Wrong type | Text in a numeric/date field | Inline validation message or rejection |
| Duplicate detection | A known existing entity name | Duplicate-rejected error and its `data-cy` |

Findings become source material for `field_validation` Functionality stubs and are recorded in the
manifest route's optional `field_constraints[]` (see below).

---

## manifest.json (Exploration Manifest)

`manifest.json` lives at `<paths.bdd_artifacts>/manifest.json` (default `.copilot/bdd/manifest.json`).
It is **the agent's local memory, not a human-authored file** — its machine record of every scanned
surface, written and read by the tooling across runs. The manifest is a JSON object; **`routes` is a JSON array** of route objects
(profile `manifest_shape: object`). Targeted entries are loaded by route during a session; the full file
is loaded only for a RE-SCAN.

The manifest uses **normalized test_id keys** (not attribute-specific). The root-level `test_id_attribute` metadata
tells downstream generators (PageObject, data-cy-instrument) how to map these normalized keys to the actual HTML attribute.

```json
{
  "generated": "2026-06-08T12:00:00Z",
  "scan_version": "v1.9.2-36-g6660993",
  "test_id_attribute": "data-cy",
  "routes": [
    {
      "url": "/login",
      "title": "App - Login",
      "pageobject_path": "playwright/pages/LoginPage.ts",
      "feature_id": "FEAT-001",
      "last_scanned": "2026-05-28T13:32:00Z",
      "note": "Optional scan provenance.",
      "elements": [
        { "test_id": "input-username", "tag": "cps-input",  "label": "Username" },
        { "test_id": "btn-login",      "tag": "cps-button", "label": "Login", "note": "NEW [scan: ...]" }
      ],
      "coverage_gaps": [
        { "tag": "button", "ariaLabel": "Collapse sidebar", "suggested_test_id": "btn-collapse-sidebar", "note": "no test-id" }
      ],
      "open_actions_menu": {
        "owned_domain": ["View data feeds", "Grant access", "Edit domain"],
        "note": "Optional — menu contents per context."
      },
      "navigation_context": "Default landing page after login.",
      "field_constraints": [
        { "field": "domain-name", "max_length": 100, "special_chars": "rejected", "duplicate": "rejected-with-error", "duplicate_error_test_id": "domain-name-duplicate-error" }
      ]
    }
  ]
}
```

**Route object fields:**

| Field | Required | Purpose |
|---|---|---|
| `url` | Yes | Route path; use `{param}` for dynamic segments. `modal:<host-route>` for dialog-only surfaces |
| `title` | Yes | Document/page title at scan time |
| `pageobject_path` | Yes | Repo-relative path to the PageObject file |
| `feature_id` | Yes | Living-doc Feature ID, or `FEAT-UNKNOWN` |
| `last_scanned` | Yes | ISO 8601 timestamp; surfaces stale entries |
| `elements[]` | Yes | Discovered test-id elements: `{ "test_id": <id>, "tag": <html-tag>, "label": <text\|null>, "note"?: <scan note> }`. `test_id` is normalized and maps to root `test_id_attribute` downstream. |
| `coverage_gaps[]` | Yes | Interactive elements lacking a test-id: `{ "tag", "text"\|"ariaLabel"\|"role"\|"type", "suggested_test_id", "note"? }`. Empty array = fully instrumented. `suggested_test_id` is normalized. |
| `navigation_context` | Yes | **String** — how to reach the route (prose). Reused across sessions |
| `note` | No | Scan provenance for the route as a whole |
| `open_actions_menu` | No | Context-menu contents keyed by context (e.g. owned vs non-owned) |
| `field_constraints[]` | No | Per-field validation findings: `{ field, max_length?, special_chars?, duplicate?, duplicate_error_test_id?, allowed_format?, real_world_required? }` |

> **Normalized test_id keys:** The manifest uses `test_id` (not `data-cy`) and `suggested_test_id` (not `suggestedDataCy`)
> as fixed, attribute-agnostic keys. The root-level `test_id_attribute` (mirrors Project Profile) tells downstream
> generators what HTML attribute these keys map to (e.g., `data-cy`, `data-testid`, or a custom attribute).
> PageObject generators read this metadata and emit the correct attribute; the manifest shape remains consistent
> regardless of the configured attribute.

### Lifecycle

| Event | What happens |
|---|---|
| First form encountered | The sourcing cascade is applied; the form is filled; validation is probed |
| `real-world` value missing | User-assist pause → value saved to `form_fixtures` with `source: user_provided` |
| Validation probe finds a new `data-cy` | Added to the route `elements[]`; flagged as a `field_validation` Functionality candidate |
| Next scan session | `form_fixtures` is read; the cascade is skipped for pre-declared fields |
| Constraint changes (e.g. max length) | `field_constraints` is updated; the change is flagged in `breaking-changes.md` |
| Element missing on re-scan | Flagged `BREAKING CHANGE`; the locator is never auto-deleted |

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
