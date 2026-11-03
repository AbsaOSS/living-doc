# Example Input Files for Mining

A canonical, minimal corpus of the **input** files the living-doc pipeline mines — the things a
collector reads, not the documents a generator produces. For the formats these files follow, see
[Authoring formats](../reference/authoring-formats.md) and
[Glossary](../reference/glossary.md).

All examples describe **one coherent mini technical project** — `US-001` / `FEAT-001` / `FUNC-001` /
`FUNC-002`, plus `FEAT-002`, an `API` Feature, and `FEAT-003`, the `UI` Feature that declares a
dependency on it — so that, taken together, the `.feature` files plus the entities form a complete
[coverage-matrix](../guides/living-doc-document-types.md#coverage-matrix) input: in each of the two
`.feature` files that carry scenarios, at least one AC is covered by a scenario and one is left
uncovered, and `AC:FUNC-001-03` has a scenario for one of its three values, so the matrix shows all
three verdicts — `covered`, `not_covered` and `partially_covered` (the matrix is snapshotted; see
[What the corpus mines to](#what-the-corpus-mines-to-_expected)).

## Files

| Path | Format reference |
|---|---|
| [gherkin/liv_doc_us/us-001-customer-login.feature](gherkin/liv_doc_us/us-001-customer-login.feature) | [Authoring formats § User Story](../reference/authoring-formats.md#1-user-story-in-a-gherkin-feature-file) |
| [gherkin/liv_doc_func/func-001-validate-password-strength.feature](gherkin/liv_doc_func/func-001-validate-password-strength.feature) | [Authoring formats § Functionality](../reference/authoring-formats.md#3-functionality-in-a-gherkin-feature-file) |
| [gherkin/liv_doc_func/func-002-reject-breached-password.feature](gherkin/liv_doc_func/func-002-reject-breached-password.feature) | [Authoring formats § Functionality](../reference/authoring-formats.md#3-functionality-in-a-gherkin-feature-file) |
| [pageobject/LoginPage.ts](pageobject/LoginPage.ts) | [Authoring formats § Feature in a PageObject File](../reference/authoring-formats.md#2-feature-in-a-pageobject-file) |
| [pageobject/RegistrationPage.ts](pageobject/RegistrationPage.ts) | [Authoring formats § Feature in a PageObject File](../reference/authoring-formats.md#2-feature-in-a-pageobject-file) |
| [project-profile/.project-profile.yaml](project-profile/.project-profile.yaml) | [Agentic formats § Project Profile](../../agentic/skills/shared/references/agentic-formats.md#project-profile-config-driven-conventions) |
| [project-profile/seed.yaml](project-profile/seed.yaml) | [Agentic formats § seed.yaml](../../agentic/skills/shared/references/agentic-formats.md#seedyaml-business-seed) |
| [gh-issues/us-001-customer-login.md](gh-issues/us-001-customer-login.md) | [Authoring formats § GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout) |
| [gh-issues/feat-001-login-page.md](gh-issues/feat-001-login-page.md) | [Authoring formats § GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout) |
| [gh-issues/feat-002-breached-password-check.md](gh-issues/feat-002-breached-password-check.md) | [Authoring formats § GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout) |
| [gh-issues/feat-003-registration-page.md](gh-issues/feat-003-registration-page.md) | [Authoring formats § GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout) |
| [gh-issues/func-001-validate-password-strength.md](gh-issues/func-001-validate-password-strength.md) | [Authoring formats § GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout) |
| [gh-issues/func-002-reject-breached-password.md](gh-issues/func-002-reject-breached-password.md) | [Authoring formats § GitHub issue-body layout](../reference/authoring-formats.md#github-issue-body-layout) |

## What the corpus mines to (`_expected/`)

[`_expected/collector-gh/`](_expected/collector-gh/) holds the JSON the **real**
`living-doc-collector-gh` writes when its `doc-source` and `ui-tests` modes mine this corpus's
source-code chain — `gherkin/` and `pageobject/` — in the collector's own output layout:
`doc-source/doc-source.json` and `ui-tests/ui-tests.json`, normalized so only the mined content is
compared. `.github/workflows/real-collector.yml` regenerates them on every PR touching
`docs/examples/**` or `tests/**`. It runs the pinned collector in a venv built from the collector's
own `requirements.txt`, validates each artifact against its contract, asserts that what the corpus
authors comes through with none of the warnings a canonical corpus must not raise, and fails on any
diff — so a parser or schema change in the pinned collector that alters the mined output surfaces
here. These files double as a worked reference for anyone integrating the collector. To regenerate
after an intended change, see
[CONTRIBUTING.md § Regenerating the collector snapshots](../../CONTRIBUTING.md#regenerating-the-collector-snapshots).

The snapshots carry everything the source-code chain authors: the backlog AC
`AC:FUNC-002-01 (planned)` and the `not_in_scope` on `FUNC-002`, `FEAT-001` with its state derived
from its Functionalities, the `feature_dependencies` edge `FEAT-003` declares, and the
[named keyword](../reference/authoring-formats.md#ac-variants) on `AC:FUNC-001-03` — its three
`rule` values as the AC's `aspect`, and its one scenario linked as `aspect: minimum-length`. They also
carry the two warnings this corpus expects: `UNRESOLVED_RELATION` for that edge (see
[The dependency is authored in both `FEAT-003` forms](#conventions-used-by-this-corpus)) and
`FEATURE_WITHOUT_FUNCTIONALITY` for `FEAT-003`, documented at surface level.

[`_expected/toolkit/`](_expected/toolkit/) holds what the **real** `living-doc-toolkit` writes from
the collector's raw output, never from these snapshots: the
[inner](_expected/toolkit/gh-headers/generator-ready.inner.json) and
[release](_expected/toolkit/gh-headers/generator-ready.release.json) views of the technical project,
the [coverage matrix](_expected/toolkit/gh-headers/coverage-matrix.json) and the
[test catalog](_expected/toolkit/tests/ui-test-catalog.json). The same job runs the pinned toolkit in a
venv of its own, validates each artifact against its contract, asserts its content and fails on any
diff. The matrix holds the coverage verdicts, `AC:FUNC-001-03` partly covered (**1/3**) among them; its
release view differs only in `document.view`, so it has no snapshot of its own. The two warnings above
stay in both views and the matrix, and none reaches the catalog.

One thing is not in `_expected/`, and it is not a gap in the collector: what only `gh-issues/`
authors — the `## Notes` on `FEAT-001`, the `## Not In Scope` on `US-001`, and the `API` Feature
`FEAT-002`. The `doc-issues` mode that mines issue bodies is planned, not yet available, so
`examples_check` alone checks that form.

## Conventions used by this corpus

- **Minimal.** Each entity file carries every required field plus one optional field — just enough to
  show one field extension, no more. (`.project-profile.yaml` is shown complete: it is pure config
  with no optional-field layer.)
- **AC states are part of the AC grammar, not optional field extensions.** A `planned`, `in_review`,
  `active` or `deprecated` AC — with or without a target version, with or without a removal note — is
  the grammar of [`AC:<id> (…)`](../reference/glossary.md#acceptance-criterion-ac) doing its
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
  - feature-level `not_in_scope:` — `gherkin/liv_doc_func/func-002-reject-breached-password.feature`
  - `External Dependencies` — `gh-issues/feat-001-login-page.md`
  - `Aspect:` on an AC — `gherkin/liv_doc_func/func-001-validate-password-strength.feature`, in both
    its spellings: `- Aspect:` on `AC:FUNC-001-01`, and the named keyword `- rule:` on `AC:FUNC-001-03`.
    The keyword is the second spelling of the `Aspect:` extension, not a second extension (see
    [Authoring formats § AC variants](../reference/authoring-formats.md#ac-variants)), so the file still
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
  [Authoring formats § Feature in a PageObject File](../reference/authoring-formats.md#2-feature-in-a-pageobject-file).
  `RegistrationPage.ts` is the instrumented counterpart: real `getByTestId()` locators and no
  `stub-reason:`.
- **Two forms per entity, in step.** `US-001`, `FUNC-001` and `FUNC-002` each exist as a GitHub issue
  body and as a `.feature` header, and `FEAT-001` and `FEAT-003` as an issue body and a PageObject
  header. The two forms of an entity carry the same required content and, for the User Story and the
  Functionalities, the same AC set; only the optional field extension differs, by the assignment above.
- **One form for an `API` Feature.** `FEAT-002` exists as an issue body only. An `API` Feature's
  contract anchor carries no living-doc header yet, so there is no source-code form to write — see
  [Glossary — Feature](../reference/glossary.md#feature). It is documented at
  surface level (`## Functionalities` is `none`): the corpus needs it as a resolvable **target**, and a
  dependency resolves on the Feature id.
- **The dependency pair.** `FEAT-001` records `auth-api` under `External Dependencies` — a system with
  no canonical anchor, named as free text. `FEAT-003` records `FEAT-002` under `feature_dependencies` —
  an `API` Feature, named by id and validated by `tests/examples/examples_check.py`. The two fields side by side
  are the distinction the [glossary](../reference/glossary.md#feature) draws. `FEAT-003` is
  documented at surface level (`User Stories` and `Functionalities` are `none`), like `FEAT-002`.
- **The dependency is authored in both `FEAT-003` forms**, as the one optional extension of each.
  `living-doc-utilities` carries the field from `0.5.0`; an earlier release drops an authored value on
  the way in — `IGNORED_AUTHORED_KEY`, as for `notes` above. Carried, the edge does not resolve in the
  `doc-source` chain: `FEAT-002` is authored in `gh-issues/`, and a pipeline that takes its technical
  project from `gherkin/` + `pageobject/` reports `UNRESOLVED_RELATION` for a target it cannot see —
  `_expected/` shows the edge and the warning both. That is expected
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

1. **Format change.** When a field or rule on [Authoring formats](../reference/authoring-formats.md)
   or [Glossary](../reference/glossary.md) changes, update the matching example here.
2. **Implementation change (last check).** When a collector mode that mines these inputs
   (`collector-gh` `doc-source` / `ui-tests` / `doc-issues`) is implemented or changed, re-check this
   corpus **and** the pages above against what the tooling actually mines, and correct any drift.
   This is the checkpoint that catches divergence between the documented format and the shipped state.
