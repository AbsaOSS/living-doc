# agentic

Parent: [../CONTEXT.md](../CONTEXT.md)

## Purpose

The optional AI authoring layer this repository ships: skills and the `living-doc-bdd-copilot` agent that help authors write entity headers and the BDD tests bound to them. Users install it into their own projects. Catalog and install: [README.md](README.md). Change rules, tests and PR checklist: [CONTRIBUTING.md](CONTRIBUTING.md).

Not here: this repository's own dev agents, which live in `.claude/agents/`. The test: an agent that is useless to someone who installed the layer and never opens this repository belongs in `.claude/agents/`.

## Layout

| Path | Holds |
|---|---|
| `skills/<name>/` | `SKILL.md`, `scripts/` with `test_*.py` beside each script, `evals/` (body `evals.json`, `trigger-eval.json`, fixtures) |
| `skills/shared/` | `lib/` (shared Python), `references/` (canon copies, `agentic-formats.md`, JSON schemas) |
| `agents/` | the shipped agent and its evals |
| `docs/guides/` | one guide per skill and agent |
| `docs/testing/` | eval protocol, recorded baseline, re-run prompt |
| `scripts/` | `sync-canon-copies.sh`, `evals-inventory.py`, `evals/` (the deterministic half of an eval run) |

## Conventions

- `test_*.py` files are standalone scripts with `__test__ = False`: run each with `python`, as CI does. A bare `pytest` collects none and passes.
- Scripts must run on Python 3.10 (the `living-doc-utilities` floor) and 3.14. Skill format validation needs 3.11+.
- Skills write the release canon: one dash in a structural position, the four AC states with `(planned)` for backlog, authored status on User Stories and Functionalities only, no Feature status, no `descoped` or `future_release`.
- A failing eval never justifies loosening the canon: fix the eval case.
- Every change to the layer gets an eval run scoped to what changed, compared with [docs/testing/baseline.md](docs/testing/baseline.md). Scope table: [CONTRIBUTING.md § How much to re-test](CONTRIBUTING.md#how-much-to-re-test-after-a-change).
- Eval runs follow [docs/testing/eval-protocol.md](docs/testing/eval-protocol.md), started with [docs/testing/rerun-prompt.md](docs/testing/rerun-prompt.md) and run by the `eval-runner` agent (`.claude/agents/eval-runner.md`).

## Invariants and gotchas

- `skills/shared/references/living-doc-glossary.md` and `living-doc-bdd-schemas.md` are generated from `docs/guides/` by `scripts/sync-canon-copies.sh`. Never hand-edit them; CI fails when a committed copy differs. They exist because `npx skills add` copies only a skill's folder and `shared`'s, so the canon in `docs/` isn't there.
- Nothing in CI runs an eval. Raw eval evidence (`agentic-evals-workspace/`) is gitignored; only the distilled `docs/testing/baseline.md` is tracked.
- Trigger evals need `--num-workers 1` and must run alone (eval-protocol § 2).
