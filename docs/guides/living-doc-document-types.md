# Living Documentation Document Types

The pipeline produces **three kinds of document**. Each is a distinct dataset with its own
prerequisites, and each can be rendered as **Markdown** or **PDF** by pointing a generator at it.

- For the entities these are built from (User Story, Feature, Functionality, AC), see [Living Doc Glossary](living-doc-glossary.md).
- For the file formats a collector mines, see [Living Doc Header Types](living-doc-header-types.md).
- To choose Markdown vs PDF, see [Choosing a Generator](choosing-a-generator.md).

## At a glance

| Document type | Answers | Built from | Needs |
|---|---|---|---|
| [Technical project](#technical-project) | *What are we building, and what's the status?* | User Stories, Features, Functionalities + their ACs | One collector source |
| [Test catalog](#test-catalog) | *What behaviours do our tests cover?* | Gherkin `.feature` files | Gherkin scenarios in the repo |
| [Coverage matrix](#coverage-matrix) | *Which acceptance criteria actually have a test?* | Technical project **×** test catalog | Both of the above, for the same system |

Everything here is **mined, never hand-edited as output** — you maintain the *inputs* (issues,
source-code header blocks, `.feature` files); the pipeline regenerates the document on every run.

---

## Technical project

The catalog of **what the system is** — every User Story, the Features that satisfy it, the
Functionalities under each Feature, and the acceptance criteria at each level, with version and
status.

**Structure**

```
User Story  (US-nnn)  — actor, capability, business value, ACs
  └─ Feature  (FEAT-nnn)  — a system surface (page, API), owner, status
       └─ Functionality  (FUNC-nnn)  — one atomic behaviour, ACs
```

See the [relationship diagram](living-doc-glossary.md#relationship-diagram) for the full model.

**Built from** — one of:

| Input | Collector mode | Status |
|---|---|---|
| GitHub issues labelled as US / Feature / Functionality | `collector-gh` `doc-issues` | Available |
| Source-code header blocks (see [Header Types](living-doc-header-types.md)) | `collector-gh` `doc-source` | Specced, not yet built |
| Azure DevOps work items | `collector-ad` `work-items` | Planned |

**Prerequisites** — a collector source, nothing else. This is the base document; the other two build
on it.

**Two views.** The same technical project is generated in one of two views:

| View | Contains | Use for |
|---|---|---|
| **Inner** | Everything, unchanged — `planned`, `in_review`, `active`, and `deprecated` entities and ACs alike | Team-internal planning and traceability; nothing is hidden |
| **Release** | `planned` / `in_review` items dropped; ACs that are no longer `active` (delivered, then deprecated) filtered out — i.e. *what was actually shipped and is still current* | A release note / delivery record shared outside the team |

The view is a generation-time filter over the same mined data — no separate authoring. How it is
selected is a generator input; see the generator's README.

**Generator input:** `document-type: user-stories`.

---

## Test catalog

The list of **behaviours the automated tests document** — every Gherkin scenario, grouped by the
Feature / Functionality it exercises, with its `@AC:` links.

**Structure**

```
Feature file  (@US_ID / @FUNC_ID)
  └─ Scenario  (# AC: comment + @AC: tag)
       └─ steps
```

Scenario-to-AC traceability comes from the `# AC:` comment and `@AC:` tag on each scenario — see
[Living Doc Glossary § Acceptance Criterion](living-doc-glossary.md#acceptance-criterion-ac).

**Built from** — Gherkin `.feature` files in the living-doc directories
(`features/liv_doc_us/`, `features/liv_doc_func/` by default), mined by `collector-gh`'s `ui-tests`
mode *(specced in `collector-gh/SPEC.md`, not yet built)*.

**Prerequisites** — `.feature` files that follow the [feature-file header format](living-doc-header-types.md#1-user-story-in-a-gherkin-feature-file)
and carry `@AC:` tags. A test catalog can be produced without a technical project, but it is far more
useful alongside one.

**Generator input:** `document-type: ui-test-catalog`.

---

## Coverage matrix

The **cross-reference between acceptance criteria and tests** — for every AC in the technical
project, whether a scenario in the test catalog covers it, and which one. This is what surfaces
*gaps* (ACs with no test) and *orphans* (scenarios not tied to any AC).

**Structure** — a matrix of `AC ID × scenario`, with a covered / not-covered verdict per AC and a
per-Feature rollup.

**Built from** — the technical project (`doc-source.json`: User Stories, Features, Functionalities +
ACs) **and** the test catalog (`ui-tests.json`: scenarios + `@AC:` tags), joined by
[`living-doc-toolkit`](https://github.com/AbsaOSS/living-doc-toolkit)'s `coverage-matrix` service.

**Prerequisites** — **both** other document types, and they must describe **the same system**:

- a technical project with ACs assigned stable IDs,
- a test catalog whose scenarios tag those same AC IDs,
- both mined from the same repository, or [merged into one dataset](../specs/data-flows.md) (§8) if they come from different sources.

**Generator input:** `document-type: coverage-matrix`.

---

## Prerequisite matrix

| To produce… | You need | Which in turn needs |
|---|---|---|
| Technical project | A collector source (issues, source code, or work items) | Entities authored in the [documented format](living-doc-header-types.md) |
| Test catalog | Gherkin `.feature` files with `@AC:` tags | — |
| Coverage matrix | Technical project **+** test catalog, same system | Both of the above; AC IDs consistent across the two |

## Related

- [Choosing a Generator](choosing-a-generator.md) — Markdown vs PDF for any of these
- [Getting Started](getting-started.md) — assemble the pipeline
- [Living Documentation in 5 Minutes](../introduction/quickstart.md) — the fast path
- [Example Input Files for Mining](../specs/example-inputs.md) — reference inputs for each document type
- [Data Flows & Schemas](../specs/data-flows.md) — the JSON contracts and multi-source handling
