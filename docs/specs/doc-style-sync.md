# Spec: Documentation & Style Synchronization

**Status:** Draft — 2026-08-25
**Scope reviewed:** `living-doc-collector-gh`, `living-doc-collector-ad`, `living-doc-utilities`, `living-doc-toolkit`, `living-doc-generator-markdown`, `living-doc-generator-pdf`

## 1. Method

Every repo was cloned locally and its `README.md`, `CONTRIBUTING.md`, `DEVELOPER.md`, and (where present) `SPEC.md` were read in full, alongside `pyproject.toml` / `requirements.txt` for version claims. Findings below cite the specific file and, where useful, the specific line so they're directly actionable.

## 2. What's already consistent

This is worth stating explicitly so remediation doesn't undo it: four of the six repos (`collector-gh`, `collector-ad`, `utilities`, and to a lesser extent `generator-pdf`) already share one README template — `Motivation → Usage → Action Configuration → Action Outputs → Developer Guide → Contribution Guidelines → License → Contact`— and one `DEVELOPER.md` template — `Project Setup → Run Pylint/Black/mypy → Run Unit Test → Code Coverage → Releasing`, with matching wording (pylint ≥9.5, coverage ≥80%, Black line length 120). `CONTRIBUTING.md` is byte-for-byte identical across `collector-gh`, `collector-ad`, and `utilities`. This is a strong, reusable baseline — the fix here is to converge the outliers onto it and stop future drift, not to invent a new template.

## 3. Findings

### 3.1 Broken / stale cross-repo links

| Repo | File | Issue |
|---|---|---|
| `living-doc-generator-markdown` | `CONTRIBUTING.md` (all Issues links) | Points to `github.com/AbsaOSS/generate-release-notes/issues` — this is boilerplate copied from the org template and never rebound to this repo. Same defect this root repo's own placeholder `README.md` had before this pass (see [Architecture](architecture.md)). |

### 3.2 `living-doc-generator-markdown` is not a documented project yet

Its `README.md` is 5 lines of unmodified org template text (the "implement AquaSec Night Scan" placeholder). It has no `DEVELOPER.md`, no `SPEC.md`, no `action.yml`, no source code — it is scaffolding only. Every other repo in the ecosystem has moved past this stage. This isn't a style-sync defect to *fix* so much as a fact the rest of this spec (and the architecture/data-flow specs) needs to account for: any doc-sync work here is templating the repo for a first author, not correcting drift.

### 3.3 `living-doc-toolkit` diverges from the shared template — partly by necessity, partly by gap

- **No `CONTRIBUTING.md` at all** (confirmed absent at repo root). Every other repo has one, and it's identical across three of them. This is a plain gap, not a design choice — nothing about the monorepo structure justifies dropping it.
- **`README.md` and `DEVELOPER.md` follow a different, arguably better structure** (`Understand / Use / Maintain` doc taxonomy, a `Services` section per CLI command, CI badges at the top) than the five-repo template. This is justified — it's a monorepo hosting multiple services, and the flat one-README template doesn't fit — but it means a reader moving between `toolkit` and the other repos hits two different documentation philosophies with no signposting that the switch is intentional.
- **No `SPEC.md`**, unlike `collector-gh` which uses one to spec upcoming modes (`doc-source`, `ui-tests`) before implementation. `toolkit`'s own `docs/architecture.md` and `docs/contracts.md` partially fill this role but are retrospective ("what the system is") rather than prospective ("what we're about to build") — there's no place in `toolkit` to spec a new service the way `collector-gh/SPEC.md` specs a new mode.

### 3.5 `living-doc-collector-ad` advertises unbuilt modes as "todo" inline, `living-doc-collector-gh` does the same for "in development" — inconsistent signaling convention

