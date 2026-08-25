# Roadmap: v1 — Unified PDF & Markdown Delivery

**Status:** Draft — 2026-08-25
**Builds on:** [Documentation & Style Synchronization](doc-style-sync.md), [Architecture](architecture.md), [Data Flows & Schemas](data-flows.md), [CI Checks & QA Tooling](ci-qa-tooling.md), [Copilot & AI-Agent Tooling](copilot-ai-tooling.md)

**Related, external to this ecosystem's repos:** [`AbsaOSS/agentic-toolkit`](https://github.com/AbsaOSS/agentic-toolkit)'s `living-doc-bdd-copilot` agent authors the User Story / Feature / Functionality / AC content and `.feature` files this ecosystem's collectors mine — see [Data Flows & Schemas](data-flows.md) §9. Phase 2 below accounts for it.

## v1 goal

The ecosystem can deliver, from a single normalized dataset, both **PDF** and **Markdown** output for:

1. **`liv-doc-tech-project`ish content** — User Stories, Features, and Functionalities (the `doc-issues.json` family already collected by `collector-gh`'s `doc-issues` mode)
2. **UI test catalog** — Playwright/Gherkin BDD scenarios (`ui-tests.json`, currently only specced in `collector-gh/SPEC.md`)
3. **Coverage matrix** — the AC-to-test cross-reference `toolkit`'s `coverage_matrix` service already builds

Everything below is scoped to reach that, not to finish every idea in the four specs above — the immediate next task after v1 is called out separately (Post-v1), and everything further out is explicitly deferred at the end.

## Why this order

The four specs each found real problems, but not all of them block v1 equally. The ordering logic:

1. **Fix things that would make later steps harder to build correctly** first (schema rename, doc-source/ui-tests modes) — these are load-bearing for the rest.
2. **Wire the golden path** (collector → toolkit → both generators) before polishing anything alongside it — a working end-to-end path for one content type beats partial polish across three.
3. **Security and CI hardening** ride along in parallel — they don't block the data-flow work and shouldn't wait for it, but they also don't need to finish before the golden path does.
4. **Doc-sync and Copilot-instruction de-drift** are cheap and high-leverage but not on the critical path to v1 functionality — sequenced to happen alongside Phase 1 (fresh eyes on the repos anyway) rather than blocking it.

## Step 1 — Resolve the open questions

Before any Phase 0 work starts: these are real unresolved decisions surfaced across the specs — genuinely open, not things this document can settle on its own. Get an answer to each before committing to the phases below, since several of them change what a later phase actually builds.

**Format & directory conventions**
- What's the directory convention for the flagged, long-run tutorial-capture scenarios ([Architecture](architecture.md) §4.6) — a new directory alongside `liv_doc_us`/`liv_doc_func`, or do they live "outside the living-doc directories" the way smoke/regression/exploratory scenarios already do per the glossary?
- Once `collector-gh/SPEC.md` is reconciled against `agentic-toolkit`'s format (Phase 2), does the resulting schema bump ship as additive `v1.x` (every new field optional) or `v2.0.0`? Depends on whether `not_in_scope`/deprecation-metadata/AC-level precondition extensions can all be modeled as optional without breaking the "same shape, richer" goal. *[Data Flows & Schemas](data-flows.md) §9.2.*

**Component fate**
- `generator-mdoc`: migrate onto the canonical `generator-ready.json` contract, or formally mark deprecated/maintenance-only? Nothing in any repo states an intended timeline either way today. *[Architecture](architecture.md) §4, Phase 4 task.*
- `collector-ad`'s remaining modes (`boards`, `pipelines`, `test_plans`, `release_notes`): is there an owner or rough timeline, or are they aspirational placeholders in the README with no near-term plan? Affects how the "todo" badges in that README should be worded (see [Documentation & Style Synchronization](doc-style-sync.md) §3.5).
- `packages/datasets_pdf` → a generator-agnostic package name: worth doing once `generator-markdown` exists and needs the package, or not worth the churn ever? *[Data Flows & Schemas](data-flows.md) §5, task list.*

**Process & convention decisions**
- Should `copilot-instructions.md` converge fully on the portable "core rules + Repo additions" template, or adopt `aquasec-scan-results`'s "document the repo directly" style for the architecture-facing sections specifically (the two aren't mutually exclusive, but nobody's picked)? *[Copilot & AI-Agent Tooling](copilot-ai-tooling.md) §5.*
- Is `generator-pdf`'s README structure (Overview-first, no "Motivation" heading) the new template direction for all action repos, or an unintentional one-off that should be reverted to match the shared template? *[Documentation & Style Synchronization](doc-style-sync.md) §5.*
- Is `living-doc-utilities`' looser `requires-python = ">=3.12"` (versus every other repo's stated/enforced 3.14) intentional — is the shared library meant to support older Python than the actions that consume it — or just unreconciled? *[Documentation & Style Synchronization](doc-style-sync.md) §3.4.*

