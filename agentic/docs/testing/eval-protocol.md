# Eval protocol — how to run a suite so the numbers mean something

[skill-testing.md](skill-testing.md) and [agent-testing.md](agent-testing.md) describe *what* an
eval is. This page describes *how to run a whole suite* so its result can be trusted, compared and
reproduced. It is deliberately repo-agnostic: nothing below is specific to living-doc beyond the
examples, so a sibling repository with its own agents, skills and commands should link to this page
rather than fork it.

Every rule here was paid for by a wrong number in the iteration-1 run that produced
[baseline.md](baseline.md). They are not style preferences.

---

## 1. Measurement setup

**Two arms, one variable.** Compare the current skill (`with_skill`) against a baseline arm
(`old_skill`) and change nothing else. Pin the baseline to a **commit**, checked out as a
read-only worktree:

```bash
git worktree add /tmp/<layer>-baseline <commit>
```

Treat that worktree as read-only — it is the control arm. Never edit a file inside it.

**Fix the executor model and record it.** Run both arms on the same model, and write it into every
`timing.json`. A benchmark that does not name the model it measured cannot be compared to anything
later. When spawning runs as subagents, pass the model explicitly and **never use a `fork`-style
subagent**, which inherits the parent's model and silently measures something stronger than you
think.

**Grade with a stronger model than you execute with**, and keep grading separate from execution.
The grader's job is judgement; the executor's is producing an answer.

**Capture timing at notification time.** Token and duration figures arrive when a run reports and
are not recoverable afterwards. If a run is killed (a rate limit, a timeout) after writing its
answer but before reporting, write the zeros **with a `note` saying the figures are unrecoverable**
— a zero that looks like a measurement is worse than an admitted gap.

**Finish one target before starting the next.** Runs, grading and benchmark for one skill, then the
next. A failure half way through then costs one skill, not the suite.

---

## 2. Harness behaviours that silently produce wrong numbers

These are properties of the `skill-creator` tooling, found by measuring. Each produces
plausible-looking output that means nothing.

**Trigger runs need `--num-workers 1`.** `run_eval.py` writes one command file per in-flight run,
all carrying the same `description`, and detects a trigger by finding *its own* generated name in
the `Skill` call. At the default 10 workers, dozens of indistinguishable files exist at once, the
model picks a sibling's, and genuine triggers are scored as misses. Measured on the same two
queries: **0/2 at 10 workers, 2/2 at 1 worker.** Run one skill at a time too, so no other
description competes — and run nothing else in the session while trigger evals are in flight.

**`aggregate_benchmark.py` can invert the delta.** It discovers configuration directories with
`sorted(iterdir())`, so a baseline named `old_skill` sorts before `with_skill` and
`run_summary.delta` comes out backwards. Recompute it as `with_skill − old_skill`.

**It reads the pass rate from `grading["summary"]`**, not a top-level `pass_rate`. A grader that
writes only the latter yields 0.0 % for every configuration. Derive `summary` from the
`expectations` array so the two can never disagree.

**`grading.json` field names are load-bearing:** `expectations[]` with `text`, `passed`,
`evidence`. Anything else renders blank in the viewer.

`agentic/scripts/evals/` carries these as code so they are not re-derived by hand.

---

## 3. Grading discipline

**Grade against the assertion as written** — do not credit an answer for something it did not say.

**"The assertion is wrong" is a first-class outcome.** Record it, with the reason, as a finding for
the owner. In iteration 1, 54 of 153 aligned-arm assertion failures were the eval's fault, not the
skill's.

**An aligned arm losing to the baseline is a signal to read the assertion, not evidence of a
regression.** This one rule saves the most time. Two skills scored *below* baseline purely because
their assertions rewarded guessing and penalised an honest refusal — one required an error code the
prompt never supplied, another was passable only by inventing an ID. Before accepting any
regression as real, read the assertion that produced it.

**Verify a reported finding against the file before believing it.** A grader is a model and will
sometimes be confidently wrong. In iteration 1 two grader claims were false — a legitimate code
reported as forbidden, and a skill section reported as missing that exists. Both would have reached
the owner as fabricated defects. Require every finding to cite `file:line`, so checking it is cheap,
and check the ones you intend to act on.

**Anything that passed but looks unreliable belongs in the report.** An assertion satisfied by a
schema-shaped example from a run that did no work is a gap, not a pass.

---

## 4. Validity rules for the eval set

**Runners must not read the eval tree.** A roaming run will find a sibling eval's fixture and use
it as input — it happened, and the answer silently contained another case's data. Tell every runner
not to read anything under `evals/`, and stage fixtures **outside** the eval tree so a prompt never
has to name a path inside it.

**Label evals that need a live service or a fixture.** An eval that hard-stops identically in both
arms measures the environment, not the skill. Nine of 26 agent evals were in this state and
consumed a third of its assertions. A non-discriminating eval is not coverage, and a clean sheet
made of them is not a result.

**One run per arm means no variance.** Do not read a ±0.01 difference as signal; record
`runs_per_configuration` honestly.

**Test the mechanical facts mechanically.** Whether a documented command resolves, or a documented
flag exists, is a fact about the text — not about a model's answer. It belongs in a script test
(see `agentic/skills/shared/test_skill_doc_commands.py`), where it is deterministic and cannot
hallucinate. Reserve eval assertions for behaviour.

**Every fix gets a guard.** When a defect is corrected, add the assertion or test that would have
caught it, in the same change. An uncovered fix regresses silently.

---

## 5. Scope rules

**Trigger evals measure; they do not authorise a rewrite.** Changing a `description:` invalidates
the baseline it is compared against, so the change has to be re-measured, not guessed. Report the
recall figure and let the owner decide.

**The regression gate is separate from the evals.** Script tests on every supported interpreter,
generated-copy checks, format validation and link checks are pass/fail infrastructure. Run the gate
after any edit to the layer. **Never make a gate pass by committing a regenerated artifact** — a
non-empty diff in a generated file means its source changed, which is a finding, not a chore.

**"What this suite does not test" is a required deliverable.** A gap in the eval set is as much a
finding as a failing case, and it is the part no score can show. Report it every time.

---

## 6. What a run must deliver

1. One benchmark per target, naming the executor model and the baseline commit.
2. The trigger table: rate, precision, recall, and every failing query with its reason.
3. Each fix, tied to the eval that drove it.
4. Each eval judged wrong rather than the skill, with the reason.
5. The regression-gate output.
6. Anything still failing, and why.
7. **One production-readiness line per target** — can it be relied on, and if not, what is the weak
   spot. This is the thing being bought with the run.
8. The gaps in the eval set itself.

Distil the result into [baseline.md](baseline.md) and keep the raw evidence out of version control;
it is regenerable and large.
