# NEXT_STEPS — iteration-2 eval run, handoff

> **Temporary. Delete before merge.** Written 2026-10-12 22:35. Carries an in-progress eval run
> across machines. Everything normative lives in
> [`agentic/docs/testing/`](agentic/docs/testing/eval-protocol.md); nothing here is canon.

## 1. Read first — the evidence does not travel with a commit

`agentic-evals-workspace/` is gitignored (`.gitignore:14`) and holds all 474 answer files, 8
targets' `grading.json`, every `timing.json`, and all 12 finished trigger JSON files. **Pulling on
another machine gets you none of it.**

```bash
# 810 KB, enough to finish the run elsewhere
tar czf agentic-evals-iter2.tgz \
    --exclude='prompt.txt' --exclude='grader-prompt.txt' \
    -C agentic-evals-workspace iteration-2 trigger-evals-2 staging PROGRESS.md
```

Prompts are excluded because they hold absolute macOS paths; regenerate them with
`gen_runner_prompts.py` / `gen_grader_prompts.py` (edit the repo root at the top of each).

Without the archive, finishing costs **204 body runs** (the 5 ungraded targets × 2 arms) plus a
re-run of any trigger set you want to re-check. `timing.json` figures are **not recoverable** at
all — they exist only at the moment a run reports.

| Phase | State |
|---|---|
| Body evals | **Complete** — 474/474 runs, all timings recorded |
| Trigger evals | **Complete** — 347/347 queries, all 12 skills |
| Grading | **8 of 13** targets |
| Benchmark / gate / `baseline.md` | **Not started** |

Baseline arm: worktree at `/tmp/agentic-baseline`, commit `c6dbcc7`. Recreate with
`git worktree add /tmp/agentic-baseline c6dbcc7`; remove with `git worktree remove` when done.

Models used: body execution **Haiku**, both arms · grading **Opus 5** · triggers
**`claude-haiku-4-5-20251001`**.

---

## 2. What remains, in order

### 2.0 Prompt for the finishing agent

Paste this into a fresh session. Run the orchestrator on **Opus**, subagents on **Haiku**.

````text
Use `@eval-runner` (`.github/agents/eval-runner.agent.md`) and follow
`agentic/docs/testing/eval-protocol.md`. Read `NEXT_STEPS.md` first — it is the handoff
for a run that is partly done. Do not restart work it records as complete.

Already done, do not repeat: all 474 body-eval runs (237 evals x 2 arms, timings
recorded) and all 347 trigger queries across 12 skills. Eight targets are graded.

Your job, in this order:

1. GRADE the five outstanding targets: living-doc-impact-analysis,
   living-doc-pageobject-scan, living-doc-scenario-creator, living-doc-update,
   living-doc-bdd-copilot. Use the pre-generated
   `agentic-evals-workspace/iteration-2/<target>/grader-prompt.txt`. One Opus subagent
   per target, staggered three-then-two. Graders MUST write grading.json per eval as
   they go. Do not mix grader models — the other eight were graded by Opus 5.
   For living-doc-bdd-copilot specifically, confirm whether evals 2, 4, 5, 7, 14, 16,
   18, 23, 25 still hard-stop identically in both arms, and report them as an eval-set
   gap rather than agent quality.

2. RE-RUN the living-doc-create-functionality trigger set alone (delete its .done
   marker). This is the run's one unresolved anomaly — see NEXT_STEPS.md § 5.4. Say
   whether 0.59 reproduces.

3. BENCHMARK: normalize_grading.py, then aggregate_benchmark per target, then
   fix_benchmark.py <target> haiku opus c6dbcc7, then compare_baseline.py.

4. REGRESSION GATE — read NEXT_STEPS.md § 3 first. A bare `pytest` reports success
   while collecting nothing. Run all three CI checks, on Python 3.10 AND 3.14.

5. REWRITE `agentic/docs/testing/baseline.md` as the new initial baseline: validity
   block naming the state measured, models, per-target table, trigger table, one
   production-readiness line per target, and what the suite still does not test.

6. Remove the baseline worktree and delete NEXT_STEPS.md.

