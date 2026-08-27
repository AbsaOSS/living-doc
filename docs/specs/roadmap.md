# Roadmap: v1 — Unified PDF & Markdown Delivery

**Status:** Draft — 2026-08-27
**Builds on:** [Documentation & Style Synchronization](doc-style-sync.md), [Architecture](architecture.md), [Data Flows & Schemas](data-flows.md), [CI Checks & QA Tooling](ci-qa-tooling.md), [Copilot & AI-Agent Tooling](copilot-ai-tooling.md), [Example Input Files for Mining](example-inputs.md)

**Related, external to this ecosystem's repos:** [`AbsaOSS/agentic-toolkit`](https://github.com/AbsaOSS/agentic-toolkit)'s `living-doc-bdd-copilot` agent authors the User Story / Feature / Functionality / AC content and `.feature` files this ecosystem's collectors mine — see [Data Flows & Schemas](data-flows.md) §9. Phase 2 below accounts for it.

## v1 goal

The ecosystem can deliver, from a single normalized dataset, both **PDF** and **Markdown** output for:

1. **`liv-doc-tech-project`ish content** — User Stories, Features, and Functionalities (the `doc-issues.json` family already collected by `collector-gh`'s `doc-issues` mode)
2. **UI test catalog** — Playwright/Gherkin BDD scenarios (`ui-tests.json`, currently only specced in `collector-gh/SPEC.md`)
3. **Coverage matrix** — the AC-to-test cross-reference `toolkit`'s `coverage_matrix` service already builds

Everything below is scoped to reach that, not to finish every idea in the specs above — the immediate next task after v1 is called out separately (Post-v1), and everything further out is explicitly deferred at the end.

## Why this order

The specs each found real problems, but not all of them block v1 equally. The ordering logic:

1. **Unify the repos before building on them.** READMEs, `CONTRIBUTING.md`, `copilot-instructions.md`, CI-workflow shape, command names, and the stated Python version have all drifted apart across the six repos. Reconciling them — and adding one shared set of developer helpers — is cheap, mechanical, and makes every later phase (and every AI-assisted change inside it) run on a consistent, correct base. This is Phase 0.
2. **Then fix what would make the build phases harder to get right** — the canonical schema rename, the `doc-source`/`ui-tests` collector modes. These are load-bearing for everything downstream.
3. **Wire the golden path** (collector → toolkit → both generators) for one content type end to end before polishing across all three — a working path beats partial polish.
4. **Security and deep CI hardening** ride along in parallel — they don't block the data-flow work and shouldn't wait for it, but should land before v1 is called "done."

## Decisions locked

Resolved with the repo owner. Each one changes what a later phase actually builds; where a decision supersedes text in another spec, that spec edit is listed in Step 1.

- **Tutorial-capture scenarios** ([Architecture](architecture.md) §4.1) live in one or more folders *parallel* to the living-doc scenario directories, named `tutorials` or `tutorial_<group>`, and carry their own `@tutorial` scenario flag. They are not part of living-doc logic. End users author them, ideally one tutorial per `.feature` file (expect large files — many Gherkin steps plus context commentary that the capture logic reuses). **Not in v1 collector scope:** Phase 2's `SPEC.md` parsing rules must explicitly exclude `tutorial*` directories and `@tutorial`-flagged scenarios from every v1 collector mode. Execution is Post-v1.
- **Schema versioning during v1** — there are no live deployments, so the canonical (`generator-ready`) and collector (`doc-issues` / `doc-source` / `ui-tests`) schemas stay at `v1.0.0` and may change shape freely as fields are added; they freeze at the v1 release. There is no additive-`v1.x`-vs-`v2.0.0` gate to reason about. *(Supersedes [Data Flows & Schemas](data-flows.md) §9's "additive `v1.x`, otherwise `v2.0.0`" framing.)*
- **`collector-ad` remaining modes** (`boards`, `pipelines`, `test_plans`, `release_notes`) — Azure DevOps support is evaluated *after* the v1 pre-release, as its own decision; current expectation is "not in v1." For the doc pass now: soften `collector-ad`'s README "todo" badges to "planned — scope decision deferred to post-v1-pre-release analysis" (no timeline, no removal); do **not** create empty stub directories.
- **`toolkit/packages/datasets_pdf` rename** — **in scope, Phase 1.** Phase 1 already migrates every `pdf_*` name to `generator-*` (artifact, schema file, output contract), so the internal Python package rename rides along rather than being deferred. *(Supersedes [Data Flows & Schemas](data-flows.md) §5 step 2 and the old "Explicitly deferred" entry.)*
- **`copilot-instructions.md` style + repo unification** — every repo documents *itself* directly (the `aquasec-scan-results` approach: module map, entry points, real commands), but within one shared structure, command vocabulary, and constraint dialect (`Must` / `Must not` / `Prefer` / `Avoid`). `CONTRIBUTING.md` is identical in every repo — one ecosystem. All repos also get the same `.claude/` helper set (skills, commands, agents). This is a **Phase 0** workstream, done before the build phases so the AI-assisted work in Phases 1–5 runs on correct, consistent instructions. *(Pulls the "AI-workflow process additions" out of "Explicitly deferred" — the roadmap they were waiting on now exists.)*
- **README structure** — one canonical action-repo README skeleton: Overview-first, intro only, a `## Developer Guide` pointer for anyone who needs to dig deeper. **The assessment and proposed skeleton go to the repo owner for sign-off before rollout.** Phase 0.
- **Python floor — 3.10, every repo identically.** A target consumer platform is limited by its environment to old Python; 3.10 is the agreed floor (3.9 has been end-of-life since Oct 2025, and 3.10 keeps `match`/`case` and PEP-604 unions so the code delta is near-zero). Per repo: `requires-python = ">=3.10"`, `ruff` / `pylint` `target-version = py310`, the composite-action `minimal_required_version` gate lowered to `"3.10.0"`, CI matrix `3.10 → 3.14` (full range), and a `tomli` backport wherever `tomllib` is used (stdlib only from 3.11). *(Supersedes [Documentation & Style Synchronization](doc-style-sync.md) §4 / §5's "standardize on 3.14".)* Phase 0.
- **AI-free principle governance** — the "pipeline runs AI-free; `agentic-toolkit` is acceleration only" principle ([Architecture](architecture.md) §4) gets a shared boilerplate paragraph near the top of every repo's `README.md` and a one-line restatement in every `CONTRIBUTING.md`. Phase 0.
- **Open PRs across the ecosystem** (checked 2026-08-27) — nothing blocks or reshapes a phase:
  - `collector-gh`, `utilities`, `toolkit`, `generator-pdf` — no open PRs.
  - `collector-ad` — 6 open, all Dependabot: 5 CI-action / dependency bumps (`setup-python`, `action-gh-release`, `checkout`, `types-requests`, `pylint`) that Phase 0's CI-unification + action-pin work supersedes, plus `mypy` 1.20 → 2.0 (major) to resolve as a Phase 0 lint-config decision.
  - `generator-markdown` — 1 Dependabot action-group bump; supersede in Phase 0.
  - `agentic-toolkit` (external) — 2 stale feature PRs (`web-fragments` skill, Graphify tool guide). Watch the `web-fragments` one only if it touches `living-doc-bdd-copilot` output format; otherwise no impact.

## Step 1 — Review all files in this repo

Before Phase 0 starts, do one consistency pass over every file in this repo (`living-doc`) — README, guides, tutorials, project pages, and all specs — since they were written incrementally across several rounds of edits. Check specifically for:

- Cross-references that point at a section number that moved (this document's own drafting is a live example of the failure mode to catch).
- Naming drift now that `generator-ready.json` is final — no stray `pdf_ready` / `doc_ready` left anywhere outside the deliberate "superseded name" callouts in [Data Flows & Schemas](data-flows.md) §5.
- Claims that were true when written but superseded by a later correction in this same conversation (e.g. the tutorial-video section's scope narrowed after first being drafted — confirm nothing elsewhere in the repo still describes the wider version).
- Every markdown link still resolves and no wiki-link (`[[...]]`) syntax slipped back in.
- **Decision-driven corrections that touch other specs are already applied** (2026-08-27) — the pass just needs to confirm nothing else still references the superseded text:
  - [Data Flows & Schemas](data-flows.md) §5 (migration step 2) and §10 — `datasets_pdf` package rename is now in scope, Phase 1.
  - [Data Flows & Schemas](data-flows.md) §9 — "additive `v1.x` / `v2.0.0`" framing replaced with "schemas stay `v1.0.0`, evolve in place until the v1 release."
  - [Documentation & Style Synchronization](doc-style-sync.md) §3.6, §4 (item 4), §5 — Python floor **3.10** (not 3.14); README-skeleton and `collector-ad`-badge decisions folded into the task list.
  - [Copilot & AI-Agent Tooling](copilot-ai-tooling.md) §5 — reframed as Phase 0; the "document repo directly + shared structure" and "identical CONTRIBUTING" decisions are locked in.

## Phase 0 — Repo unification & shared dev tooling (do first)

The specs found the same drift — in READMEs, `CONTRIBUTING.md`, `copilot-instructions.md`, CI workflows, and Python-version claims — across all six repos. Unify them before the build phases: every later phase, and every AI-assisted change inside it, is cheaper and safer on a consistent base. Mostly mechanical and parallelizable.

**Docs & conventions**

- [ ] Assess the current README variants; propose one canonical action-repo README skeleton (Overview-first, intro only, `## Developer Guide` pointer for depth). **Get owner sign-off, then** roll it out to all six repos. The skeleton bakes in the "GitHub Actions is the expected usage; local CLI is for debug only" paragraph ([Architecture](architecture.md) §2.1) and the AI-free-principle paragraph. *Ref: [Documentation & Style Synchronization](doc-style-sync.md) §5.*
- [ ] Put one identical `CONTRIBUTING.md` in every repo — this fixes `generator-markdown`'s wrong-repo Issue links and `toolkit`'s missing file in the same move. Include the one-line AI-free restatement. *Ref: [Documentation & Style Synchronization](doc-style-sync.md) §3.1, §3.3.*
- [ ] Reconcile `copilot-instructions.md` / `copilot-review-rules.md` onto one version: repo-documented-directly content (module map, entry points, real commands) inside a shared structure and a single `Must` / `Must not` / `Prefer` / `Avoid` dialect. Fill `toolkit`'s "Repo additions" with its real per-package Makefile commands (a correctness fix, not just consistency). Add the `.github/agents/` board to the repos that lack it. *Ref: [Copilot & AI-Agent Tooling](copilot-ai-tooling.md) §2, §5.*

**Shared developer tooling**

- [ ] One command vocabulary across repos — align every repo's Makefile / QA targets on the same names (`make qa` running lint + format + types + tests, etc.), so one set of instructions and one set of helpers work everywhere.
- [ ] Add the same `.claude/` helper set to every repo:
  - a **task-driven implementation command** — reads a roadmap task's spec + acceptance criteria, reads every referenced file before writing code, implements to spec, runs the QA loop to green, verifies each acceptance criterion against the actual code (not "it compiles"), writes a PR description, and stops.
  - a lighter **PR-ready verify command** — re-check every acceptance criterion against code, run the QA gates, run the review agent, report a single PR-ready yes/no with a specific fix list.
  - a **test-authoring agent** scoped to this ecosystem's real mock surface — a concrete cheat-table (GitHub API → `responses`, per existing `collector-gh/tests/` patterns; `toolkit` adapter version compatibility → golden fixtures under `tests/fixtures/collector_gh/v*`), not just principles.
  - a **docs-lifecycle rule** — when a `SPEC.md` section is implemented, its content moves out of `SPEC.md` and into the live `README.md` / mode docs, so specs shrink toward empty instead of drifting out of sync with shipped code. *Ref: [Copilot & AI-Agent Tooling](copilot-ai-tooling.md) §4.*

**Python & CI**

- [ ] Set the Python floor to **3.10** in every repo: `requires-python = ">=3.10"`, `ruff` / `pylint` `target-version = py310`, composite-action `minimal_required_version = "3.10.0"`, CI matrix `3.10 → 3.14`. Sweep each repo for `>3.10` syntax / stdlib and replace it (`tomllib` → `tomli`, etc.). *Ref: [Documentation & Style Synchronization](doc-style-sync.md) §4 item 4.*
- [ ] Converge every repo's lint/test workflow onto one shape — `permissions` block, `concurrency` group, path-filtered `detect` / `noop` jobs, and one consistent set of pinned action SHAs (`actions/checkout` and friends). This supersedes the pending Dependabot action-bump PRs in `collector-ad` and `generator-markdown`; decide `collector-ad`'s `mypy` 1.x → 2.0 bump here as a lint-config change. *Ref: [CI Checks & QA Tooling](ci-qa-tooling.md) §8.*
- [ ] Add the mandatory AquaSec Night Scan workflow to `collector-gh`, `collector-ad`, `utilities`, `toolkit`, `generator-pdf` (copy the working config from `aquasec-scan-results`). *Ref: [CI Checks & QA Tooling](ci-qa-tooling.md) §8.*

## Phase 1 — The canonical contract (blocking; everything downstream depends on this)

- [ ] Rename `pdf_ready.json` → `generator-ready.json` (schema `generator-ready-v1.0.0-schema.json`), with the old name kept as a deprecated alias. *Ref: [Data Flows & Schemas](data-flows.md) §5.*
- [ ] Rename `toolkit/packages/datasets_pdf` to a generator-agnostic name (e.g. `datasets_generator_ready` or `datasets_canonical` — pick during implementation), updating import paths and packaging metadata, with a temporary re-export shim if any consumer needs one. Done together with the artifact rename above, since Phase 1 is already touching every `pdf_*` name. *Ref: [Data Flows & Schemas](data-flows.md) §5.*
- [ ] Reframe `toolkit/docs/contracts.md`'s "Output Contract" section: the target is any generator consuming the canonical dataset, not just `generator-pdf`.
- [ ] Document the adapt → normalize → enrich → restructure stage breakdown inside `toolkit`'s own architecture docs, so the rename is paired with an accurate description of what the pipeline actually does. *Ref: [Data Flows & Schemas](data-flows.md) §7.*
- [ ] Fix `SCHEMA_SYNC.md`'s stale `CONFIRMED_MIN` value while the schema work is in hand. *Ref: [Data Flows & Schemas](data-flows.md) §3.*

## Phase 2 — Ship `doc-source` and `ui-tests` collector modes

- [ ] **Write `collector-gh/SPEC.md`'s header / AC / scenario-tag parsing rules (§3, §3.6.7, §4.6.3) against the canonical format** in [Living Doc Glossary](../guides/living-doc-glossary.md) and [Living Doc Header Types](../guides/living-doc-header-types.md) — field-for-field, including `not_in_scope`, AC-level precondition extensions, deprecation metadata, and the `@AC:<id>/aspect:<value>` tag syntax. Parse against the reference files in [Example Input Files for Mining](example-inputs.md) (author them first if not yet present). Add an explicit rule: `tutorial*` directories and `@tutorial`-flagged scenarios are out of scope for every v1 collector mode. *Ref: [Data Flows & Schemas](data-flows.md) §9.*
- [ ] Extend `doc-issues-v1.0.0-schema.json` (and the not-yet-shipped `doc-source` / `ui-tests` schemas) in place to carry those fields — the schemas stay at `v1.0.0` and evolve freely until the v1 release. *Ref: [Data Flows & Schemas](data-flows.md) §9.*
- [ ] Implement `doc_source/` (collector-gh): header-block parser, `GHDocSourceCollector`, output to `doc-source.json` — per `SPEC.md` §3.
- [ ] Implement `ui_tests/` (collector-gh): scenario-block parser, `GHUITestsCollector`, output to `ui-tests.json` — per `SPEC.md` §4.
- [ ] Ship `ui_tests/schema/ui-tests-v1.0.0-schema.json` as the actual owned schema (it currently only exists as `generator-pdf`'s consumer copy).
- [ ] Transfer schema ownership for `doc-source-v1.0.0` and `ui-tests-v1.0.0` from `toolkit` (de facto today) to `collector-gh` (the intended owner); re-label `toolkit`'s copies as owner-sourced validation copies. *Ref: [Data Flows & Schemas](data-flows.md) §3.1.*
- [ ] Re-run `toolkit coverage-matrix`'s golden tests against this real collector output, not just the hand-built fixtures used today.

## Phase 3 — Wire `generator-pdf` onto the canonical contract as the only supported path

Design rule (repo owner, 2026-08-27): **collector output is not directly consumable by a generator — normalization through `toolkit` is always required.** `generator-pdf` technically renders any JSON at `source-path` today, but the raw-collector-schema path stops being a documented option.

- [ ] Add `generator-ready-v1.0.0-schema.json` to `generator-pdf/generator/schemas/` and point `generator-pdf`'s `document-type` template sets at it; retire the raw `doc-issues` schema from the docs as an input option (keep it only as a `schema-path` a user can pass explicitly).
- [ ] Update `generator-pdf/README.md`'s Quick Start to show `collector-gh → toolkit normalize-issues → generator-pdf`; remove any `collector-gh → generator-pdf` direct example.
- [ ] Confirm (or add) a `document-type: ui-test-catalog` and `document-type: coverage-matrix` path, both consuming `toolkit`-produced output, completing PDF delivery for all three v1 content types.
- [ ] Decide where the technical project's **inner vs release view** filter lives (a `toolkit` normalize option vs a generator input) and specify the exact filter rule — drop `planned` / `in_review` entities and ACs; drop ACs no longer `active` (delivered, then deprecated). Document it in [Living Documentation Document Types](../guides/living-doc-document-types.md) once real, replacing that page's current "how it is selected is a generator input" placeholder.

## Phase 4 — Build `generator-markdown` against the same canonical contract

This is the phase that actually delivers "PDF and Markdown from the same normalized output" — everything before it is what makes this phase buildable correctly the first time instead of inventing a fourth divergent input contract.

- [ ] Scaffold `living-doc-generator-markdown` from the canonical action-repo template Phase 0 produced — not from the stale org default it has today.
- [ ] Consume `generator-ready-v1.0.0-schema.json` — the same schema `generator-pdf` now documents as primary, for User Stories / Features / Functionalities.
- [ ] Add Markdown rendering for the UI test catalog and coverage matrix content types, mirroring `generator-pdf`'s `document-type` selector.
- [ ] Share template-organization conventions (`templates/{document-type}/...`) with `generator-pdf` where not format-specific, so the "same data, different format" symmetry is visible in the codebase.
- [ ] The mandatory AquaSec workflow and full QA gate set come with the Phase 0 template, so this repo has them from day one rather than retrofitted.

## Phase 5 — Harden what Phases 1–4 rely on

Runs alongside Phases 2–4 rather than after them — none of it blocks the golden path, but all of it should land before calling v1 "done."

- [ ] Implement the pin-and-vendor schema sync mechanism: owning repos publish schemas as versioned release assets, consumers fetch into a vendored copy from a pinned tag (never `master` live), and CI fails if the vendored copy drifts from that pin. *Ref: [Data Flows & Schemas](data-flows.md) §3.2, §10.*
- [ ] Confirm `living-doc-utilities` version pins stay aligned across `collector-gh` and `collector-ad` as new versions ship.

## Post-v1 (next)

The first task queued up once v1 ships — not part of v1 itself, but not an unordered "someday" item either.

- [ ] **Tutorial-capture scenario execution** ([Architecture](architecture.md) §4.1): run the flagged, long-run Gherkin scenarios (the `@tutorial` scenarios in the `tutorials` / `tutorial_<group>` folders) and collect the outputs — screenshots per step plus step-level commentary — as structured artifacts. Scope stops there: no video-generation skill is planned in this ecosystem or in `agentic-toolkit`; turning the collected artifacts into a tutorial video is a downstream AI consumer outside this pipeline. Depends on Phase 2's scenario-mining and execution machinery existing first, which is why it queues right after v1 rather than during it.

## Explicitly deferred (not v1)

Real findings from the specs, deliberately left out of this roadmap because they're not required to hit the v1 goal above:

- **`collector-ad` / Azure DevOps support for any of this** — v1's stated scope is the GitHub-sourced content types only. A `toolkit` adapter for `collector-ad` is real future work, re-evaluated after the v1 pre-release.
- **Full `collector-ad` mode build-out** (`boards`, `pipelines`, `test_plans`, `release_notes`) — orthogonal to v1's GitHub-sourced scope entirely.
- **`agentic-toolkit`'s automation layer** (PageObject generation/healing, Playwright crawling, step-definition authoring) — v1 only needs its *catalog and scenario format* to be correctly mined by `collector-gh` (Phase 2); the BDD test-automation tooling itself is a separate concern this roadmap doesn't need to touch.
