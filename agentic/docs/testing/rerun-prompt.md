# Re-run prompt — how to ask for an eval run

[eval-protocol.md](eval-protocol.md) says *how* a suite must be run; this page is *what to say* to
start one. It exists because the instructions a run needs are not all derivable from the repository:
three of them change every time and only the owner knows them.

Start a session as the runner, `claude --agent eval-runner`, copy the block below into it, fill the
three marked sections, and send it.

- **Orchestrator on Opus, body-eval subagents on Haiku.**
- Expect ~2 subagent runs per body eval and ~3 invocations per trigger query — for the current set,
  roughly 470 runs and ~1000 invocations.
- **Start early in a quota window.** The Opus grading pass is what gets rate-limited, and it comes
  last; a limit at that point strands the most expensive part of the run.

---

## Invocation modes

In a `claude --agent eval-runner` session:

| You type | What happens |
|---|---|
| A request to run the suite, naming no target | Full suite, every target. The agent reads this page and follows the prompt below. |
| `<skill> [<skill> …]` | **Partial run** over the named targets only. Same protocol, same arms, same models. |
| The filled-in prompt below | Full suite, with this run's ground facts supplied. Preferred for a baseline run. |

**A partial run must not rewrite [baseline.md](baseline.md).** The baseline is a statement about the
whole layer; a run that measured four targets cannot make it. A partial run writes its result as a
standalone report, names the targets it did *not* measure, and leaves `baseline.md` alone. Only a
full run replaces it.

---

## The prompt

````text
You are `eval-runner` (`.claude/agents/eval-runner.md`). Follow
`agentic/docs/testing/eval-protocol.md` exactly.

**Goal.** Produce a new initial baseline for the agentic layer, replacing
`agentic/docs/testing/baseline.md`. The existing baseline is a comparison point, not a
target to reproduce.

## Ground facts

- Baseline arm: the commit named in `baseline.md` § Validity. Recreate it read-only:
  `git worktree add /tmp/agentic-baseline <commit>`.
- Run `python3 agentic/scripts/evals-inventory.py` and compare against `baseline.md`.
  Expected counts and the reason they changed:
  <!-- FILL IN: e.g. "237 body / 347 trigger; +3 body evals in bdd-maintain,
       gherkin-living-doc-sync, living-doc-impact-analysis; one duplicate trigger query
       removed from living-doc-create-functionality; 7 id-bearing trigger queries added
       across the three living-doc-create-* skills" -->
  Confirm those exact numbers; stop only if they differ from what is written here.
- Treat the working tree as `with_skill`. Uncommitted SKILL.md / agent changes are the
  thing under test.
- An eval-by-eval comparison against the old baseline is invalid whenever assertions were
  corrected or added. Compare per-target aggregates and say where the assertion count moved.

## What to expect, so you do not misread it as a regression

<!-- FILL IN per run: each change, and which direction it moves the score. -->

Where a fix makes the honest answer score *lower* because an assertion still rewards
guessing, report it as a corrected behaviour and record the assertion as suspect — not as
a regression.

## Verify these specifically

<!-- FILL IN: the claims from the previous run that are measured but not yet confirmed. -->

## Hard stops

- No git writes beyond the baseline worktree and its removal.
- Never edit a skill, an agent, or an eval file. You measure; you do not fix.
- Never rewrite a `description:`.
- Do not run `run_loop.py`.
- Every finding cites `file:line` and is confirmed against the file before you report it.
  Graders are models and have been confidently wrong; two were, in the first baseline run.

## Operating rules learned from previous runs — not optional

1. **Assume you will be interrupted.** A session or rate limit mid-run is the normal case.
   Keep `<workspace>/PROGRESS.md` current after every target: what is run, what is graded,
   headline numbers, open findings. Anything held only in your context is lost.
2. **Graders write per-eval files as they go**, never batching at the end. A grader killed
   after writing its `grading.json` files is recoverable; one killed before writing them has
   produced nothing. Totals can always be recomputed from `grading.json` on disk.
3. **Runner usage figures come from the harness, not the runner.** A subagent cannot see its
   own token count and will answer `missing`. Take `subagent_tokens` / `duration_ms` from the
   harness usage block. Durations include queueing, so an outlier is wall-clock, not model
   time — say so rather than presenting it as a measurement.
4. **Pin each runner to exactly one output path, and say so twice.** A runner has written its
   answer into a mis-spelled sibling directory, leaving one arm silently empty. After each
   target assert `answers == evals x 2` before moving on.
5. **Stage every fixture outside the eval tree** and point the prompt at the copy. Tell every
   runner: do not read anything under any `evals/` directory.
6. **Trigger evals run alone**, `--num-workers 1`, one skill at a time, with no subagent or
   other model call in flight. Drive them from a single serial script that writes a `.done`
   marker per skill, so the phase survives an interruption and resumes where it stopped.
7. **Do not mix grader models across targets.** If the grading model becomes unavailable, wait
   for it, or state explicitly in the validity block which targets were graded by what.

## Deliverables

The protocol's § 6, then rewrite `agentic/docs/testing/baseline.md` as the new initial
baseline: validity block, models, per-target table, trigger table, one production-readiness
line per target, and what the suite still does not test. Keep raw evidence out of git
(`agentic-evals-workspace/` is gitignored). Leave everything uncommitted; the owner commits.

Finish by reporting what you ran, the headline figures with the models named, what you
verified, what you could not, and the working tree's state.
````

---

## Rolling the baseline forward

[baseline.md](baseline.md) serves two purposes at once: it is the control arm a run compares
against, and it is the record of what the skills currently score. Those stay compatible only if it
moves with the layer.

- **Update it when an improvement is confirmed and merged**, not while it is still a proposal. A
  run measures the working tree, so its numbers describe uncommitted work until the owner commits;
  the validity block must therefore name the state measured, not just a branch.
- **Then move the baseline arm to the merge commit.** The `old_skill` commit named in § Validity is
  the control for the *next* run. Leaving it pinned to an older ancestor turns the delta column from
  "did this change help?" into "how far have we come since then?", which the per-target table is not
  built to answer.
- A run that measures no improvement still updates the figures, if the eval set changed. The numbers
  must describe the current set, or the next count check fires a false alarm.

---

## Why the three blanks

They are the only inputs an agent cannot recover from the repository, and each one has cost a run:

- **Changed counts.** `evals-inventory.py` disagreeing with `baseline.md` is the protocol's signal to
  stop. When the eval set changed on purpose, that stop is a false alarm — but the agent cannot tell
  the two apart, so the owner states it.
- **Expected direction.** A fix that removes a false claim lowers the score wherever an assertion
  still rewards the claim. Unannounced, it reads as a regression and gets reported as one.
- **Unconfirmed claims.** A figure measured once under imperfect conditions is not settled. Naming
  them is what turns the next run into a verification rather than a repetition.