HARD STOPS: no git writes beyond the baseline worktree; never edit a skill, an agent or
an eval file; never rewrite a `description:`; every finding cites file:line and is
confirmed against the file before you report it.

NOTE ON SCOPE: NEXT_STEPS.md § 9 lists ~50 skill and eval defects. Those are for the
owner to fix, not you — you measure. Re-measure only after the owner has fixed them.
````

### 2.0b Fixing pass — for the owner, a separate session

The fix work in § 9 must **not** run in the same session as the measuring work; the protocol
forbids the measurer fixing what it measures. Suggested order:

1. **`living-doc-create-functionality` `SKILL.md:148-150`** — the one change that unblocks the
   merge gate (body eval 10).
2. **The two CONFIRMED `gherkin-step` defects** (`SKILL.md:322/327`, `:278/283/343/351`) — the
   skill contradicts its own stated rules.
3. **The fabrication instructions** — `data-cy-instrument SKILL.md:89/91`,
   `gherkin-living-doc-sync SKILL.md:151-154`, and generalising the
   `living-doc-create-feature SKILL.md:123-125` honesty guard beyond `next_id.py`.
4. **The contradictory assertion pairs** — `create-feature evals.json:200`/`:205`,
   `create-functionality evals.json:176`/`:182`. These cannot both pass; one must change.
5. Everything else in § 9, lowest risk last.

**Every fix gets a guard** (protocol § 4): add the assertion or script test that would have caught
it, in the same change. An uncovered fix regresses silently.

Then re-measure — a **partial run** over the touched targets is enough to check the gate
(`@eval-runner <skill> …`), but only a **full run** may rewrite `baseline.md`.

### 2.1 Grade the five outstanding targets

`living-doc-impact-analysis`, `living-doc-pageobject-scan`, `living-doc-scenario-creator`,
`living-doc-update`, `living-doc-bdd-copilot`.

Each prompt is pre-generated at
`agentic-evals-workspace/iteration-2/<target>/grader-prompt.txt`. Spawn **one Opus subagent per
target** pointed at that file. All answers are present (32/34/50/36/52) and no partial grading
needs clearing.

- **Do not mix grader models.** The other eight were graded by Opus 5.
- **Stagger them** — an Opus session limit killed two graders during this run. Three, then two.
- **Insist graders write `grading.json` per eval as they go.** `gap-finder` survived being killed
  because it had already written its files; `pageobject-scan` had not and lost everything.
- For `living-doc-bdd-copilot`, ask specifically about evals **2, 4, 5, 7, 14, 16, 18, 23, 25** —
  confirm they still hard-stop identically in both arms without a live MCP Playwright server or
  project fixtures, and report them as an **eval-set gap**, not as agent quality.

### 2.2 Re-run `living-doc-create-functionality` triggers, alone

The one unresolved anomaly (see § 5). Twelve minutes, and it decides how much weight single-run
trigger figures can carry.

```bash
agentic/scripts/evals/run_triggers.sh      # delete its .done marker first to force a re-run
```

### 2.3 Benchmark

```bash
W=agentic-evals-workspace
python3 agentic/scripts/evals/normalize_grading.py $W/iteration-2
# then skill-creator's aggregate_benchmark per target, followed by:
python3 agentic/scripts/evals/fix_benchmark.py $W/iteration-2/<target> haiku opus c6dbcc7
python3 agentic/scripts/evals/compare_baseline.py $W/iteration-2
```

### 2.4 Regression gate — see § 3, it has a trap

### 2.5 Rewrite `agentic/docs/testing/baseline.md`

Validity block, models, per-target table, trigger table, one production-readiness line per target,
and what the suite still does not test. Name the **state measured** (uncommitted working tree on
`feature/52-agentic-layer`, parent `51f78b5`), not just the branch. Then set the **next** baseline
arm to the merge commit — see "Rolling the baseline forward" in
[`rerun-prompt.md`](agentic/docs/testing/rerun-prompt.md).

### 2.6 Clean up

`git worktree remove /tmp/agentic-baseline`, delete this file.

---

