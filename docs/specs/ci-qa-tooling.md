# Spec: CI Checks & QA Tooling

**Status:** Draft — 2026-08-25
**Scope reviewed:** all 6 `living-doc-*` repos, compared against [`AbsaOSS/generate-release-notes`](https://github.com/AbsaOSS/generate-release-notes) and [`AbsaOSS/aquasec-scan-results`](https://github.com/AbsaOSS/aquasec-scan-results) as the two most mature, established repos in the org's Python-Action portfolio.

## 1. Method

`.github/workflows/*.yml` were enumerated and diffed across all 8 repos, along with `.pylintrc`, `.pre-commit-config.yaml`, and `pyproject.toml` QA config. Workflow *content*, not just filenames, was read and compared — several repos have same-named workflows with materially different implementations.

## 2. Inventory: what exists where

| Workflow purpose | collector-gh | collector-ad | utilities | toolkit | generator-markdown | generator-pdf | **generate-release-notes** | **aquasec-scan-results** |
|---|---|---|---|---|---|---|---|---|
| Lint/format/type/test gate | `static_analysis_and_tests.yml` | `static_analysis_and_tests.yml` | `static_analysis_and_tests.yml` | `test.yml` (per-package via Makefile) | ❌ none | `test.yml` | `test.yml` | `check_python.yml` |
| Integration/example run | `integration_test.yml` | ❌ none | ❌ none | `integration.yml` | ❌ none | `example.yml` | ❌ none | ❌ none |
| PR release-notes presence check | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Release draft | ✅ | ✅ | ✅ (+ `release.yml` PyPI publish) | ✅ | `gh_release_draft.yml` (diff name) | ✅ | ✅ | ✅ |
| Dependabot auto-workflow | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `dependabot_auto.yml` (diff name) |
| **AquaSec Night Scan** | ❌ | ❌ | ❌ | ❌ | n/a (no code yet) | ❌ | n/a | ✅ (source repo) |
| `.pre-commit-config.yaml` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `.pylintrc` | ✅ | ✅ | ✅ | ❌ (per-package `pyproject.toml` instead) | ❌ | ✅ | ✅ | ✅ |

## 3. The AquaSec gap is the single biggest finding here

Every `living-doc-*` repo's original scaffold README (still literally present, unmodified, in `generator-markdown`) states: *"As one of the first tasks, please implement the AquaSec Night Scan... as a mandatory workflow."* Despite that, **all 6 reviewed repos lack it** (`generator-markdown` has no code yet to scan, so it's the one partial exception). `collector-gh`, `collector-ad`, `utilities`, `toolkit`, and `generator-pdf` all ship real Python code, real dependencies, and real CI — but none of them run the mandatory security scan the org template asked for on day one. `aquasec-scan-results` (the tool that *implements* the scan action itself) unsurprisingly has it. This root repo (`living-doc`) has it too as of this pass — see [Architecture](../introduction/architecture.md)'s note on the workflow added here — but that only covers this repo; it does nothing for the 5 satellite repos that actually run Python and are the ones with a real vulnerability surface.

## 4. `aquasec-scan-results/test.yml` is a materially better lint/test gate than the shared `static_analysis_and_tests.yml` template

Diffing the two side by side:

- **`aquasec-scan-results`** has a `detect` job (path-filters on `*.py`/`requirements.txt` changes, via `gh api` on PRs and `git diff` on push) that gates every other job with `if: needs.detect.outputs.python_changed == 'true'`, plus a `noop` job that runs — and passes — when nothing Python-related changed. This means a docs-only PR doesn't burn CI minutes on pylint/black/mypy/pytest, while a required-status-check branch-protection rule still gets a green check either way.
- **`aquasec-scan-results`** declares `concurrency: { group: static-python-check-${{ github.ref }}, cancel-in-progress: true }` — a superseded push/PR run gets cancelled automatically. None of the `living-doc-*` repos' equivalent workflow declares a `concurrency` block at all.
- **`aquasec-scan-results`** declares explicit `permissions: { contents: read, security-events: write }` at the workflow level (least-privilege, and `security-events: write` specifically enables SARIF/code-scanning uploads). The `living-doc-*` repos' `static_analysis_and_tests.yml`/`test.yml` declare no `permissions` block, which means they run with the repository's default token permissions — broader than necessary for a read-only lint/test job.
- **Pinned action SHAs differ between the two families**: `living-doc-collector-gh` pins `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1`; `aquasec-scan-results` pins `actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0` — a newer SHA. This is a small, mechanical drift but it means the "same" security-pinning discipline is stuck at different points in time across the org's own repos.

