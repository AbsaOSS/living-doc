# Decision archive

## Purpose

This page keeps the decisions behind the ecosystem's current design and those that bind planned work: what was
decided, why, and where its rule lives. It is append-only: a decision that replaces another gets a row of its own and
names the one it replaces. It is not canon; the linked page states the rule.

## Contents

- [Decisions](#decisions)

## Decisions

Numbers keep their original value and have gaps: the decisions on task order, drafting and replaced choices are left
out, and the merged pull requests record them.

| No. | Date | Decision | Why | Rule lives in |
|---|---|---|---|---|
| DEC-1 | 2026-09-27 | A page that describes a step no tool ships yet says so on the page. | That disclosure is what keeps documenting a planned part ahead of its code honest. | [Writing documentation][wd] |
| DEC-3 | 2026-09-27 | `living-doc-toolkit` keeps its `SPEC.md` process and `living-doc-collector-gh` its empty `SPEC.md`; no other repository gets one. | The first says when a prospective spec is needed, and the second anchors that rule in its repository. | [toolkit `SPEC.md`][t-spec] |
| DEC-5 | 2026-09-27 | Every page opens with `## Purpose`, and a project card has no `## Contents`. | A card is too short for a contents list, so no check may ask it for one. | [Writing documentation][wd] |
| DEC-6 | 2026-09-27 | The pages of every repository follow one page standard, held by a structure test. | One ecosystem reads the same everywhere, and the pilot proved the rules writable and checkable. | [generator-markdown docs rules][g-wd] |
| DEC-8 | 2026-09-13 | All six contracts belong to `living-doc-utilities`: models, generated schemas and runtime helpers. | One owner ends the question of who may change a shape. | [utilities contracts][u-contracts] |
| DEC-9 | 2026-09-13 | Every component pins `living-doc-utilities` exactly and imports its models and schemas, defining none of its own. | A consumer that imports the package cannot drift from it, so nothing is vendored. | [utilities R12][u-r12] |
| DEC-11 | 2026-09-13 | Entities from a tracker form one contract, `doc-entities`, because a contract names what a file holds, never its source. | The source is in `metadata`, so nothing downstream branches on it. | [utilities R4][u-r4] |
| DEC-12 | 2026-09-13 | Record arrays are keyed `entities[]`, `scenarios[]` and `content.entities[]`. | The former key named User Stories but held Features and Functionalities too. | [utilities record roots][u-roots] |
| DEC-13 | 2026-09-13 | Both tracker collectors, GitHub Issues and Azure DevOps, write `doc-entities.json`, and `metadata.producer.name` names the producer. | Downstream must not branch on which system a run read. | [utilities output layout][u-layout] |
| DEC-14 | 2026-09-13 | A collector mode is named for what it reads, and an artifact for what it holds. | Naming modes after their artifacts would hide which system a run touched. | [collector-gh modes][c-modes] |
| DEC-15 | 2026-09-13 | Every artifact carries one metadata envelope, and the legacy provenance shapes are retired with no alias window. | An alias window would keep both shapes alive indefinitely. | [utilities envelope][u-env] |
| DEC-16 | 2026-09-13 | `living-doc-toolkit` normalises the UI test catalog, and generators read toolkit outputs only. | A generator reading raw collector output re-implements normalisation, and two would disagree. | [utilities contracts][u-contracts] |
| DEC-17 | 2026-09-13 | `generator-ready` carries every authored field at the level it was authored, and the generator decides how to render it. | Expanding inheritance in the transform loses where a fact was authored. | [utilities records][u-records] |
| DEC-18 | 2026-09-13 | `living-doc-collector-ad` first builds the one body-extraction mode the first real project needs. | Building both modes before measuring a real project is guessing twice. | [living-doc#113][ld-113] |
| DEC-19 | 2026-09-13 | Every package stays `0.x`, and `1.0.0` is one event: the contracts freeze and every package moves together. | Contracts and the public API evolve in place until there are consumers to protect. | [Releasing the ecosystem][rel] |
| DEC-20 | 2026-09-13 | `entity_id` is the join key downstream, `source_ref` is provenance only, and an entity without a parseable id is not emitted. | A join on a tracker id breaks once a second system appears. | [utilities entity identity][u-id] |
| DEC-21 | 2026-09-13 | A duplicate entity or AC id is a hard input error listing every duplicate, with no precedence rule. | A precedence rule would make the misuse silently survivable. | [utilities codes][u-codes] |
| DEC-23 | 2026-09-13 | The parsers, normalisation, status derivation, relation checks and URL policy are built once, in `living_doc_utilities.authoring`. | They were being built twice, and two consumers do not justify a second package. | [utilities authoring][u-auth] |
| DEC-24 | 2026-09-13 | A composite action takes Python from `PATH` and installs its requirements into its own venv under `$RUNNER_TEMP`. | An action must never change the caller's interpreter or `PATH`. | [Ecosystem conventions][eco] |
| DEC-25 | 2026-09-14 | A collector writes `<output-path>/<mode>/<artifact>.json` and clears only its own mode directory. | Keeping projects apart is pipeline configuration, not a path convention. | [utilities output layout][u-layout] |
| DEC-26 | 2026-09-14 | Before `1.0.0` no run checks contract alignment: contract ids stay `-v1.0.0`, and `utilities_version` is never compared. | Without end customers the check would cost more than the skew it catches. | [utilities R5][u-r5] |
| DEC-27 | 2026-09-14 | A pipeline documents one project, and a toolkit run reads exactly one documentation file. | Two sources need merge logic, and a guessed precedence would hide the conflict. | [utilities one source][u-one] |
| DEC-28 | 2026-09-14 | Every collector has a required `project-id` input, written into every artifact's metadata. | The pipeline that knows the project sets it, so nothing infers it from a path. | [utilities project id][u-pid] |
| DEC-29 | 2026-09-14 | A project is documented in tracker items or in source headers, never in both in one run. | The mixed case is reported, not merged, like two documentation files. | [utilities one source][u-one] |
| DEC-30 | 2026-09-14 | The canon uses only `-` in structural positions, and one normalisation layer reads the lines each parser extracts. | Other dashes there are autocorrect defects, and a dash rule over raw text lost whole headers. | [utilities normalisation][u-norm] |
| DEC-31 | 2026-09-14 | An AC has four states, each with a version except `planned`, and `(planned)` alone is the backlog. | The version on `planned` is the target version, which made a separate state and its fields redundant. | [utilities AC grammar][u-ac] |
| DEC-32 | 2026-09-14 | A Feature has no authored status: its state is derived from its Functionalities and marked `derived`. | A Feature's changing behaviour lives in its Functionalities, which an authored status would contradict. | [utilities state][u-state] |
| DEC-35 | 2026-09-14 | Contract and authoring rules live in `living-doc-utilities`' `docs/`, and the canon and ecosystem view live here. | One home per fact, and a rule beside its code cannot drift unnoticed. | [docs/CONTEXT.md][d-contracts] |
| DEC-36 | 2026-09-14 | The optional Azure DevOps fields are in the contracts before `living-doc-collector-ad` exists. | Adding them later would ripple a contract change through every component. | [utilities Azure DevOps fields][u-ado] |
| DEC-37 | 2026-09-14 | One URL policy module serves every HTML conversion and every generator. | Three sanitisers drift, and the one that drifts lets something through. | [utilities URL policy][u-url] |
| DEC-38 | 2026-09-14 | `living-doc-collector-ad` owns the synthetic Azure DevOps fixture generator, and CI fails when a fixture differs from it. | A fixture that drifts from its generator silently stops proving anything. | [living-doc#113][ld-113] |
| DEC-39 | 2026-09-14 | Planning notes stay local and untracked, and nothing normative lives only there. | A rule kept only in planning notes ships nowhere. | [CONTEXT.md][ctx] |
| DEC-40 | 2026-09-18 | A relation resolving to the wrong entity type is `RELATION_TYPE_MISMATCH`, not `RELATION_MISMATCH`. | A code defined as either of two things stops being usable. | [utilities codes][u-codes] |
| DEC-42 | 2026-09-30 | `feature_dependencies` is authored on the Feature and targets an `API` Feature, and nothing derives it or its reverse. | A dependency belongs to the surface: a `UI` Feature calls an `API` Feature. | [Glossary: Feature][gl-feature] |
| DEC-43 | 2026-09-30 | The ecosystem has a fixed frame, F1 to F7 with exception E1, and every PR states how it relates to it. | Checking at review stops drift where it enters; an audit would only report it later. | [Principles][frame] |
| DEC-44 | 2026-09-30 | Indentation is significant in every authored input: a deeper line belongs to the open item, never becoming a sibling or key. | Parsers that stripped lines first turned nested items into siblings, silently. | [Authoring formats: Indentation][af-indent] |
| DEC-45 | 2026-09-30 | A misindented line is `MISINDENTED_LINE`, and a nested item stays in its parent's string with its relative indent. | A distinct code points the author to the right fix, and the indent lets a renderer rebuild the list. | [utilities codes][u-codes] |
| DEC-46 | 2026-10-01 | One framing pass decides every section boundary before parsing, and the normaliser and the parser both read it. | Four defects were one class: a prose predicate applied without its structural context. | [utilities normalisation][u-norm] |
| DEC-47 | 2026-10-01 | A Feature has no `deprecated_at`, and an authored one is dropped with `IGNORED_AUTHORED_KEY`. | No rule picks one date among its Functionalities', and inventing one would leave the frame. | [Glossary: Feature][gl-feature] |
| DEC-48 | 2026-10-01 | `FEATURE_WITHOUT_USER_STORY` and `FEATURE_WITHOUT_FUNCTIONALITY` replace `ORPHAN_FEATURE`, one code per direction. | One code meant two conditions in two reports, and a reader could not tell which. | [utilities codes][u-codes] |
| DEC-49 | 2026-10-05 | `living-doc-testbed` is a passive project that follows the canon fully, and the checks here assert invariants over its `master`. | A real-shaped project takes the code path production takes, where a minimal corpus misses shapes. | [The collector stage over the testbed][tb] |
| DEC-50 | 2026-10-05 | GitHub Issues as a documentation source is planned, and the `doc-issues` mode is disabled with its code kept aside. | The source-code chain came first, and porting an unshipped mode buys nothing until it is finished. | [living-doc#114][ld-114] |
| DEC-51 | 2026-10-05 | Azure DevOps as a documentation source is planned, and `living-doc-collector-ad` is not released. | The coverage matrix and the technical project need only source code and UI tests. | [living-doc#113][ld-113] |
| DEC-52 | 2026-08-27 | Tutorial scenarios live in `tutorials` or `tutorial_<group>` folders with `@tutorial`, and no collector mode reads them. | Long tutorial scenarios with commentary would pollute the entities and the coverage. | [collector-gh `doc-source`][c-source] |
| DEC-53 | 2026-08-27 | No repository has pre-commit hooks, because `make qa`, the gate CI runs, is the local feedback. | One feedback path instead of two that drift. | [Ecosystem conventions][eco] |
| DEC-54 | 2026-08-27 | Every repository supports Python 3.10 and later, in its packages, actions and CI alike. | A target platform is limited to old Python, and 3.10 keeps `match` and union types. | [Ecosystem conventions][eco] |
| DEC-56 | 2026-08-27 | Every action repository's `README.md` follows the reference repository's skeleton: an overview, then a developer guide pointer. | One ecosystem reads the same way in every repository. | [Ecosystem conventions][eco] |
| DEC-57 | 2026-08-27 | The pipeline runs without AI, and the agentic layer only speeds up authoring. | The documentation must be reproducible and auditable. | [Principles][frame] |
| DEC-58 | 2026-08-27 | Dev tooling follows its latest stable major through Dependabot, unless an upgrade breaks something or drops Python 3.10. | Small regular upgrades cost less than rare large ones. | [Ecosystem conventions][eco] |
| DEC-62 | 2026-10-05 | The toolkit's documentation command is `normalize-docs`, paired with `normalize-tests`, with no alias for its former name. | It reads no issues, and a rename after the first tags would break callers. | [toolkit commands][t-cmd] |
| DEC-63 | 2026-10-05 | A `living-doc` release names the component tags that work together, and `1.0.0` has no date and no fixed scope. | The current scope cannot carry the stability promise `1.0.0` makes. | [Releasing the ecosystem][rel] |
| DEC-64 | 2026-10-05 | Before `1.0.0` a minor may break and a patch never does, and the notes list each breaking change with its migration. | That is the common `0.x` expectation, and every consumer is still the owner's own project. | [Releasing the ecosystem][rel] |
| DEC-65 | 2026-10-05 | The agentic layer lives and ships in this repository, under `agentic/`. | The canon and the skills that write it cannot drift when they are reviewed and released together. | [The agentic layer][agentic] |
| DEC-66 | 2026-10-05 | Markdown is the first output format, and `living-doc-generator-pdf` moves onto the contracts later. | Markdown can be integrated into the owner's projects directly. | [living-doc#115][ld-115] |
| DEC-68 | 2026-10-07 | The agentic layer keeps two canon copies, regenerated here by one script, and CI fails when a copy differs. | An installed skill cannot reach `docs/`, and a copy checked at the same commit cannot drift. | [agentic CONTRIBUTING][ag-contrib] |
| DEC-71 | 2026-10-07 | An AC's named keyword is an alias of `Aspect`, and an AC declares its variants in one way only. | It reuses per-aspect coverage with no contract change, and authors keep a readable name. | [Authoring formats: AC variants][af-variants] |
| DEC-72 | 2026-10-07 | Every milestone and the release go/no-go run on the testbed with no warning accepted. | A real project mixes pipeline defects with its authors' deviations, so its warnings decide nothing. | [Run a milestone target][int-ms] |
| DEC-74 | 2026-10-07 | An AC with variants is covered, partly covered or not covered, and the toolkit computes one weighted coverage figure. | One number serves the reader and the gate, computed where the frame puts computation. | [utilities coverage][u-cov] |
| DEC-76 | 2026-10-07 | A bare `@AC:<id>` tag covers every declared value, and a tag carries at most one parameter. | A data-driven scenario must read as covered, and a second parameter cannot be told from a variant. | [Authoring formats: AC variants][af-variants] |
| DEC-77 | 2026-10-07 | A warning names its entity, AC, line and file in fields, and the inner view shows what was not loaded. | The canon promises nothing authored is lost without a word, which held only in the JSON. | [Rendering rules: not loaded][rr-loaded] |
| DEC-79 | 2026-10-15 | `real-collector.yml` runs on a change and by hand, never on a schedule. | The owner chose it, accepting that a testbed merge breaking `core` shows only at the next run. | [`real-collector.yml`][wf-rc] |
| DEC-80 | 2026-10-15 | Gate, milestone and go/no-go runs are filed under `docs/_integration/`, an internal target as a redacted row only. | The operator's machine reaches internal repositories, and a tracked folder carries steps and reports between machines. | [What may be committed][int-commit] |
| DEC-81 | 2026-10-15 | An action's full reference is the depth-2 `docs/action.md`, and `README.md` lists each input and links it. | One reference page keeps the input table testable against `action.yml`. | [collector-gh action reference][c-action] |
| DEC-82 | 2026-10-16 | The Markdown generator holds the view rules in one presentation module, which moves into `living-doc-utilities` when PDF returns. | A second generator re-implementing the rules would mirror presentation logic and drift. | [generator-markdown design rules][g-design] |
| DEC-83 | 2026-10-16 | Every generator run writes a render manifest of the ids, aspects and badges it rendered. | Parity between two output formats needs something machine-readable to compare. | [generator-markdown design rules][g-design] |
| DEC-84 | 2026-10-16 | Every field the Markdown generator emits passes the URL policy, and no raw HTML passes through. | The Markdown is committed and rendered on GitHub, so an authored link reaches every reader. | [generator-markdown design rules][g-design] |
| DEC-86 | 2026-10-19 | `living-doc-generator-markdown` has no `SPEC.md`, and its design rules live in its `DEVELOPER.md`. | A rule is stated where it is implemented and tested. | [generator-markdown design rules][g-design] |
| DEC-87 | 2026-10-19 | Every composite action's logging switch is the input `verbose-logging`. | `living-doc-utilities` already reads `INPUT_VERBOSE_LOGGING`, so the name needs no mapping. | [Ecosystem conventions][eco] |
| DEC-88 | 2026-10-19 | The venv step clears six environment variables, as the reference repository's `action.yml` does. | A caller's `PIP_ROOT` or `PIP_PYTHON` defeats the venv like the other four. | [Ecosystem conventions][eco] |
| DEC-89 | 2026-10-19 | The coverage matrix carries each AC's keyword name, and an unknown contract version is `INVALID_CONTRACT_ID`. | Cross-referencing the inputs is the toolkit's work, never a generator's. | [utilities coverage][u-cov] |
| DEC-90 | 2026-10-19 | A warning carries `source_url`, the permalink of the file its line is in, set by the collector. | A link built from the entity's source opened the wrong file for a cross-reference header. | [utilities warning fields][u-report] |
| DEC-92 | 2026-10-20 | `living-doc-toolkit` has no test guarding its requirements files, and its `DEVELOPER.md` states the rule. | An unlisted package already fails the install and the action's import check. | [toolkit setup][t-setup] |
| DEC-96 | 2026-10-20 | `document.title` comes from the run or the project id, and `document.version` defaults to `1.0.0`. | A fixed version is cheap, and the real one needs an input and a source of truth. | [toolkit document block][t-document] |
| DEC-97 | 2026-10-20 | `normalize-tests` copies `source` from its one input and writes `document.view: inner`. | The catalog has no documentation input and no field that depends on the view. | [utilities envelope][u-env] |
| DEC-98 | 2026-10-20 | A test linked to a `planned` or `in_review` AC keeps its link in the catalog, and the matrix has no row for it. | The matrix counts only `active` and `deprecated` criteria. | [utilities coverage][u-cov] |
| DEC-99 | 2026-10-20 | No stats ledger spans a run: each transform's `FIELD_LOSS` check and each snapshot's read are the guarantee. | Its classification rules existed nowhere, and the pipeline works without the report. | [utilities#232][u-232] |
| DEC-101 | 2026-10-20 | Every PR stays in sync with the canon and names each canon rule it implements, with its page. | Seven mismatches with the contracts showed work drifting from the canon unnoticed. | [PR Description][pr] |
| DEC-104 | 2026-10-21 | Each toolkit command keeps its lineage table in its own package, whose completeness only the tests check. | A field the table does not know must not stop a run, while `FIELD_LOSS` stays an error. | [toolkit lineage][t-lineage] |
| DEC-105 | 2026-10-21 | `living-doc-toolkit` has one version, its release tag, read at run time from the installed `living-doc-core`. | The CLI also runs outside GitHub, so package metadata is the one source both read. | [toolkit versioning][t-version] |
| DEC-106 | 2026-10-21 | A field the pinned models do not know fails the read, and the fleet ships as one matched set. | The error already names the fix, and a skipped field would still miss the document. | [utilities R9][u-r9] |
| DEC-107 | 2026-10-22 | Each `doc-source` record root holds one entity type, and `full_sample` holds only records a producer could write. | A sample no producer could write failed the toolkit's own input validation. | [utilities check 3][u-check3] |
| DEC-108 | 2026-10-22 | `normalize-tests`' `FIELD_LOSS` check adds up each path across the catalog's three scenario groups. | A scenario lands in one of three groups, so a one-group mapping raised false losses. | [toolkit `normalize-tests`][t-tests] |
| DEC-109 | 2026-10-22 | A catalog feature file is keyed by its scenarios' `scenario_id` up to the last `/` until a contract names the repository. | Keyed by path alone, two repositories' files with one name would merge. | [utilities#234][u-234] |
| DEC-110 | 2026-10-27 | That key is used only when exactly `<org>/<repo>` precedes the path, and `source_ref.native_id` otherwise. | Any other prefix names no repository the contracts know. | [toolkit grouping][t-group] |
| DEC-111 | 2026-10-27 | `coverage-matrix` computes `selected_stats` over what it counts and checks `FIELD_LOSS` against the documentation input only. | Otherwise a project whose criteria are all `planned` could get no matrix. | [toolkit run-time check][t-runtime] |
| DEC-112 | 2026-10-27 | A tag with an aspect its AC does not declare is `STALE_AC_REF`, and it counts only on an AC without aspects. | Without aspects the tag names the criterion, and with them a typo must not cover them all. | [toolkit warnings][t-warnings] |
| DEC-116 | 2026-10-30 | A page carries no code anchor, and a depth-2 page's anchors live in the `## Code map` of the `CONTEXT.md` beside it. | A reader needs the fact, and an agent reads the `CONTEXT.md` beside the code first. | [toolkit anchors][t-anchors] |
| DEC-118 | 2026-10-30 | That code-map rule holds in every repository whose pages were rebuilt. | One rule across the fleet, and the toolkit's was the newer one. | [generator-markdown anchors][g-anchors] |
| DEC-119 | 2026-10-30 | `tests/docs/pages.py` stays a hand-written parser, with no Markdown library. | It reads every page so far, and a library would be a new dependency in each repository. | [`pages.py`][pages] |
| DEC-120 | 2026-10-30 | A component's pages link `living-doc-utilities`' docs at `master` though it pins a release, until a linked page changes ahead of the pin. | The owner keeps `master` while no linked rule is newer than the pinned release. | [living-doc#136][ld-136] |
| DEC-121 | 2026-10-30 | A page's `## Purpose` says what the page is for, not who reads it. | Pages that open with their job read better, and the level already implies the reader. | [Writing documentation][wd] |
| DEC-122 | 2026-10-30 | No test checks that a page's facts have code-map items, and review samples them instead. | A fact is prose that a test cannot match to an item reliably. | [toolkit#114][t-114] |
| DEC-123 | 2026-11-04 | The data-flow, contract and error pages here summarise `living-doc-utilities` and link its rules. | A second definition of a rule would drift. | [docs/CONTEXT.md][d-contracts] |
| DEC-124 | 2026-11-04 | The retired-names check runs with `--strict` on every PR and push, and each exception names its reason. | A check that only reports is ignored. | [`retired-names.yml`][wf-rn] |
| DEC-125 | 2026-11-05 | The integration runner clones each component at its pin or a tag, and never writes a developer's checkout. | Each component reads its own checkout's configuration, which a run must not overwrite. | [Run a milestone target][int-ms] |
| DEC-126 | 2026-11-05 | A planned tutorial keeps its path and carries no workflow, and the page rules live only in `CONTRIBUTING.md`. | A workflow marked as not running still gets copied, and the path keeps outside links landing. | [Writing documentation][wd] |
| DEC-128 | 2026-11-09 | `living-doc-utilities` keeps its pages' code maps in `CONTEXT.md` files under `docs/`. | Hundreds of anchors would triple the package `CONTEXT.md` files an agent reads on every change. | [utilities docs rules][u-wd] |
| DEC-129 | 2026-11-09 | The release go/no-go is one runner run over the testbed, its exit code the verdict, before any tag. | A tag is never re-cut, so a no-go after tagging would cost a patch per component. | [Release go/no-go][int-gng] |
| DEC-131 | 2026-11-11 | Every repository has one release-notes configuration, and each chapter names both label schemes. | The repositories' forms set two label schemes, and a draft on one scheme loses the other's issues. | [.github/CONTEXT.md][gh-ctx] |
| DEC-133 | 2026-11-11 | Every open debt is a GitHub issue in the repository it concerns, and planning goes on in issues. | Issues are public and tracked, where the fleet's other work already lives. | [Debt overview][debt] |
| DEC-134 | 2026-11-11 | The shared configuration also fixes the PR check's skip labels, both workflows' permissions and the notes title. | Without them the fleet would have ended on three PR-check configurations. | [.github/CONTEXT.md][gh-ctx] |
| DEC-135 | 2026-11-12 | The agentic layer is installed from `master`, and its links into the canon point at `master`. | Its canon copies are generated, and the layer installed, from `master`. | [agentic README][ag-readme] |
| DEC-136 | 2026-11-12 | A link from a page here to a component's page points at `master` while the ecosystem is under development. | The owner accepts a linked page newer than the tag the examples run. | [docs/CONTEXT.md][d-conventions] |
| DEC-137 | 2026-11-12 | The one-off workflow `tutorial-by-tag.yml` is removed by an issue of its own, and the merged PR stays as it is. | A merged PR's missed criterion is fixed forward, never by rewriting the record. | [living-doc#133][ld-133] |
| DEC-138 | 2026-11-12 | The decisions behind the design stay on this page, and the planned work is seven epics in `living-doc`. | The issues hold the plan, and the repository keeps a small record of why its code is as it is. | [Purpose](#purpose) |
| DEC-139 | 2026-11-12 | `docs/_backlog/debt-overview.md` lists each open tech-debt or epic issue by its search keys and nothing else. | The issues hold the data, and the page serves a fast search by people and agents. | [Debt overview rules][debt-rules] |
| DEC-140 | 2026-11-12 | A check compares the debt overview with the open issues weekly and on a change, and opens a documentation task on drift. | The issue shows when a debt is done, and the weekly check keeps the page true without a commit. | [Debt overview rules][debt-rules] |

[wd]: ../../CONTRIBUTING.md#writing-documentation
[pr]: ../../CONTRIBUTING.md#pr-description
[tb]: ../../CONTRIBUTING.md#the-collector-stage-over-the-testbed
[agentic]: ../../CONTRIBUTING.md#the-agentic-layer
[rel]: ../../CONTRIBUTING.md#releasing-the-ecosystem
[eco]: ../../CONTRIBUTING.md#ecosystem-conventions
[ctx]: ../../CONTEXT.md#key-decisions
[d-contracts]: ../CONTEXT.md#contracts
[d-conventions]: ../CONTEXT.md#conventions
[gh-ctx]: ../../.github/CONTEXT.md#invariants-and-gotchas
[frame]: ../introduction/principles.md#the-frame
[gl-feature]: ../reference/glossary.md#feature
[af-indent]: ../reference/authoring-formats.md#indentation
[af-variants]: ../reference/authoring-formats.md#ac-variants
[rr-loaded]: ../reference/rendering-rules.md#what-was-not-loaded
[int-commit]: ../_integration/README.md#what-may-be-committed
[int-ms]: ../_integration/README.md#run-a-milestone-target
[int-gng]: ../_integration/README.md#release-gono-go
[debt]: ../_backlog/debt-overview.md
[debt-rules]: ../_backlog/debt-overview.md#rules
[pages]: ../../tests/docs/pages.py
[wf-rc]: ../../.github/workflows/real-collector.yml
[wf-rn]: ../../.github/workflows/retired-names.yml
[ag-readme]: ../../agentic/README.md
[ag-contrib]: ../../agentic/CONTRIBUTING.md
[ld-113]: https://github.com/AbsaOSS/living-doc/issues/113
[ld-114]: https://github.com/AbsaOSS/living-doc/issues/114
[ld-115]: https://github.com/AbsaOSS/living-doc/issues/115
[ld-133]: https://github.com/AbsaOSS/living-doc/issues/133
[ld-136]: https://github.com/AbsaOSS/living-doc/issues/136
[u-232]: https://github.com/AbsaOSS/living-doc-utilities/issues/232
[u-234]: https://github.com/AbsaOSS/living-doc-utilities/issues/234
[t-114]: https://github.com/AbsaOSS/living-doc-toolkit/issues/114
[u-contracts]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts.md#contracts
[u-auth]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/authoring.md#decisions
[u-wd]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/DEVELOPER.md#writing-documentation
[u-r12]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/component-checks.md#r12-no-component-mirrors-a-contract
[u-check3]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/component-checks.md#check-3-full-sample-test
[u-r4]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/artifact-rules.md#r4-a-file-declares-its-contract
[u-r5]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/artifact-rules.md#r5-consumers-check-an-input-in-a-fixed-order
[u-roots]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/artifact-rules.md#contracts
[u-env]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/artifact-rules.md#the-metadata-envelope
[u-r9]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/schema-rules.md#r9-records-are-closed-maps-are-typed-and-keyed
[u-one]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#one-project-one-pipeline-one-documentation-source
[u-pid]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#project-id
[u-layout]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#collector-output-layout
[u-id]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/entities-and-state.md#entity-identity
[u-state]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/entities-and-state.md#state-and-state-origin
[u-ado]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/entities-and-state.md#fields-prepared-for-azure-devops
[u-codes]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/errors.md#codes
[u-report]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/errors.md#how-codes-are-reported
[u-records]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/rendering.md#records-and-presentation
[u-cov]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/rendering.md#coverage
[u-norm]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/authoring/normalisation.md#where-normalisation-runs
[u-ac]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/authoring/ac-grammar.md#header
[u-url]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/authoring/urls-and-html.md#url-policy
[t-spec]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/SPEC.md
[t-setup]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/DEVELOPER.md#setup
[t-version]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/DEVELOPER.md#versioning
[t-anchors]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/DEVELOPER.md#anchors
[t-cmd]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/action.md#commands
[t-document]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/packages/services/normalize_docs/README.md#the-document-block
[t-lineage]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/packages/services/normalize_docs/README.md#lineage
[t-tests]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/packages/services/normalize_tests/README.md#lineage
[t-group]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/packages/services/normalize_tests/README.md#grouping-and-order
[t-runtime]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/packages/services/coverage_matrix/README.md#the-run-time-check
[t-warnings]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/packages/services/coverage_matrix/README.md#warnings
[c-modes]: https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/README.md#inputs-and-outputs
[c-source]: https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/doc_source/README.md
[c-action]: https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md
[g-wd]: https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/DEVELOPER.md#writing-documentation
[g-design]: https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/DEVELOPER.md#design-rules
[g-anchors]: https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/DEVELOPER.md#anchors
