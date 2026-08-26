# Spec: Copilot Instructions, Review Rules, Agents & AI-Assisted Workflow Tooling

**Status:** Draft — 2026-08-25
**Scope reviewed:** `.github/copilot-instructions.md`, `.github/copilot-review-rules.md`, and `.github/agents/*.agent.md` across all 6 `living-doc-*` repos plus `generate-release-notes` and `aquasec-scan-results`; general prior art on AI-assisted development workflows for the "propose their application" part of this spec (§4).

## 0. Governing principle: acceleration, not dependency

This applies to every AI-agent artifact this spec covers, not just this ecosystem's own `.github/agents/`: the `copilot-instructions.md`/`copilot-review-rules.md`/agent-board tooling in these repos, and [`agentic-toolkit`](https://github.com/AbsaOSS/agentic-toolkit)'s `living-doc-bdd-copilot` skill family covered in [Architecture](architecture.md) §4, exist to make development and content-authoring *faster* — never to make either one *required*. Every `living-doc-*` repo builds, tests, and runs with zero AI involvement; a contributor who never opens Copilot or Claude can do every task these agent definitions describe by hand, just slower. Keep this in mind reading §4's proposed workflow additions below: a roadmap-task-driven implementation command is a productivity tool for whoever chooses to use it, not a new required step in how this ecosystem ships changes.

## 1. What exists today

Five of the eight repos reviewed (`collector-gh`, `collector-ad`, `utilities`, `toolkit`, `generator-pdf`, plus `generate-release-notes`) carry a `.github/copilot-instructions.md` and a `.github/copilot-review-rules.md`. Three of those (`collector-gh`, `utilities`, `generator-pdf`) additionally carry a `.github/agents/` directory with five role-scoped agent definitions: `specification-master`, `senior-developer`, `sdet`, `reviewer`, `devops-engineer` — a small "review board" of GitHub Copilot custom agents, each with a one-line mission (Specification Master: "produces precise, testable specs and keeps repository docs as the contract source of truth"; SDET: "ensures automated test coverage, determinism, and fast feedback"; Reviewer: "guards correctness, performance, and contract stability; approves only when all gates pass"; etc.). `toolkit`, `collector-ad`, `generate-release-notes`, and `aquasec-scan-results` have copilot-instructions but no agent board. `generator-markdown` — consistent with everything else found about it in [Architecture](architecture.md) — has none of this.

Every one of these files is visibly built from **one shared portable template**: a "core rules, portable across repos" body plus a "Repo additions" section at the end for repo-specific facts, with rules phrased as `Must` / `Must not` / `Prefer` / `Avoid` constraints. This is a good design — it's exactly the right way to keep AI-agent guidance both consistent and locally accurate. The problem is execution, not design.

## 2. Findings: the template has drifted the same way the human-facing docs did

Diffing `copilot-instructions.md` pairwise across repos surfaces the same class of problem [Documentation & Style Synchronization](doc-style-sync.md) found in READMEs — except here the drift silently changes what an AI coding agent is instructed to do per repo, which is a step more consequential than a stale link.

### 2.1 At least two independent lineages, never reconciled

`collector-gh` and `generator-pdf`'s copies are close to each other but diverged (different phrasing throughout, e.g. collector-gh: *"Must keep sections in the order defined in this file"* vs generator-pdf: *"Must keep sections ordered exactly as listed in this file"* — same rule, reworded). `utilities`, meanwhile, has a **structurally different, more elaborate specification-master.agent.md** — with sections neither `collector-gh` nor `generator-pdf`'s copy has at all: "Verbosity levels" (brief/standard/detailed spec length tiers by change size), a "Minimum structure (portable)" checklist for what a spec document should contain, and a "Verification plan" deliverable alongside acceptance criteria. This is a materially better version of the same agent — and it exists in only one of the three repos that have this file, with no indication its improvements were ever considered for the other two.

### 2.2 The constraint-keyword dialect itself has drifted