The actual QA *rules enforced* (pylint ≥9.5, Black --check, mypy, pytest --cov-fail-under=80) are identical in substance across every repo including the two reference ones — that part of the standard is solid and consistently applied. The gap is entirely in the workflow's operational hardening (concurrency, permissions, change-detection), not the quality bar itself.

## 5. Workflow naming is inconsistent for equivalent jobs

`static_analysis_and_tests.yml` (3 repos) vs. `test.yml` (`toolkit`, `generator-pdf`, and both reference repos) vs. `check_python.yml` (`aquasec-scan-results`, doing the same job under yet another name) name the same conceptual gate three different ways. Given `test.yml` is what both reference repos converge on, that's the stronger signal for a standard name — `static_analysis_and_tests.yml` is arguably more descriptive but is the minority pattern among the org's own most mature repos.

Similarly: `release_draft.yml` (5 repos) vs. `gh_release_draft.yml` (`generator-markdown` only) — trivial, but avoidable drift the moment a new repo is scaffolded from a slightly different template snapshot.

## 6. `.pre-commit-config.yaml` exists in exactly one repo

`generator-pdf` is the only `living-doc-*` repo with local pre-commit hooks configured — meaning it's the only repo where a contributor gets fast, local feedback (format/lint) before ever pushing, rather than discovering a Black/Pylint failure only after CI runs. Neither reference repo (`generate-release-notes`, `aquasec-scan-results`) has one either, so this isn't a "match the mature repos" gap — it's an opportunity `generator-pdf` already found and nothing has propagated it, including to the two repos held up as most mature.

## 7. `collector-ad` has no integration/example workflow at all

`collector-gh` (`integration_test.yml`), `toolkit` (`integration.yml`), and `generator-pdf` (`example.yml`) all have *some* workflow that exercises the action/service beyond unit tests. `collector-ad` has none — its only gates are static analysis and the PR/release bookkeeping workflows. Given `collector-ad` is the least-built-out collector ([Architecture](architecture.md) §2), this compounds: it has the least code, the least test coverage of real ADO interaction, and no CI signal at all for "does the action actually run end-to-end."

## 8. Tasks

**Security (highest priority — this is a stated mandatory control that's been skipped)**
- [ ] Add `aquasec-night-scan.yml` to `collector-gh`, `collector-ad`, `utilities`, `toolkit`, `generator-pdf` — copy the working config from `aquasec-scan-results` (which already has it correctly wired) rather than re-deriving it from the org template each time.
- [ ] Add it to `generator-markdown` once that repo has real code to scan (tracking it as a blocked/deferred task now avoids it being silently dropped again the way it was the first time).

**Harden the shared lint/test workflow, converging on the `aquasec-scan-results` pattern**
- [ ] Add a `permissions: { contents: read }` block (minimum) to every `static_analysis_and_tests.yml`/`test.yml` in the 6 `living-doc-*` repos.
- [ ] Add a `concurrency` group (`${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: true`) to the same workflows.
- [ ] Adopt the `detect` (path-filter) + `noop` pattern from `aquasec-scan-results/test.yml` in repos where docs-only PRs currently pay the full CI cost unnecessarily.
- [ ] Re-pin `actions/checkout` (and other actions) to one consistent, current SHA across all 8 repos — pick the newest verified pin (`aquasec-scan-results`'s) as the baseline and propagate it.

**Naming convergence**
- [ ] Standardize on `test.yml` as the lint/test gate filename (majority pattern among mature repos) — rename `static_analysis_and_tests.yml` → `test.yml` in `collector-gh`, `collector-ad`, `utilities`; rename `aquasec-scan-results/check_python.yml` → `test.yml` too, or fold this into a broader "same file, same name" template pass alongside [Documentation & Style Synchronization](doc-style-sync.md).
- [ ] Rename `generator-markdown`'s `gh_release_draft.yml` → `release_draft.yml` once/if that repo's workflows are otherwise rebuilt from the current template.
- [ ] Standardize `dependabot.yml` vs `dependabot_auto.yml` naming (`aquasec-scan-results` is the outlier here).

**Close specific coverage gaps**
- [ ] Add an integration/example workflow to `collector-ad`, modeled on `collector-gh/integration_test.yml`, once there's at least one ADO test fixture to run it against.
- [ ] Evaluate propagating `generator-pdf`'s `.pre-commit-config.yaml` to the other 5 repos — it's a net-new improvement over even the two reference repos, not just a consistency fix.

**Longer-term, tie-in with other specs**
- [ ] Add the schema-drift CI check from [Data Flows & Schemas](data-flows.md) §7 as a new job once the schema-ownership decision is made.
- [ ] Add the link-check gate from [Documentation & Style Synchronization](doc-style-sync.md) §5 to the same shared workflow set once this pass's naming/permissions convergence lands, so it's added once to the template rather than 6 times separately.