## 3. The Python / CI gate — a bare `pytest` lies

**`pytest` reports success while collecting nothing.** Every `test_*.py` under `agentic/skills/`
carries `__test__ = False`; they are standalone scripts that assert in plain functions and exit
non-zero from `__main__`. A green `pytest` is not evidence of anything
([`agentic/CONTRIBUTING.md:23`](agentic/CONTRIBUTING.md)).

What CI actually runs (`.github/workflows/agentic-tests.yml`), all three:

```bash
# 1. script tests — must pass on BOTH Python 3.10 and 3.14
pip install -r agentic/requirements-agentic-tests.txt
find agentic/skills -type f -name "test_*.py" | sort | xargs -n1 python

# 2. skill-format validation — needs Python 3.11+
pip install -r agentic/requirements-skill-lint.txt
agentskills validate agentic/skills/<name>

# 3. canon-copy check
bash agentic/scripts/sync-canon-copies.sh all
```

Three traps, in order of how easily they bite:

1. **Both interpreters.** 3.10 is the floor `living-doc-utilities` declares; a skill's scripts run
   under whatever the user's project has. Passing only on 3.14 is not passing.
2. **The canon-copy check.** A non-empty diff means a source canon page changed. **Regenerating and
   committing the artifact to make it green hides the finding** — protocol § 5 forbids it.
3. **`agentic/skills/shared/test_skill_doc_commands.py` is untracked** (`??` in git status). It is
   new in this change set and is the mechanical-facts guard the protocol asks for. It must be in
   the commit, and must pass on both interpreters.

Also useful before any eval work:

```bash
python agentic/scripts/evals-inventory.py            # body + trigger counts per skill
python agentic/scripts/evals-inventory.py --check    # shape only, exit 1 on a problem
```

---

## 4. Results — body evals (8 of 13 graded)

| Target | Evals | Assertions | with_skill | old_skill | reg evals |
|---|---|---|---|---|---|
| `bdd-maintain` | 11 | 39 | **1.00** | 0.92 | — |
| `data-cy-instrument` | 12 | 44 | **1.00** | 0.98 | — |
| `gherkin-living-doc-sync` | 17 | 74 | 0.91 | 0.84 | — |
| `gherkin-step` | 18 | 70 | 0.97 | 0.99 | 11, 13 |
| `living-doc-create-feature` | 17 | 74 | 0.82 | 0.78 | 8, 11 |
| `living-doc-create-functionality` | 19 | 86 | 0.83 | 0.87 | 1, 10, 16 |
| `living-doc-create-user-story` | 23 | 97 | 0.88 | 0.82 | 9, 17 |
| `living-doc-gap-finder` | 18 | 77 | **0.95** | 0.81 | — |
| **Graded subtotal** | **135** | **561** | **0.906** | **0.865** | |
| `living-doc-impact-analysis` | 16 | — | not graded | | |
| `living-doc-pageobject-scan` | 17 | — | not graded | | |
| `living-doc-scenario-creator` | 25 | — | not graded | | |
| `living-doc-update` | 18 | — | not graded | | |
| `@living-doc-bdd-copilot` | 26 | — | not graded | | |

### Gate verdict — one target blocks

Per the rule now in [`eval-protocol.md` § 5](agentic/docs/testing/eval-protocol.md) (no target may
drop on an assertion the grader confirms is correct):

- **`living-doc-create-functionality` BLOCKS.** Eval 10: the aligned arm emitted no JSON entity at
  all, contradicting its own `SKILL.md:148-150`; baseline emitted a complete one. Unrelated to the
  honesty fix. Fix and re-measure before merge.
- `gherkin-step` **passes** — both drops are wrong assertions. Eval 11 demands `page.close()` where
  closing the BrowserContext is correct; eval 13 demands constructor injection that
  `@cucumber/cucumber` does not support.
- `create-feature` 8, 11 and `create-user-story` 9, 17 are genuine but small. Details in each
  target's `GRADER-NOTES.md`.

### The `next_id.py` honesty fix worked