Both READMEs use shield.io status badges next to mode links (`![Status](...status-in%20development...)`, `...status-todo...`), which is good practice. But `collector-gh` lists 3 modes, all "in development" (and one, `doc-source`, is fully speced in `SPEC.md` while not yet in `main.py`/`action.yml` — i.e., "in development" spans two very different states: fully speced-but-unwired vs partially-coded). `collector-ad` lists 5 modes with only `work-items` implemented and the other 4 (`boards`, `pipelines`, `test_plans`, `release_notes`) marked "todo" — but none of those four have a corresponding directory or README file to link to (only `work_items/README.md` exists on disk). The badge convention communicates state; the underlying repo structure doesn't yet support the "todo" modes even as stubs, so the link targets in the README (`boards/README.md`, `pipelines/README.md`, etc.) are dead links today.

### 3.6 Two different "why this action exists" motivations, worded almost identically but drifting

`collector-gh` and `collector-ad` each open with a near-identical "Motivation" paragraph ("Addresses the need for continuously updated documentation accessible to all team members and stakeholders..."). This is good — it's a shared narrative. But `generator-pdf`'s README replaces this entirely with a different framing ("A source-agnostic GitHub Action that renders **any** structured JSON into a professional PDF...") and drops the "Motivation" section/heading altogether in favor of "Overview". Given `generator-pdf` is explicitly the newest and most deliberately-designed of the actions (see [Architecture](architecture.md)), this may be an intentional, improved template rather than drift — worth a decision, not an automatic revert.

### 3.7 `README.md` "Developer Guide" pointer style is inconsistent

Repos following the shared template put a one-line `## Developer Guide` section with a link to `DEVELOPER.md` in a stable position (after Action Outputs, before How-to/Contribution). `generator-pdf`'s README has no such section at all — `DEVELOPER.md` exists but nothing in `README.md` points to it.

## 4. Target state

1. One canonical **action-repo template** (README structure, CONTRIBUTING.md verbatim, DEVELOPER.md structure) — already ~90% real today across 4 repos; formalize it as a template the org scaffolds new repos from, so `living-doc-generator-markdown` doesn't get built against stale boilerplate.
2. One canonical **monorepo template** for `toolkit`-shaped repos (multiple services/packages) — document that `toolkit`'s `Understand/Use/Maintain` structure is the intended pattern for this repo shape, not a deviation, and give it its own root `CONTRIBUTING.md`.
3. A lightweight **link-check gate** (see [CI Checks & QA Tooling](ci-qa-tooling.md)) so a repo rename never again leaves stale cross-repo links live for an unknown period.
4. A single **stated Python version policy** (pick 3.14, since it's what CI actually enforces almost everywhere) that every README states identically.

## 5. Tasks

- [ ] Fix `living-doc-generator-markdown/CONTRIBUTING.md`: repoint Issues links from `generate-release-notes` to `living-doc-generator-markdown`.
- [ ] Add `CONTRIBUTING.md` to `living-doc-toolkit` (adapt from the shared 36-line template; add a note on monorepo-specific PR scope, e.g. "PRs should touch one package where possible").
- [ ] Reconcile the Python version claim: standardize on 3.14 in every README (`collector-gh`, `collector-ad` already correct); confirm `utilities`' `>=3.12` `pyproject.toml` constraint is intentionally looser than the action repos, or tighten it to match.
- [ ] Either build out `collector-ad/boards`, `pipelines`, `test_plans`, `release_notes` stub directories with README placeholders, or remove/soften the "todo" badge links in `collector-ad/README.md` until a directory exists to link to.
- [ ] Decide and document whether `generator-pdf`'s README structure (Overview-first, no Motivation heading) is the new template direction for all action repos, or should be reverted to match the shared template — then apply the decision everywhere, including adding the missing `## Developer Guide` pointer to `generator-pdf/README.md`.
- [ ] Write (or adapt from `toolkit/docs/architecture.md` + `contracts.md`) a prospective `SPEC.md`-style process for `toolkit`, so new services get speced before being built the way `collector-gh/SPEC.md` specs new collector modes.
- [ ] Once `living-doc-generator-markdown` gets its first real implementation, scaffold it directly from the canonical template in task 1 rather than the stale org default it currently carries.
- [ ] Add a CI link-check workflow (cross-reference with [CI Checks & QA Tooling](ci-qa-tooling.md) task list) to catch the class of defect in 3.1 automatically going forward.
