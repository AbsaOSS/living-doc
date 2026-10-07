# Example Input Files for Mining

A canonical, minimal corpus of the **input** files the living-doc pipeline mines — the things a
collector reads, not the documents a generator produces. For the formats these files follow, see
[Living Doc Header Types](../guides/living-doc-header-types.md) and
[Living Doc Glossary](../guides/living-doc-glossary.md).

All examples describe **one coherent mini technical project** — `US-001` / `FEAT-001` / `FUNC-001` /
`FUNC-002`, plus `FEAT-002`, an `API` Feature, and `FEAT-003`, the `UI` Feature that declares a
dependency on it — so that, taken together, the `.feature` files plus the entities form a complete
[coverage-matrix](../guides/living-doc-document-types.md#coverage-matrix) input: in each of the two
`.feature` files that carry scenarios, at least one AC is covered by a scenario and one is left
uncovered, and `AC:FUNC-001-03` has a scenario for one of its three values, so the matrix shows all
three verdicts — `covered`, `not_covered` and `partially_covered` (the pinned snapshot does not show
the third yet; see [What the corpus mines to](#what-the-corpus-mines-to-_expected)).

## Files

| Path | Format reference |
|---|---|
| [gherkin/liv_doc_us/us-001-customer-login.feature](gherkin/liv_doc_us/us-001-customer-login.feature) | [Header Types § User Story](../guides/living-doc-header-types.md#1-user-story-in-a-gherkin-feature-file) |
| [gherkin/liv_doc_func/func-001-validate-password-strength.feature](gherkin/liv_doc_func/func-001-validate-password-strength.feature) | [Header Types § Functionality](../guides/living-doc-header-types.md#3-functionality-in-a-gherkin-feature-file) |
| [gherkin/liv_doc_func/func-002-reject-breached-password.feature](gherkin/liv_doc_func/func-002-reject-breached-password.feature) | [Header Types § Functionality](../guides/living-doc-header-types.md#3-functionality-in-a-gherkin-feature-file) |
| [pageobject/LoginPage.ts](pageobject/LoginPage.ts) | [Header Types § Feature in a PageObject File](../guides/living-doc-header-types.md#2-feature-in-a-pageobject-file) |
| [pageobject/RegistrationPage.ts](pageobject/RegistrationPage.ts) | [Header Types § Feature in a PageObject File](../guides/living-doc-header-types.md#2-feature-in-a-pageobject-file) |
| [project-profile/.project-profile.yaml](project-profile/.project-profile.yaml) | [Header Types § Project Profile](../guides/living-doc-header-types.md#project-profile-config-driven-conventions) |
| [project-profile/seed.yaml](project-profile/seed.yaml) | [Header Types § seed.yaml](../guides/living-doc-header-types.md#seedyaml-business-seed) |
| [gh-issues/us-001-customer-login.md](gh-issues/us-001-customer-login.md) | [GitHub issue-body layout](#github-issue-body-layout-canonical) |
| [gh-issues/feat-001-login-page.md](gh-issues/feat-001-login-page.md) | [GitHub issue-body layout](#github-issue-body-layout-canonical) |
| [gh-issues/feat-002-breached-password-check.md](gh-issues/feat-002-breached-password-check.md) | [GitHub issue-body layout](#github-issue-body-layout-canonical) |
| [gh-issues/feat-003-registration-page.md](gh-issues/feat-003-registration-page.md) | [GitHub issue-body layout](#github-issue-body-layout-canonical) |
| [gh-issues/func-001-validate-password-strength.md](gh-issues/func-001-validate-password-strength.md) | [GitHub issue-body layout](#github-issue-body-layout-canonical) |
| [gh-issues/func-002-reject-breached-password.md](gh-issues/func-002-reject-breached-password.md) | [GitHub issue-body layout](#github-issue-body-layout-canonical) |

## What the corpus mines to (`_expected/`)

[`_expected/`](_expected/) holds the JSON this `gherkin/` corpus produces when the **real**
`living-doc-collector-gh` (`doc-source` + `ui-tests`) and `living-doc-toolkit` `coverage-matrix`
are run over it — `doc-source.json`, `ui-tests.json`, `coverage-matrix.json`, normalized so only
the mined content is compared. `.github/workflows/real-collector-snapshot.yml` regenerates them on
every PR touching `docs/examples/**` and fails on any diff, so a parser or schema change in the
pinned collector that alters the mined output surfaces here. These files double as a worked
reference for anyone integrating the collector. To regenerate after an intended change, see
[CONTRIBUTING.md § Regenerating the collector snapshots](../../CONTRIBUTING.md#regenerating-the-collector-snapshots).

The snapshots record what the **pinned** collector mines, which is not always all of what the corpus
says. The pinned `collector-gh` predates the version-less backlog AC form, so it skips
`AC:FUNC-002-01 (planned)` as a malformed header — and that is `FUNC-002`'s only AC, so `_expected/`
shows the Functionality with none. That gap is the point of the snapshot: it is visible here, and it
closes when the pin moves to a collector whose AC grammar accepts the backlog form. The pinned
collector likewise predates `feature_dependencies` and `notes`, which `living-doc-utilities` carries
from `0.5.0`, and drops both authored keys, so the edge `FEAT-003` declares and the notes on `FEAT-001`
are not in `_expected/` yet either. Both gaps close when the pin moves to a collector built on
`living-doc-utilities` `0.5.0` or later. The pinned collector also predates the
[named keyword](../guides/living-doc-header-types.md#ac-variants): it folds `- rule: …` into the
description of `AC:FUNC-001-03`, declares no values for it, and reads
`@AC:FUNC-001-03/rule:minimum-length` as a link to the whole criterion, so `_expected/` shows that AC
`covered` where the canon says `partially_covered`, 1/3. That gap closes when the pin moves to a collector
whose `living-doc-utilities` maps the keyword to `aspect`.

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
  [glossary](../guides/living-doc-glossary.md#acceptance-criterion-ac) — including the version-less
  backlog form `AC:<id> (planned)`. Feature-level `Preconditions` / `Not In Scope` are inherited by
  all ACs; AC-level extensions go under the AC sub-heading.
- Bullet sections are ordinary Markdown lists. An item indented under another item's text is that
  item's child and stays part of it. A nested item may sit under a bullet-list heading
  (`## Business Value`, `## Preconditions`, `## Not In Scope`, `## Rationale`, `## Notes`), never
  under an id-list heading (`## User Stories`, `## Functionalities`, `## Feature Dependencies`,
  `## Parent Feature`, `## Superseded By`). A flat list stays valid. The shared rule is in
  [Header Types § Indentation](../guides/living-doc-header-types.md#indentation).
- Anything outside this heading set is treated as free prose and ignored by the miner.

| Entity | Required headings | Optional headings |
|---|---|---|
| User Story | `## Description`, `## Status`, `## Business Value`, `## Acceptance Criteria` | `## Preconditions`, `## Not In Scope`, `## Deprecated At`, `## Deprecation Reason`, `## Superseded By`, `## Notes` |
| Feature | `## Description`, `## Surface Type`, `## Owners`, `## User Stories`, `## Functionalities` | `## External Dependencies`, `## Feature Dependencies`, `## Deprecation Reason`, `## Superseded By`, `## Notes` |
| Functionality | `## Description`, `## Status`, `## Parent Feature`, `## Func Type`, `## Acceptance Criteria` | `## Rationale`, `## Preconditions`, `## Not In Scope`, `## Deprecated At`, `## Deprecation Reason`, `## Superseded By`, `## Notes` |

**`## Status` and `## Deprecated At` have no place on a Feature**, and `## Notes` is available on
every entity as a bullet list of human context. The rules, and why, are in
[Living Doc Glossary — Feature](../guides/living-doc-glossary.md#feature) and
[Core entities](../guides/living-doc-glossary.md#core-entities): a Feature's status is derived from its
Functionalities, and a Feature has no deprecation date.

**`## User Stories` and `## Functionalities` take `none`** — the same value and the same meaning as the
matching PageObject header fields (see
[Header Types § Feature in a PageObject File](../guides/living-doc-header-types.md#required-fields)).
The heading stays required; `none` is how a Feature says it has no link of that kind documented yet.

## Conventions used by this corpus

- **Minimal.** Each entity file carries every required field plus one optional field — just enough to
  show one field extension, no more. (`.project-profile.yaml` is shown complete: it is pure config
  with no optional-field layer.)
- **AC states are part of the AC grammar, not optional field extensions.** A `planned`, `in_review`,
  `active` or `deprecated` AC — with or without a target version, with or without a removal note — is
  the grammar of [`AC:<id> (…)`](../guides/living-doc-glossary.md#acceptance-criterion-ac) doing its
  job, so it does not count against the one-optional-extension-per-file rule above.
- **`## Notes` is not a field extension either.** It extends no mined field set, so the one instance in
  the corpus does not count against the one-optional-extension-per-file rule above. It is shown once, on
  [`gh-issues/feat-001-login-page.md`](gh-issues/feat-001-login-page.md): a Feature is the entity whose
  state is derived and which has no deprecation date, so a human note is what is left to record there.
  `living-doc-utilities` carries `notes` in the entity contract from `0.5.0` and never interprets a
  note; an earlier release drops an authored value and warns — `UNKNOWN_SECTION` from the issue-body
  parser, `IGNORED_AUTHORED_KEY` from the `.feature` and PageObject header parsers.
- **Field extensions**, spread across the corpus so each is shown once in isolation — one per file,
  no file carrying two:
  - AC-level `preconditions` extension — `gherkin/liv_doc_us/us-001-customer-login.feature`
  - feature-level `Not In Scope` — `gh-issues/us-001-customer-login.md`
  - `External Dependencies` — `gh-issues/feat-001-login-page.md`
  - `Aspect:` on an AC — `gherkin/liv_doc_func/func-001-validate-password-strength.feature`, in both
    its spellings: `- Aspect:` on `AC:FUNC-001-01`, and the named keyword `- rule:` on `AC:FUNC-001-03`.
    The keyword is the second spelling of the `Aspect:` extension, not a second extension (see
    [Header Types § AC variants](../guides/living-doc-header-types.md#ac-variants)), so the file still
    carries one.
  - `Rationale` — `gh-issues/func-001-validate-password-strength.md`
  - `Feature Dependencies` — `gh-issues/feat-003-registration-page.md`
  - `feature_dependencies:` — `pageobject/RegistrationPage.ts`
  - feature-level `Preconditions` — `gh-issues/func-002-reject-breached-password.md`
- **`@domain_*` tag** — `.project-profile.yaml` sets `scenario_conventions.domain_tag: true`, and all
  three `.feature` files carry `@domain_authentication` as the optional second feature-level tag.
- **Coverage pair.** `AC:US-001-01` and `AC:FUNC-001-01` are covered by scenarios;
  `AC:US-001-02` and `AC:FUNC-001-02` are declared but have no scenario (a deliberate gap, so the
  coverage matrix shows both the covered and the uncovered verdict). `AC:FUNC-001-03` sits between
  them: one of its three `rule` values has a scenario, so it is partly covered, **1/3**.
- **AC states, once each.** Beyond the `active` ACs above, `AC:US-001-03 (v1.1.0 - planned)` shows a
  `planned` AC that targets a version, `AC:FUNC-002-01 (planned)` shows the version-less backlog form,
  and `AC:US-001-04 (v1.0.0 - deprecated - removal planned v2.0.0)` shows a deprecated AC with its
  removal note — covered by a scenario, because a deprecated AC still describes shipped behaviour and
  is still counted.
- **Derived Feature state, no surface status.** `FEAT-001` carries no authored status in either form:
  its issue body has no `## Status` heading and `LoginPage.ts` has no `status:` field, and neither form
  carries a `deprecated_at`. The Feature's state is derived from `FUNC-001` and `FUNC-002`. The login
  template is not
  yet instrumented for test automation, and the PageObject says so with `stub-reason:` — the
  instrumentation marker, which is removed once the surface is instrumented. See
  [Header Types § Feature in a PageObject File](../guides/living-doc-header-types.md#2-feature-in-a-pageobject-file).
  `RegistrationPage.ts` is the instrumented counterpart: real `getByTestId()` locators and no
  `stub-reason:`.
- **Two forms per entity, in step.** `US-001`, `FUNC-001` and `FUNC-002` each exist as a GitHub issue
  body and as a `.feature` header, and `FEAT-001` and `FEAT-003` as an issue body and a PageObject
  header. The two forms of an entity carry the same required content and, for the User Story and the
  Functionalities, the same AC set; only the optional field extension differs, by the assignment above.
- **One form for an `API` Feature.** `FEAT-002` exists as an issue body only. An `API` Feature's
  contract anchor carries no living-doc header yet, so there is no source-code form to write — see
  [Living Doc Glossary — Feature](../guides/living-doc-glossary.md#feature). It is documented at
  surface level (`## Functionalities` is `none`): the corpus needs it as a resolvable **target**, and a
  dependency resolves on the Feature id.
- **The dependency pair.** `FEAT-001` records `auth-api` under `External Dependencies` — a system with
  no canonical anchor, named as free text. `FEAT-003` records `FEAT-002` under `feature_dependencies` —
  an `API` Feature, named by id and validated by `tools/examples_check.py`. The two fields side by side
  are the distinction the [glossary](../guides/living-doc-glossary.md#feature) draws. `FEAT-003` is
  documented at surface level (`User Stories` and `Functionalities` are `none`), like `FEAT-002`.
- **The dependency is authored in both `FEAT-003` forms**, as the one optional extension of each.
  `living-doc-utilities` carries the field from `0.5.0`; an earlier release drops an authored value on
  the way in — `IGNORED_AUTHORED_KEY`, as for `notes` above — and the pinned collector is one, so
  `_expected/` does not show it yet. Carried, the edge does not resolve in the `doc-source` chain:
  `FEAT-002` is authored in `gh-issues/`, and a pipeline that takes its technical project from
  `gherkin/` + `pageobject/` reports `UNRESOLVED_RELATION` for a target it cannot see. That is expected
  of this corpus — the same shape as the `STALE_AC_REF` note below, one chain referencing what the
  other declares — and it is what a source-code project sees in general, since no `API` Feature can be
  authored there yet.
- **Expected `STALE_AC_REF` on the `gh-issues` chain.** `Aspect:` is a `.feature`-header extension, so
  `AC:FUNC-001-01` declares its three aspects, and `AC:FUNC-001-03` its three `rule` values, only in the
  `gherkin/` form. A pipeline that takes its technical project from `gh-issues/` and its test catalog
  from `gherkin/` therefore sees the `@AC:FUNC-001-01/aspect:…` and `@AC:FUNC-001-03/rule:…` scenario
  tags reference values the mined AC does not declare, and reports `STALE_AC_REF` for them. That is
  expected of this corpus, not a defect: the `doc-source` chain (`gherkin/` + `pageobject/`) is the
  pairing the `_expected/` snapshots exercise.

## Sync obligation

This corpus is part of the persisted product documentation and does not depend on any planning spec.
Two rules keep it truthful, both enforced **in the same PR** as the change that triggers them:

1. **Format change.** When a field or rule on [Living Doc Header Types](../guides/living-doc-header-types.md)
   or [Living Doc Glossary](../guides/living-doc-glossary.md) changes, update the matching example here.
2. **Implementation change (last check).** When a collector mode that mines these inputs
   (`collector-gh` `doc-source` / `ui-tests` / `doc-issues`) is implemented or changed, re-check this
   corpus **and** the guides above against what the tooling actually mines, and correct any drift.
   This is the checkpoint that catches divergence between the documented format and the shipped state.