It never caused the aligned arm to lose to baseline in `create-feature`. In `create-functionality`
eval 14 the **baseline** arm prints `Ran: next_id.py … -> FUNC-008` while admitting the catalog is
not on disk — a fabricated run the assertion rewards. Where the aligned arm loses such a point it
is a corrected behaviour and the **assertion** is the defect.

---

## 5. Results — trigger evals (complete, 347/347)

| Skill | Overall | id-bearing | paraphrase | negatives |
|---|---|---|---|---|
| `bdd-maintain` | 19/20 | 3/3 | 7/7 | **9/10** |
| `data-cy-instrument` | 20/22 | 1/1 | 8/10 | 11/11 |
| `gherkin-living-doc-sync` | 27/30 | — | 12/15 | 15/15 |
| `gherkin-step` | **38/38** | — | 19/19 | 19/19 |
| `living-doc-create-feature` | 28/32 | 2/3 | 10/13 | 16/16 |
| `living-doc-create-functionality` | **20/34** | 2/4 | **3/15** | 15/15 |
| `living-doc-create-user-story` | 27/29 | 2/3 | 12/13 | 13/13 |
| `living-doc-gap-finder` | 28/32 | — | 13/17 | 15/15 |
| `living-doc-impact-analysis` | 19/23 | **3/3** (was 1/3) | 5/9 | 11/11 |
| `living-doc-pageobject-scan` | 28/30 | — | 13/15 | 15/15 |
| `living-doc-scenario-creator` | 25/29 | **9/12** (was 0/12) | 2/3 | 14/14 |
| `living-doc-update` | 21/28 | 5/6 | **3/9** (was 5/9) | 13/13 |
| **TOTAL** | **300/347 (0.865)** | 27/35 (0.77) | 107/145 (0.74) | **166/167** |

Previous run: 292/340 (0.859). **Precision 134/135 = 0.99.**

### 5.1 The id-bearing question is answered

| Group | id-bearing recall |
|---|---|
| Old baseline, whole suite | 0.31 |
| **Controls** — new id queries, descriptions untouched | **6/10 = 0.60** |
| **Rewritten descriptions** — `scenario-creator`, `impact-analysis`, `update` | **17/21 = 0.81** |

Both readings were partly right: id-bearing queries are a **moderate layer-wide weakness** (0.60
even untouched), and `scenario-creator`'s 0/12 was a genuine outlier **on top of** that, now fixed.
The old 0.31 was dominated by that one skill — excluding it, the old figure was 0.53. Control
denominator is only 10, so treat as directional.

`scenario-creator` improved by **generalisation**: its description cites `US-123/456/789`, the eval
queries use `US-007/003/009/011/012/015`. Nothing matched literally.

### 5.2 The one precision break is in untouched text

`bdd-maintain` fired at 0.67 on *"Heal the PageObjects — selectors are broken after the UI
redesign"*, which belongs to `pageobject-scan` HEALING. Its description at
`agentic/skills/bdd-maintain/SKILL.md:3` is **byte-identical to `c6dbcc7`** and already carries an
explicit *"Does NOT trigger for: … healing selector drift"* exclusion.

So **no rewritten description was widened too far** — but a negative clause naming the correct
alternative did not prevent the fire. Negative instructions are weaker than positive keyword
overlap.

### 5.3 `living-doc-update` is a net loss

+1 id-bearing, −2 paraphrase. Now misses *"Mark the legacy payment feature as deprecated in the
living doc"* (0.00) and *"I need to add an AC to an existing User Story…"* (0.00) — core to what the
skill is for. Four of seven misses sit at 0.33 and the paraphrase denominator is 9, so
**re-measure before rewriting**.

### 5.4 UNRESOLVED — `living-doc-create-functionality` collapsed

**0.88 → 0.59; paraphrase 13/15 → 3/15.** Verified:

- Description **byte-identical** to `c6dbcc7`.
- Queries effectively unchanged — 32 of 33 identical, 0 removed, 2 added.
- No harness errors, normal log size, 3 runs per query recorded.
- Twelve failures at **exactly 0.00**, not at the 0.33 boundary.
- Failures include *"Create a functionality entity for the payment retry logic"* (0.00), close to
  phrases the description lists verbatim.