The template's own house style — "write rules as constraints using Must / Must not / Prefer / Avoid" — is stated identically almost everywhere, but not *followed* identically. `collector-review-rules.md` in `collector-gh` uses `Do` / `Avoid` throughout ("Do use short headings…"); the same file in `toolkit` uses `Do:` / `Prefer:` / `Avoid:` with trailing colons; the same file in `generator-pdf` uses `Must` / `Prefer` / `Avoid` — three different keyword vocabularies for what is meant to be one shared review-behavior contract.

### 2.3 `toolkit`'s "Repo additions" section was never actually filled in for its monorepo reality

This is the most consequential single finding here. `toolkit/.github/copilot-instructions.md`'s "Repo additions" section — the one part of the file that's supposed to be repo-specific — reads:

```
Log prefix (if any): <none defined>
Commands (if different from defaults): <none>
```

But `toolkit`'s actual QA commands **are** different from the template's defaults: the template's canonical commands assume a single-package repo run from the root (`pylint $(git ls-files '*.py')`, `pytest tests/`), while `toolkit` is a monorepo where every quality-gate command must run *per package* via its `Makefile` (`make py-qa-core`, `make pylint-packages/core`, per `toolkit/DEVELOPER.md`). An AI agent following `toolkit`'s copilot-instructions literally today would run repo-root Pylint/pytest commands that don't match how `toolkit`'s own CI (`test.yml`, using the same Makefile targets) actually gates changes — the one repo shaped differently enough to need the "Repo additions" escape hatch is the one repo where it wasn't used.

### 2.4 `aquasec-scan-results` took a different, and arguably better, design path

Rather than the portable-template-plus-additions structure, `aquasec-scan-results/.github/copilot-instructions.md` (67 lines, the shortest of any reviewed) just documents the repo directly: entry point, module map (`src/modes/`, `src/services/`), the two operational modes, exact input env vars, exact outputs. No "Must keep this file portable" meta-rules at all. This is less reusable across repos but more immediately useful *in that repo* — a tension worth resolving deliberately (§4) rather than letting two philosophies coexist by accident.

## 3. Why this is worth fixing, not just noting

