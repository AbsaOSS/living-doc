# `agentic/scripts/evals/` — the deterministic half of an eval run

These scripts exist because parts of an eval run must not be done by a model: building directories,
copying figures, recomputing a delta and comparing against a baseline are mechanical, and a model
doing them by hand is slower, unrepeatable and occasionally wrong. Everything here is pure
bookkeeping — no judgement. Judgement stays with the grader, and the rules stay in
[../../docs/testing/eval-protocol.md](../../docs/testing/eval-protocol.md).

Each script also encodes one harness behaviour that silently produces wrong numbers, so the
workaround is applied by default rather than remembered:

| Script | What it does | The trap it removes |
|---|---|---|
| `scaffold.py` | Builds `iteration-N/<target>/eval-<id>-<slug>/{with_skill,old_skill}/run-1/outputs/` and writes `eval_metadata.json` | Maps the eval files' `expectations` to the `assertions` key the harness reads, without editing the eval file |
| `record_timing.py` | Writes `timing.json`, model included | Figures arrive at notification time and are unrecoverable later; a lost run is marked as missing data, not as zero |
| `normalize_grading.py` | Derives `summary` from `expectations[]` | `aggregate_benchmark.py` reads `grading["summary"]`, so a top-level `pass_rate` alone yields 0.0 % everywhere |
| `fix_benchmark.py` | Reorders configurations, recomputes the delta, stamps the models and the baseline commit | `sorted(iterdir())` puts `old_skill` first, inverting `run_summary.delta` |
| `compare_baseline.py` | Diffs a finished iteration against `docs/testing/baseline.md` | Makes "did this change help?" a command instead of an impression |

All of them take paths as arguments and write only inside the workspace. None of them touches a
skill, an eval file or git.

## Usage

```bash
W=agentic-evals-workspace                       # gitignored; evidence is regenerable
python3 agentic/scripts/evals/scaffold.py <target> $W 1
# … run both arms, then per finished run:
python3 agentic/scripts/evals/record_timing.py $W/iteration-1/<target> haiku eval-1:with_skill:45822:24317
# … after grading:
python3 agentic/scripts/evals/normalize_grading.py $W/iteration-1
python3 agentic/scripts/evals/fix_benchmark.py $W/iteration-1/<target> haiku opus
python3 agentic/scripts/evals/compare_baseline.py $W/iteration-1
```

`scaffold.py` takes a fourth argument to point at an eval file elsewhere — the agent's set lives at
`agentic/agents/evals/<agent>/evals.json`, not under `agentic/skills/`.