**Governance of the AI-free principle**
- [Architecture](architecture.md) §4.5's "the pipeline must run AI-free, `agentic-toolkit` is acceleration only" is stated in this root repo's specs — but nothing in any individual `living-doc-*` repo's own README/CONTRIBUTING currently states this principle explicitly. Should it be added there too (so it's visible to someone who lands directly on `collector-gh` or `toolkit` without ever reading this repo), and if so, in what form — a shared boilerplate paragraph, like the CONTRIBUTING.md template already is?

## Step 2 — Review all files in this repo

Before Phase 0 starts, do one consistency pass over every file in this repo (`living-doc`) — README, guides, tutorials, project pages, and all six specs — since they were written incrementally across several rounds of edits. Check specifically for:

- Cross-references that point at a section number that moved (this document's own renumbering during drafting is a live example of the failure mode to catch).
- Naming drift now that `generator-ready.json` is final — no stray `pdf_ready`/`doc_ready` left anywhere outside the deliberate "superseded name" callouts in [Data Flows & Schemas](data-flows.md) §5.
- Claims that were true when written but superseded by a later correction in this same conversation (e.g. the tutorial-video section's scope narrowed after first being drafted — confirm nothing elsewhere in the repo still describes the wider version).
- Every markdown link still resolves and no wiki-link (`[[...]]`) syntax slipped back in.

## Phase 0 — Groundwork (small, do first, unblocks everything else)

Small, mostly independent tasks that reduce risk before the bigger builds start.

- [ ] **[Security]** Add the mandatory AquaSec Night Scan workflow to `collector-gh`, `collector-ad`, `utilities`, `toolkit`, `generator-pdf` (copy the working config from `generator-mdoc`). *Ref: [CI Checks & QA Tooling](ci-qa-tooling.md) §8.*
- [ ] **[Docs]** Fix the three broken/stale cross-repo links (`generator-mdoc`'s stale rename, `generator-markdown`'s wrong-repo `CONTRIBUTING.md`). *Ref: [Documentation & Style Synchronization](doc-style-sync.md) §3.1.*
- [ ] **[Docs]** Fix `SCHEMA_SYNC.md`'s stale `CONFIRMED_MIN` value; add the missing `CONTRIBUTING.md` to `toolkit`. *Ref: [Data Flows & Schemas](data-flows.md) §3, [Documentation & Style Synchronization](doc-style-sync.md) §3.3.*
- [ ] **[Usage clarity]** Add the "GitHub Actions is the expected usage; local CLI is for debug" note to each repo's `README.md`. *Ref: [Architecture](architecture.md) §2.1, Phase 0.*
- [ ] **[AI tooling]** De-drift `copilot-instructions.md`/`copilot-review-rules.md` onto one reconciled version; fill in `toolkit`'s empty "Repo additions" with its real per-package Makefile commands. *Ref: [Copilot & AI-Agent Tooling](copilot-ai-tooling.md) §5.* Doing this now, before the heavier Phase 1–3 build-out, means the AI-assisted work on those phases runs on correct instructions instead of `toolkit`'s currently-wrong default commands.

## Phase 1 — The canonical contract (blocking; everything else depends on this)

- [ ] Rename `pdf_ready.json` → `generator-ready.json` (schema `generator-ready-v1.0.0-schema.json`), with the old name kept as a deprecated alias. *Ref: [Data Flows & Schemas](data-flows.md) §5.*
- [ ] Reframe `toolkit/docs/contracts.md`'s "Output Contract" section: target is any generator consuming the canonical dataset, not just `generator-pdf`.
- [ ] Document the adapt → normalize → enrich → restructure stage breakdown inside `toolkit`'s own architecture docs, so the rename in the previous task is paired with an accurate description of what the pipeline actually does. *Ref: [Data Flows & Schemas](data-flows.md) §7.*

## Phase 2 — Ship `doc-source` and `ui-tests` collector modes

Both are already fully specced in `collector-gh/SPEC.md` — this phase is "build what's already designed," not new design work, **except for one correction that must land first.**

- [ ] **Reconcile `collector-gh/SPEC.md` against `agentic-toolkit`'s current living-doc format before writing any parser code.** `SPEC.md`'s header/AC parsing rules are behind the authoring-side format the `living-doc-bdd-copilot` agent actually produces — implementing `SPEC.md` as currently written would ship a collector that mis-parses or silently drops `not_in_scope`, AC-level precondition extensions, deprecation metadata, and `@AC:<id>/aspect:<value>`-tagged scenarios. Update `SPEC.md`'s §3 (header format), §3.6.7 (AC block parsing), and §4.6.3 (scenario tag parsing) to match `agentic-toolkit`'s `skills/shared/references/living-doc-glossary.md` and `living-doc-bdd-schemas.md` field-for-field. *Ref: [Data Flows & Schemas](data-flows.md) §9.1 for the full delta table.*
- [ ] Bump `doc-issues-v1.0.0-schema.json` (and the not-yet-shipped `doc-source`/`ui-tests` schemas) to account for the new fields from the reconciliation above — additive `v1.x` if every new field can be optional, otherwise `v2.0.0`. *Ref: [Data Flows & Schemas](data-flows.md) §9.2.*
- [ ] Implement `doc_source/` (collector-gh): header-block parser, `GHDocSourceCollector`, output to `doc-source.json` — per the reconciled `SPEC.md` §3.
- [ ] Implement `ui_tests/` (collector-gh): scenario-block parser, `GHUITestsCollector`, output to `ui-tests.json` — per the reconciled `SPEC.md` §4.
- [ ] Ship `ui_tests/schema/ui-tests-v1.0.0-schema.json` as the actual owned schema (it currently only exists as `generator-pdf`'s consumer copy — see Phase 1 ownership note below).
- [ ] Transfer schema ownership for `doc-source-v1.0.0` and `ui-tests-v1.0.0` from `toolkit` (de facto today) to `collector-gh` (the intended owner); re-label `toolkit`'s copies as owner-sourced validation copies. *Ref: [Data Flows & Schemas](data-flows.md) §3.1.*
- [ ] Re-run `toolkit coverage-matrix`'s golden tests against this real collector output, not just the hand-built fixtures used today.

## Phase 3 — Wire `generator-pdf` onto the canonical contract as the primary path

- [ ] Add `generator-ready-v1.0.0-schema.json` to `generator-pdf/generator/schemas/`; document it in `README.md` as the recommended `document-type: user-stories` source (today's docs point at the raw collector schema instead).
- [ ] Update `generator-pdf/README.md`'s Quick Start to show `collector-gh → toolkit normalize-issues → generator-pdf`, not `collector-gh → generator-pdf` directly.
- [ ] Confirm (or add) a `document-type: ui-test-catalog` and `document-type: coverage-matrix` path both consuming `toolkit`-produced output, completing PDF delivery for all three v1 content types.

## Phase 4 — Build `generator-markdown` against the same canonical contract

This is the phase that actually delivers "PDF and Markdown from the same normalized output" — everything before it is what makes this phase buildable correctly the first time instead of inventing a fourth divergent input contract.

- [ ] Scaffold `living-doc-generator-markdown` from the canonical action-repo template (once Phase 0's doc-sync work has produced one) — not from the stale org default it has today.
- [ ] Consume `generator-ready-v1.0.0-schema.json` — same schema `generator-pdf` now documents as primary, for User Stories/Features/Functionalities.
- [ ] Add Markdown rendering for the UI test catalog and coverage matrix content types, mirroring `generator-pdf`'s `document-type` selector.
- [ ] Share template-organization conventions (`templates/{document-type}/...`) with `generator-pdf` where not format-specific, so the "same data, different format" symmetry is visible in the codebase.
- [ ] Add the mandatory AquaSec workflow and full QA gate set to the new repo from day one (not retrofitted later, unlike the rest of the ecosystem today).

## Phase 5 — Harden what Phase 1–4 relies on

Runs alongside Phases 2–4 rather than after them — none of it blocks the golden path, but all of it should land before calling v1 "done."

- [ ] Implement the pin-and-vendor schema sync mechanism: owning repos publish schemas as versioned release assets, consumers fetch into a vendored copy from a pinned tag (never `master` live), and CI fails if the vendored copy drifts from that pin. *Ref: [Data Flows & Schemas](data-flows.md) §3.2, §10.*
- [ ] Harden the shared lint/test workflow: `permissions` block, `concurrency` group, path-filtered `detect`/`noop` jobs — converging on the `aquasec-scan-results` pattern. *Ref: [CI Checks & QA Tooling](ci-qa-tooling.md) §8.*
- [ ] Re-pin `actions/checkout` (and other actions) to one consistent SHA across all repos touched in this roadmap.
- [ ] Realign `living-doc-utilities` version pins across `collector-gh`, `collector-ad`, `generator-mdoc` (currently split 0.3.1/0.3.1/0.3.0).

## Post-v1 (next)

The first task queued up once v1 ships — not part of v1 itself, but not an unordered "someday" item either.

- [ ] **Tutorial-capture scenario execution** ([Architecture](architecture.md) §4.6): run flagged, long-run Gherkin scenarios and collect the outputs — screenshots per step plus step-level commentary — as structured artifacts. Scope stops there: no video-generation skill is planned in this ecosystem or in `agentic-toolkit`; turning the collected artifacts into a tutorial video is a downstream AI consumer outside this pipeline. Depends on Phase 2's scenario-mining and execution machinery existing first, which is why it queues right after v1 rather than during it.

## Explicitly deferred (not v1)

Real findings from the four specs, deliberately left out of this roadmap because they're not required to hit the v1 goal above:

- **`generator-mdoc` migration or deprecation decision** — v1 doesn't require touching the MDoc path at all; it's additive (PDF + Markdown), not a replacement for what already works. Revisit once v1 ships.
- **`collector-ad` / Azure DevOps support for any of this** — v1's stated scope is the GitHub-sourced content types only. A `toolkit` adapter for `collector-ad` is real future work, not v1.
- **`toolkit/packages/datasets_pdf` → `datasets_doc` package rename** — the artifact rename (Phase 1) is enough; renaming the Python package is a bigger, purely-cosmetic follow-up.
- **The AI-workflow process additions** (roadmap-task-driven implementation command, PR-ready verify command, docs-lifecycle automation) from [Copilot & AI-Agent Tooling](copilot-ai-tooling.md) §5 — valuable, but tooling-around-the-work, not the work itself. Worth doing once this roadmap exists to drive them, i.e. after this document, not before.
- **Full `collector-ad` mode build-out** (`boards`, `pipelines`, `test_plans`, `release_notes`) — orthogonal to v1's GitHub-sourced scope entirely.
- **`agentic-toolkit`'s automation layer** (PageObject generation/healing, Playwright crawling, step-definition authoring) — v1 only needs its *catalog and scenario format* to be correctly mined by `collector-gh` (Phase 2); the BDD test-automation tooling itself is a separate concern this roadmap doesn't need to touch.