Two hypotheses tested and **rejected**: no temp skills accumulate on disk, and there is no
positional decay (`gherkin-step`, position 8, scored 38/38). The two neighbouring `create-*`
controls reproduced their previous figures (29→28, 26→27), so this is **specific to this skill**,
not a run-wide effect.

**Settle it with the solo re-run in § 2.2.** If it reproduces at ~0.59, it is a real recall problem
in an unchanged skill that the previous run measured too optimistically. If it returns to ~0.88,
single-run trigger figures carry more variance than the baseline assumes — which would be the most
important methodological finding of this run.

### 5.5 `scenario-creator` residuals are a boundary problem, not an id problem

All three are coverage/skip questions. *"What is the scenario coverage for US-007?"* is
**near-verbatim** a phrase the description lists at
`agentic/skills/living-doc-scenario-creator/SKILL.md:13` (`"scenario coverage for US-789"`) and
still fires only 1 in 3 — interrogative framing flips it toward a read-only reading. `gap-finder`
legitimately owns *"documentation coverage"* (`SKILL.md:11`), so the term is contested by design.
**Do not widen `scenario-creator` blind**: `gap-finder` holds precision 15/15 and a contested term
is exactly how that breaks.

---

## 6. Defects in the run method itself

- **A runner wrote outside its designated output path.** `scenario-creator` eval 22's baseline
  answer landed in a mis-spelled sibling directory, leaving that arm silently empty. Recovered by
  hand. Guard: after each target assert `answers == evals × 2`.
- **Subagents cannot self-report usage** — all returned `DONE missing missing`. Authoritative
  figures are the harness's `subagent_tokens` / `duration_ms`. Some durations include queueing (one
  is 664 s) and are wall-clock, not model time.
- **A grader killed before writing its files produces nothing.** Graders must write per-eval as
  they go.
- **One run per arm means no variance.** § 5.4 is the live demonstration of why that matters.

---

## 7. New helper scripts (`agentic/scripts/evals/`)

Added this session so the run reproduces off this machine. Pure bookkeeping, no judgement; drop
them if you prefer them out of the repo.

| Script | Purpose |
|---|---|
| `gen_runner_prompts.py` | One `prompt.txt` per eval × arm; fixtures redirected outside the eval tree, no-`evals/` rule inlined |
| `gen_grader_prompts.py` | One `grader-prompt.txt` per target, with grading rules and the required `grading.json` shape |
| `run_triggers.sh` | Serial trigger driver: `--num-workers 1`, one skill at a time, `.done` markers so it resumes |
| `trigger_report.py` | Aggregates trigger JSON into the id-bearing / paraphrase / precision table |

**Windows:** `run_triggers.sh` is bash — use Git Bash or WSL. Generated `prompt.txt` /
`grader-prompt.txt` hold absolute macOS paths and must be regenerated.

---

## 8. Working tree

Uncommitted, nothing staged, no commits made by this run. Beyond the pre-existing SKILL.md / eval
edits under test:

- `agentic/docs/testing/rerun-prompt.md` (new)
- `agentic/docs/testing/eval-protocol.md` (pointer + no-degradation gate)
- `agentic/docs/testing/baseline.md` (pointer only; **full rewrite still pending**)
- `.github/agents/eval-runner.agent.md` (invocation modes: no-arg, partial run, filled prompt)
- `agentic/scripts/evals/` (four new scripts above)
- `agentic/skills/shared/test_skill_doc_commands.py` (**untracked — must be committed**)
- `NEXT_STEPS.md` (this file — delete before merge)

---

## 9. Fix list — consolidated from the grader notes

> **These exist nowhere else.** The per-target `GRADER-NOTES.md` files live only in the gitignored
> workspace, which is not being archived. This section is the surviving record.
>
> **Verify each before acting.** These are Opus grader findings with `file:line`, not my own
> confirmations — in the previous run two grader claims were confidently wrong. Items the grader
> itself marked CONFIRMED were opened and checked by it; items marked UNVERIFIED were not.
> Protocol § 3: confirm against the file first. Checking one costs a single command.

