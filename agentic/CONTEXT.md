# agentic

Parent: [../CONTEXT.md](../CONTEXT.md)

## Purpose

The optional AI authoring layer this repository ships: skills and the `living-doc-bdd-copilot` agent that help authors write entity headers and the BDD tests bound to them. Users install it into their own projects. Catalog and install: [README.md](README.md). Change rules, tests and PR checklist: [CONTRIBUTING.md](CONTRIBUTING.md).

Not here: this repository's own dev agents, which live in the root `.claude/agents/`. The test: an agent that is useless to someone who installed the layer and never opens this repository belongs in the root `.claude/agents/`.

## Layout

| Path | Holds |
|---|---|
| `.claude/skills/<name>/` | `SKILL.md`, `scripts/` with `test_*.py` beside each script, `evals/` (body `evals.json`, `trigger-eval.json`, fixtures) |
| `.claude/skills/living-doc-shared/` | `lib/` (shared Python), `references/` (canon copies, `agentic-formats.md`, JSON schemas) |
| `.github/agents/` | the shipped agent |
| `agents/evals/` | the agent's evals |
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

- The layer mirrors a project's root: each skill and the agent sit at the path they get in a user's project, so `.claude/` and `.github/` here are shipped content, not this repository's configuration (that is the root `.claude/`). The skills CLI must be pointed at `agentic/` (`…/tree/master/agentic`): from the repository root it stops at the root `.claude/skills/` and never sees the layer.
- Claude Code loads `.claude/skills/` here as nested project skills once a session reads or edits a file under `agentic/` (at startup when started in `agentic/`). They are the product under change, not tools for working on this repository, and an eval arm must not invoke them (the runner prompt from `scripts/evals/gen_runner_prompts.py` forbids the Skill tool).
- An eval baseline commit from before the move to `.claude/skills/` and `.github/agents/` has the old layout (`skills/`, `agents/`); `scripts/evals/gen_runner_prompts.py` reads whichever the baseline worktree holds, so the recorded baseline stays usable.
- `.claude/skills/living-doc-shared/references/living-doc-glossary.md` and `living-doc-bdd-schemas.md` are generated from `docs/reference/glossary.md` and `docs/reference/authoring-formats.md` by `scripts/sync-canon-copies.sh`. Never hand-edit them; CI fails when a committed copy differs. They exist because `npx skills add` copies only a skill's folder and `living-doc-shared`'s, so the canon in `docs/` isn't there.
- Nothing in CI runs an eval. Raw eval evidence (`agentic-evals-workspace/`) is gitignored; only the distilled `docs/testing/baseline.md` is tracked.
- Trigger evals need `--num-workers 1` and must run alone (eval-protocol § 2).
