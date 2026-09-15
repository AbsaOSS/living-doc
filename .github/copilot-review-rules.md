# Copilot Review Rules — living-doc

This file defines how Copilot reviews pull requests in this repository. It describes this
repo's own risk areas and review expectations; it is not shared with other repos. It is
referenced from `.github/agents/reviewer.agent.md` ("Review modes").

**House rules for this file**

- Must write every guidance bullet as a constraint led by one of `Must`, `Must not`, `Prefer`, `Avoid`.
- Must not put a colon after the leading keyword, and Must not use any other keyword style.
- Prefer short headings and bullet lists over prose.
- Prefer verifiable checks — a reviewer can point to the code and the impact.
- Avoid long audit reports unless they are explicitly requested.

## Review modes

- Must support two modes — Default review for standard PR risk, and Double-check review for elevated-risk PRs.

## Mode — Default review

- Must treat the change as a single PR with normal risk.
- Must prioritise in this order — correctness, security, tests, maintainability, style.

**Checks**

- Must flag logic bugs, missing edge cases, regressions, and unintended contract changes.
- Must flag unsafe input handling and insecure defaults in `tools/*.py`.
- Must check that `tools/test_examples_check.py` covers the success and failure path of any changed rule in `tools/examples_check.py`.
- Must check that a `docs/examples/**` fixture change carries a matching `docs/examples/_expected/**` regeneration when it changes what the real collector/toolkit mines (see `CONTRIBUTING.md` § "Regenerating the collector snapshots").
- Prefer calling out unnecessary complexity, duplication, and unclear naming or structure.
- Avoid style notes unless they reduce readability or break a repo convention.

**Response format**

- Must use short bullet points.
- Prefer referencing files and line ranges.
- Must group comments by severity — Blocker (must fix), Important (should fix), Nit (optional).
- Prefer actionable suggestions over rewrites.
- Must not rewrite the whole PR or produce a long report.

## Mode — Double-check review

- Must treat the change as higher risk — any change to `docs/guides/living-doc-header-types.md`, `docs/guides/living-doc-document-types.md`, or `docs/guides/living-doc-glossary.md` (the format contracts), any change to `tools/examples_check.py`'s rule set, any pin bump in `tools/collector-snapshot-pins.env`, and anything touching `docs/examples/**` or `docs/examples/_expected/**`.

**Additional focus**

- Prefer confirming that previous review comments were addressed correctly.
- Must re-check that a guide/glossary format change and the matching `docs/examples/**` update land in the same PR — this repo's stated sync obligation (`docs/examples/README.md` § "Sync obligation").
- Prefer looking for hidden side effects — cross-links broken by a doc move or rename, a new required header field not reflected in every existing example, and a `docs/examples/_expected/**` snapshot left stale after a pin bump.
- Prefer validating safe defaults — a malformed or missing `.project-profile.yaml` is reported, not silently skipped.
- Must confirm a `tools/collector-snapshot-pins.env` bump ships with regenerated `docs/examples/_expected/*.json` in the same PR, per `CONTRIBUTING.md`.

**Response format**

- Prefer commenting only where risk or impact is non-trivial.
- Avoid repeating minor style notes already covered by Default review.
- Prefer stating risk acceptance explicitly when something is left as-is — the risk, why it is acceptable, and the mitigation that exists.

## Commenting rules — all modes

- Must include for every comment — what the issue is (one line), why it matters (impact or risk), and how to fix it (a minimal actionable suggestion).
- Prefer linking to an existing pattern in the repo over introducing a new one.
- Must ask a targeted question instead of assuming when context is missing.

## Non-goals

- Must not request refactors unrelated to the PR's intent.
- Must not request a lint, type-check, or coverage-percentage gate — this repo has none configured.
- Avoid proposing architectural rewrites unless they are explicitly requested.

## Repo specifics

- Must treat these as high-risk areas — `tools/examples_check.py` (the corpus validation rules), `tools/regen-collector-snapshots.sh` / `tools/normalize_snapshot.py` (the real-collector snapshot pipeline), and the format contracts in `docs/guides/living-doc-header-types.md` / `docs/guides/living-doc-document-types.md` / `docs/guides/living-doc-glossary.md`.
- Must treat these as contract-sensitive — the `docs/examples/**` fixture corpus, the `docs/examples/_expected/**` snapshots, the pinned refs in `tools/collector-snapshot-pins.env`, and the cross-links `.github/workflows/link-check.yml` validates across `docs/**`.
- Must expect `tools/examples_check.py` and `tools/normalize_snapshot.py` to stay deterministic and offline — flag any LLM call or unpinned network request introduced into either.
- Must expect the only test suite to be `tools/test_examples_check.py`, run via `python -m pytest tools/test_examples_check.py -q`, exactly as `.github/workflows/examples-check.yml` runs it.
- Must expect PRs to carry a `#<issue>: Title` or `<issue> - Title` title, a branch name with a ticket number, and `## Overview` / `## Release Notes` / `## Related` sections — enforced by `.github/workflows/check-pr-requirements.yml` and `check_pr_release_notes.yml`, and documented in `CONTRIBUTING.md`.

## Audit — what this repo deliberately lacks relative to the fleet's code repos

- **`.github/copilot-instructions.md`** — not added by this PR. The code repos (`living-doc-toolkit`, `living-doc-collector-gh`, `living-doc-collector-ad`, `living-doc-generator-pdf`, `living-doc-utilities`) each carry one as a self-description of their package/module map. `living-doc` is documentation-plus-a-corpus, not a package tree; its self-description already lives in `README.md`, `CONTRIBUTING.md`, and `docs/examples/README.md`. Revisit if the repo grows a second Python surface.
- **`.claude/rules/docs-lifecycle.md`** — not carried over. That rule moves an implemented `SPEC.md` section into the live docs; this repo has no `SPEC.md` — its planning docs are local and gitignored (see `.gitignore`), never reaching a PR, so there is nothing for that rule to move.
- **Full `senior-developer` / `devops-engineer` remit** — scoped down, not dropped. The fleet versions assume a Python monorepo with `make qa`, per-package Pylint/mypy/coverage gates, and CLI/adapter contracts. This repo has none of that (`tools/requirements-examples-check.txt` states there is no other Python code); their `.github/agents/*.agent.md` "Repo specifics" sections reflect the smaller real surface (`tools/*.py`, the seven workflows) instead of inventing gates that don't exist here.
- **`.claude/settings.json`** — intentionally not touched by this PR; it carries local owner configuration.