### 9.1 Skill defects (fix the skill)

| Target | Location | Claim |
|---|---|---|
| `bdd-maintain` | `SKILL.md:81` | Understates `find_unused_po_methods.py` scope — script also scans `fixtures.ts` and every `*.ts` (`find_unused_po_methods.py:98-104`) |
| `bdd-maintain` | `SKILL.md:91` | Same for `find_unused_po_components.py` (`:49-68`) |
| `bdd-maintain` | `SKILL.md:126-132` | **UNVERIFIED** — barrel re-export blind spot |
| `data-cy-instrument` | `SKILL.md:227` vs `:233`, `:218` | Phase 6 contradicts itself and the PageObject-header canon: tells reader to hand-edit `# status: planned → active` |
| `data-cy-instrument` | `SKILL.md:89`, `:91` | Instructs emitting a **fabricated** issue URL (`issues/XXXX`) concretely |
| `data-cy-instrument` | `SKILL.md:102`, `:105-106`, `:133` | Project-specific identifiers leak into generic answers (`aul-ui/src/...`, `BD_CTX_API`) |
| `data-cy-instrument` | `SKILL.md:214` | Shadow-DOM check conflated with third-party forwarding (minor) |
| `gherkin-living-doc-sync` | `SKILL.md:151-154` | Instructs fabrication under missing input — propose matching ACs with no catalog-availability guard |
| `gherkin-living-doc-sync` | `SKILL.md:193`, `:196` | No rule for a variant value the AC does not declare → `STALE_AC_REF` never named |
| `gherkin-living-doc-sync` | `SKILL.md:106` | `@AC:` tag described without naming its script/CI consumers |
| `gherkin-step` | `SKILL.md:322`, `:327` | **CONFIRMED** — shows fake behave hook decorators that `:45-47` forbids |
| `gherkin-step` | `SKILL.md:278`, `:283`, `:343`, `:351` | **CONFIRMED** — playwright-bdd `async ({ fixture })` signature that `:30-31` rules out |
| `living-doc-create-feature` | `SKILL.md:133` vs `:112-121` | Draft-vs-defer conflict — **cause of body eval 8 regression** |
| `living-doc-create-feature` | `SKILL.md:217` | Rename guidance omits numeric-ID stability |
| `living-doc-create-feature` | `SKILL.md:120-121` | Factually wrong — calls `FEAT-010`/`FEAT-011` "slug-based"; they are numeric |
| `living-doc-create-feature` | `SKILL.md:192` | Anti-pattern table has no duplicate-Feature-name entry |
| `living-doc-create-feature` | `SKILL.md:123-125` | **Honesty guard scoped to `next_id.py` only** — eval 16 fabricated a `validate_entity.py` run. Generalise it |
| `living-doc-create-functionality` | `SKILL.md:148-150` | **Cause of body eval 10 — the blocking regression.** Aligned arm emitted no JSON entity |
| `living-doc-create-functionality` | `SKILL.md:88-90` vs `:92-102` | Says the `func_type` table is "not repeated here", then repeats it in full |
| `living-doc-create-functionality` | `SKILL.md:82-109` | No AC-variant / `Aspect:` rule; `visibility` tie-break underspecified |
| `living-doc-create-functionality` | `SKILL.md:187`, `:166` | No placeholder convention for an unresolved `parent_feature` |
| `living-doc-create-functionality` | `SKILL.md:197`, `:263` | No rule for error codes the prompt does not supply (forces invention) |
| `living-doc-create-user-story` | `SKILL.md:125` | **AC-variants canon unreachable** — only link into `living-doc-bdd-schemas.md:145-152` points at `#indentation` |
| `living-doc-create-user-story` | `SKILL.md:265` | Missing the "shared Functionality links to both stories" clause that `:264` has for the two-actor case |
| `living-doc-create-user-story` | `SKILL.md:272` | Vague/over-specific outcome warning applied only half the time |
| `living-doc-gap-finder` | `SKILL.md:49` vs `:257-260` | **CONFIRMED** — `/account/preferences` contradiction; both arms fell into it |
| `living-doc-gap-finder` | `SKILL.md:72-83` | Taxonomy table alignment — `FEATURE_WITHOUT_USER_STORY` / `_FUNCTIONALITY` |

