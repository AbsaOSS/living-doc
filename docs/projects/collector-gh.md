# living-doc-collector-gh

**Repo:** [github.com/AbsaOSS/living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh)
**Role:** Collector
**Type:** GitHub Action

## Purpose

Mines a GitHub repository for living-documentation data and emits it as machine-readable JSON for the rest of the Living Documentation pipeline. It is not limited to issues: depending on which modes are enabled it also mines living-doc header blocks from repository source code and Gherkin UI-test scenarios from `.feature` files.

## Supported modes

The action runs one or more independent **mining regimes** ("modes"). Each is switched on by its own boolean input, takes its own repository list, and writes its own JSON file under the action's `output-path`, so a single workflow step can collect several kinds of data in one pass.

| Mode | Enable with | Mines | Output file |
|---|---|---|---|
| **Documentation Issues** | `doc-issues` | GitHub issues used as standalone documentation tickets — title, body, labels, state, timestamps, and audit events (created / closed / commented by whom); optionally enriched with linked **GitHub Projects** state | `doc-issues/doc-issues.json` |
| **Documentation Source** | `doc-source` | Living-doc header blocks in checked-out repository source — User Story and Functionality blocks in `.feature` files, Feature blocks in TypeScript PageObject files — with acceptance criteria, business value, ownership, and parent links | `doc-source/doc-source.json` |
| **UI Tests** | `ui-tests` | Gherkin scenario blocks from `.feature` files, producing a test catalog keyed by `@US_ID` / `@AC` tags — scenario name, tags, steps, and source location | `ui-tests/ui-tests.json` |

The [project README](https://github.com/AbsaOSS/living-doc-collector-gh) tracks each mode's maturity with a status badge. `doc-issues` is the most developed and the only mode with a stable published schema (`doc-issues-v1.0.0`) that [living-doc-toolkit](toolkit.md) and [generator-pdf](generator-pdf.md) consume today; `doc-source` and `ui-tests` are newer and feed toolkit's coverage-matrix work (see [Roadmap](../specs/roadmap.md) Phase 2).

All three modes mine content authored in the shared format described in [Living Doc Header Types](../guides/living-doc-header-types.md) and [Living Doc Glossary](../guides/living-doc-glossary.md).

## Inputs / Outputs

- **Inputs:**
  - `GITHUB-TOKEN` (required) — token with read access to every repository and project the enabled modes touch.
  - Mode toggles: `doc-issues`, `doc-source`, `ui-tests` — enable at least one.
  - Per-mode repository lists: `doc-issues-repositories`, `doc-source-repositories`, `ui-tests-repositories` — a JSON array of objects carrying `organization-name`, `repository-name`, and mode-specific path/filter fields (e.g. `us-paths` / `func-paths` / `pages-paths` for `doc-source`, `projects-title-filter` for `doc-issues`).
  - Options: `doc-issues-project-state-mining` (pull GitHub Projects state into `doc-issues`), `verbose-logging`.
- **Output:** `output-path` — the directory containing one `<mode>/<mode>.json` file per enabled mode. Each file has a `metadata` provenance block (schema version, generator, source repos, workflow context) plus the mined entities.

For the exact, current list of action inputs/outputs and each mode's configuration, see the [project README](https://github.com/AbsaOSS/living-doc-collector-gh) and the per-mode docs it links.

## Where it fits

First collection stage of the pipeline — feeds [living-doc-toolkit](toolkit.md) or a generator directly. Upstream of it, [agentic-toolkit](agentic-toolkit.md)'s `living-doc-bdd-copilot` agent is what authors the User Story / Feature / Functionality entities — as issue bodies or as `.feature` / PageObject files — that this collector's modes mine. See [Architecture](../introduction/architecture.md) for where this collector sits in the pipeline.

## Used in

- [Collecting from GitHub](../guides/github-collection.md)
- [Living Doc Glossary](../guides/living-doc-glossary.md)
- [Living Doc Header Types](../guides/living-doc-header-types.md)
- [GitHub Issues → Markdown](../tutorials/gh-issues-to-markdown.md)
- [User Stories → PDF](../tutorials/user-stories-to-pdf.md)
