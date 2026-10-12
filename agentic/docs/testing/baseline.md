# Eval baseline — iteration 1

The reference every later eval run is compared against. Produced by the protocol in
[eval-protocol.md](eval-protocol.md); the run's own evidence (hundreds of answer, timing and
grading files per iteration) is regenerable and deliberately **not** tracked — see
`agentic-evals-workspace/` in `.gitignore`.

## Validity

| | |
|---|---|
| Measured at | commit `51f78b5`, branch `feature/52-agentic-layer`, **before** the skill-text fixes below |
| Baseline arm (`old_skill`) | commit **`c6dbcc7`** — pre-canon-alignment, as the layer arrived from `agentic-toolkit` |
| Body evals | **234** (208 across the skills, 26 for the agent) × 2 arms = 468 runs |
| Trigger evals | 340 unique queries × 3 runs = 1020 invocations |
| Assertions graded | **1009** per arm |

> **These figures are superseded as a quality statement, and kept as a comparison point.** After
> this run, 12 SKILL.md files were corrected (unresolvable script paths, four false claims about
> their own scripts, the fabricated-provenance instructions) and the eval set itself was changed:
> 13 assertions corrected, 5 added as guards, 3 new eval cases, one duplicate trigger query
> removed — so the set is now **237 body evals / 340 trigger queries**. A re-run will therefore
> not be directly comparable eval-by-eval. What stays comparable is the method and the per-skill
> aggregate, which is why the table below records the arm, the models and the commit.

## Models

Recorded in every `timing.json`. A benchmark that does not name its model is not reusable.

| Role | Model |
|---|---|
| Body-eval execution, both arms | **Haiku** — `Agent`, `subagent_type: general-purpose`, `model: "haiku"`; never `fork`, which inherits the parent's model |
| Trigger-eval execution | **`claude-haiku-4-5-20251001`** |
| Grading and orchestration | **Opus 5** |

## Body evals

Pass rate = assertions passed / assertions graded. "gain" / "reg" count evals where the aligned
arm scored above / below the baseline arm.

| Target | Evals | Assertions | Aligned | Baseline | Δ | gain | reg |
|---|---|---|---|---|---|---|---|
| `bdd-maintain` | 10 | 35 | **1.00** | 0.97 | +0.03 | 1 | 0 |
| `data-cy-instrument` | 12 | 43 | **0.98** | 0.98 | +0.00 | 0 | 0 |
| `gherkin-living-doc-sync` | 16 | 69 | 0.87 | 0.88 | −0.01 | 1 | 2 |
| `gherkin-step` | 18 | 69 | 0.94 | 0.94 | +0.00 | 1 | 1 |
| `living-doc-create-feature` | 17 | 73 | 0.84 | 0.82 | +0.01 | 5 | 4 |
| `living-doc-create-functionality` | 19 | 85 | 0.87 | 0.92 | **−0.05** | 0 | 2 |
| `living-doc-create-user-story` | 23 | 96 | **0.93** | 0.80 | **+0.12** | 5 | 1 |
| `living-doc-gap-finder` | 18 | 77 | **0.90** | 0.74 | **+0.16** | 8 | 3 |
| `living-doc-impact-analysis` | 15 | 60 | 0.87 | 0.87 | +0.00 | 2 | 2 |
| `living-doc-pageobject-scan` | 17 | 85 | 0.91 | 0.86 | +0.05 | 2 | 0 |
| `living-doc-scenario-creator` | 25 | 106 | 0.84 | 0.76 | +0.08 | 6 | 1 |
| `living-doc-update` | 18 | 78 | 0.86 | 0.87 | −0.01 | 1 | 1 |
| `@living-doc-bdd-copilot` | 26 | 133 | 0.57 | 0.49 | +0.08 | 9 | 1 |
| **TOTAL** | **234** | **1009** | **0.848** | **0.806** | **+0.043** | **41** | **18** |

Two readings that matter more than the total:

- **The agent's 0.57 is environmental, not quality.** Nine of its 26 evals cannot discriminate
  without a live MCP Playwright server or project fixtures, and score near zero in *both* arms.
- **Correcting only the eval set would raise the aligned figure to 0.902** (+54 assertions, of
  which 37 are the agent's). That is honesty of measurement, not improvement; 99 assertions
  (9.8 %) were genuine failures.

## Trigger evals

- **Precision 1.00 on all 12 skills** — zero false fires across 170 negative queries. Every one
  of the 48 failures is a *miss*, never a mis-fire, so the skills do not hijack unrelated work.
- Overall 292/340 queries pass (0.859).
- **Recall collapses when a query names a concrete entity id:** 0.31 with an id (`US-007`,
  `FEAT-003`, `AC:US-010-01`) against 0.81 for a paraphrase — 0.53 vs 0.80 excluding the extreme
  case. `living-doc-scenario-creator` is 3/3 on paraphrases and **0/12** on `US-<id>` queries,
  although its description already lists the matching phrases. Naming the entity is how an author
  phrases a real request, so this is the layer's largest availability risk. Measured only; no
  `description:` was rewritten, because that invalidates this baseline.

## Reproducing

```bash
git worktree add /tmp/agentic-baseline c6dbcc7      # read-only control arm
python3 agentic/scripts/evals-inventory.py          # confirm counts before starting
```

Then follow [eval-protocol.md](eval-protocol.md) — in particular `--num-workers 1` for trigger
runs, one skill at a time, and nothing else in flight. Remove the worktree with
`git worktree remove /tmp/agentic-baseline` when finished.

Four trigger skills (`impact-analysis`, `pageobject-scan`, `scenario-creator`, `living-doc-update`)
were re-run while body evals were in flight in the same session. Their logs show no harness error
and the id/paraphrase split is too clean to be scheduling noise, but a quiet re-run is the one
figure here I would not yet treat as settled.