### 9.2 Eval defects (fix the eval, not the skill)

| Target | Location | Claim |
|---|---|---|
| `bdd-maintain` | `evals.json:61`, `:59` | Stale base-class-alias claim, contradicted by eval 11 and `SKILL.md:130` |
| `bdd-maintain` | `evals.json:126` | Unfalsifiable — no suite exists, so "no false positives" passes vacuously |
| `data-cy-instrument` | `evals.json:99`, `:100` | Require data the prompt never supplies (library version, issue URL) |
| `data-cy-instrument` | `evals.json:85-87` | Satisfied by echoing a sentence `SKILL.md:24` orders verbatim |
| `data-cy-instrument` | `evals.json:82` | Stale `expected_output` — describes ng-add phases that do not exist |
| `gherkin-living-doc-sync` | `evals.json:12`, `:13`, `:40`, `:42`, `:57` | Satisfiable only by inventing paths, line numbers, AC ids or a PageObject method |
| `gherkin-living-doc-sync` | `evals.json:133` | **Factually wrong** — `scan_ac_links.py:277-292` takes no such flags |
| `gherkin-living-doc-sync` | `evals.json:129` | Stale `expected_output` (`--catalog`, stale-ID reporting) |
| `gherkin-living-doc-sync` | `evals.json:210` | Wants `STALE_AC_REF`, a token this SKILL.md never defines |
| `gherkin-step` | `evals.json:144` | **Wrong** — demands `page.close()`; closing the BrowserContext is correct |
| `gherkin-step` | `evals.json:168` | **Wrong** — demands constructor injection `@cucumber/cucumber` does not support |
| `gherkin-step` | `evals.json:131`, `:117`, `:219` | Suspect; `:109-119` is a coverage gap |
| `living-doc-create-feature` | `evals.json:16`, `:200`, `:122` | Reward the fabricated `Ran: next_id.py` claim |
| `living-doc-create-feature` | `evals.json:200` vs `:205` | **A1 and A6 directly contradict** — A1 passable only via the line A6 forbids |
| `living-doc-create-feature` | `evals.json:190`, `:217`, `:228-229` | Suspect / ambiguous |
| `living-doc-create-functionality` | `evals.json:176` vs `:182` | **Mutually contradictory**; `:176` rewards a fabricated run (`SKILL.md:186` forbids) |
| `living-doc-create-functionality` | `evals.json:14`, `:33`, `:177`, `:196`, `:221` | Require inventing error codes the prompt never supplies |
| `living-doc-create-user-story` | `evals.json:175`, `:176` | Reward claiming `next_id.py` ran with no catalog present |
| `living-doc-create-user-story` | `evals.json:15` | Conditional warning whose condition never fires |
| `living-doc-gap-finder` | `evals.json:16`, `:24`, `:18` | Contradict `SKILL.md:46-47`, `:49`, `:284` and the eval's own `expected_output` |
| `living-doc-gap-finder` | `evals.json:85`, `:8`, `:21` | Stale entity references (FEAT-005 / FEAT-008) |

### 9.3 Eval-set gaps (no score can show these)

- **Nine `@living-doc-bdd-copilot` evals** (2, 4, 5, 7, 14, 16, 18, 23, 25) hard-stop identically
  in both arms without a live MCP Playwright server or project fixtures — a third of its
  assertions. **Still to be confirmed in this iteration** (that target is ungraded).
- **Saturation.** `data-cy-instrument` 11 of 12 evals and `bdd-maintain` 9 of 11 are
  non-discriminating — both arms score identically, mostly because the SKILL.md carries a matching
  "when asked X, say Y" line and both arms recite it.
- **One run per arm = no variance.** § 5.4 is the live cost of this.
- **No fixture for most "show me the output of" evals**, so assertions pass on a schema-shaped
  example produced by an answer that did no work.