These files are read by an AI coding agent before every change in these repos (that's their entire purpose). Drift here doesn't produce a stale link a human might eventually notice and fix — it produces **silently different AI-agent behavior per repo**: different logging-format enforcement, different test-location conventions, different PR-body update conventions, different verbosity/spec-detail expectations. A contributor (human or AI) moving between two `living-doc-*` repos following "the same" instructions is actually following two quietly different rulebooks.

## 4. Proposed application: workflow patterns worth adopting

Beyond de-drifting what already exists, a few patterns worth introducing to this ecosystem's AI-assisted workflow — general practice for roadmap/spec-driven AI development, not specific to any one file reviewed above:

- **A single "implement this roadmap task" command**, parameterized by a task ID, that: reads the task's spec + acceptance criteria from a roadmap document, reads every file the task references *before* writing code, implements against the spec exactly, runs the full QA gate loop until clean, then **verifies each acceptance criterion against the actual code** (not "it compiles" — e.g. "returns typed X" is checked against the real return annotation, "sorted by Z descending" is checked against the real sort call), and only then writes a PR description and stops. This is a stronger, more automatable analog of what the `specification-master` + `senior-developer` + `sdet` + `reviewer` agent board here does as separate roles — collapsing the roadmap-task lifecycle into one driven command reduces the coordination overhead of manually invoking four agents in sequence.
- **A lighter, verify-only companion command** for right before opening a PR: re-check every acceptance criterion against code, run QA gates, run the review agent, and report a single PR-ready yes/no with a specific fix list if no. Distinct from the full implementation command above — useful when a human did most of the implementation and just wants the same rigor applied as a final gate.
- **A docs lifecycle rule tied to spec status**: when a spec document (this ecosystem's `SPEC.md` files, e.g. `collector-gh/SPEC.md`) has a section implemented, that section should be *removed* from the spec and its content *merged into* the live, "what actually exists" docs (`README.md`, mode-specific docs) — so the spec shrinks toward empty as the codebase matures instead of silently drifting out of sync with what's shipped. `collector-gh/SPEC.md` today has no such lifecycle: the `doc-source`/`ui-tests` modes are fully speced there, but nothing currently defines when/how that content graduates into `doc_issues/README.md`-style live documentation once built (see [Documentation & Style Synchronization](doc-style-sync.md) §3.3 for the related "no prospective spec process in toolkit" finding, which is the mirror-image gap).
- **A specialized test-authoring agent scoped to this ecosystem's actual mock surface**, analogous to `sdet.agent.md` but with a concrete, repo-specific cheat-table the generic agent doesn't currently have — e.g. "GitHub API calls → `responses` library, per `test_toolkit_fixtures.py` patterns already in `collector-gh/tests/`", "toolkit adapter version-compatibility → golden fixture pattern, see `tests/fixtures/collector_gh/v*.0.0/`". The generic `sdet.agent.md` states *principles* (determinism, coverage, fast feedback); a concrete mock-pattern table is what turns "ensure test coverage" into an agent that writes correct tests on the first try instead of guessing at mock targets.
- **Acceptance-criteria verification phrased as "read the code and confirm the literal claim,"** not "confirm tests pass" — e.g. "Cache hit skips the API call" is verified by confirming the check happens *before* the call in the actual function body, not by confirming a test with that name exists and is green. `reviewer.agent.md` here already gestures at this ("guards correctness... approves only when all gates pass") but doesn't spell out this level of literalness; making it explicit closes the gap between "tests pass" and "the acceptance criterion is actually true."

## 5. Tasks

**De-drift the existing template (do first — cheap, mechanical, high leverage)**
- [ ] Pick one canonical version of `copilot-instructions.md` — recommend starting from `utilities`' version of `specification-master.agent.md` specifically (it's the more complete of the two), and reconciling `copilot-instructions.md`/`copilot-review-rules.md` core-rule wording into one text, keyword dialect included (settle on `Must` / `Must not` / `Prefer` / `Avoid`, since it's the more common of the three dialects found and matches what the files' own "Structure" section already claims).
- [ ] Fill in `toolkit`'s "Repo additions" section with its real, monorepo-shaped commands (`make py-qa-<package>` per package, not repo-root `pylint`/`pytest`) — this is a correctness fix, not just a consistency one.
- [ ] Roll the reconciled template out to all 6 `living-doc-*` repos, including adding the full `.github/agents/` board to `toolkit` and `collector-ad` (currently missing it) and to `generator-markdown` once it has real code.
- [ ] Decide, deliberately, whether `aquasec-scan-results`'s "document the actual repo directly" style (§2.4) should replace the "portable core + Repo additions" style for the "Context"/architecture-facing sections specifically — the two aren't mutually exclusive: portable process rules (PR body management, output discipline, quality gates) plus a concrete, direct architecture summary (module map, entry points) in Repo additions, rather than the current generic Repo-additions placeholders many repos still carry.

**Add process the ecosystem doesn't have yet (§4)**
- [ ] Define a roadmap-task-driven implementation command for this ecosystem, once the root roadmap ([Roadmap](roadmap.md)) exists to drive it — read task spec + AC → implement → QA loop → verify AC against code → PR description. Natural home: alongside the existing agent board, invoked per roadmap task.
- [ ] Define the matching lighter "PR-ready" verification command.
- [ ] Add a docs-lifecycle rule to `collector-gh/SPEC.md` (and any future `toolkit` prospective-spec process, per [Documentation & Style Synchronization](doc-style-sync.md) §3.3): implemented sections move out of `SPEC.md` and into the relevant live `README.md`/mode docs, rather than accumulating indefinitely.
- [ ] Extend `sdet.agent.md` (in the four repos that have it, then the rest once §5's rollout lands) with a concrete, ecosystem-specific mock/fixture pattern table, sourced from what already exists in `tests/` across these repos rather than invented fresh.
- [ ] Tighten `reviewer.agent.md`'s acceptance-criteria language to require checking the literal claim in code, not just that a same-named test passes.
