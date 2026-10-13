# Eval baseline — iteration 3

The reference every later eval run is compared against. Produced by the protocol in
[eval-protocol.md](eval-protocol.md); the run's own evidence (answers, timings, grading files and
grader notes per target) is regenerable and deliberately **not** tracked — see
`agentic-evals-workspace/` in `.gitignore`. Iteration 1's figures (commit `51f78b5` against
`c6dbcc7`, Opus 5 grading) are superseded; they are not comparable eval-by-eval, because the eval set,
the grader model and the run count all changed.

## Validity

| | |
|---|---|
| Measured state (`with_skill`) | commit **`4999b05`**, branch `feature/52-agentic-layer` — `git diff 4999b05 -- agentic/skills agentic/agents` empty for every run |
| Baseline arm (`old_skill`) | commit **`23b36a3`** (pre-fix skills). Its answers are iteration 2's `with_skill` answers, **reused** (`prepare_iteration.py`): no eval prompt changed in the fix pass, only assertions and expected outputs, so the reused answers were re-graded against the current assertions |
| Runs per arm | `with_skill` **2**, `old_skill` **1** |
| Body evals | **237** (211 across 12 skills, 26 for the agent) — 474 measured runs, 711 graded answers, 1030 assertions per run |
| Trigger evals | 347 queries × 3 runs, from an empty project outside any repository |
| Regression gate | green — see [below](#regression-gate) |

Deviations that a later run must know about:

- **Orchestrator model.** The run was orchestrated by Opus 5.5, not Sonnet as planned. The
  orchestrator produced no answers and no grades.
- **Two machines.** The run moved from Windows to macOS part-way (session limits). Runs of
  bdd-maintain to impact-analysis and pageobject-scan evals 1 and 10–17 are Windows runs; the
  rest of pageobject-scan, scenario-creator, living-doc-update and the agent are macOS runs. **Pass
  rates are comparable across the two; tokens and durations are not**: a macOS run cost
  ~52–58k tokens and 10–40 s, a Windows run ~38–50k and 120–200 s, for the same kind of eval. A
  probe showed macOS runners also received the user's auto-memory *index* (one-line entries, no
  eval data) and a larger skill list.
- **The two arms ran in different sessions.** `old_skill` answers come from iteration 2 (another
  machine and session), so a difference on skill text that is identical in both commits can be
  session variance, not the change. That is why the below-baseline verdicts below read the skill
  text at both commits before calling anything a regression.
- **Session limits killed runs and graders.** Five create-feature answers were complete on disk
  and kept with timing recorded as `missing` (eval 10 r2, 11 r2, 13 r1, 14 r2, 16 r2); killed
  graders were resumed with an instruction not to regrade existing files.
- **Sibling-fixture contamination.** Four `with_skill` runs answered from another eval's fixture
  found in the shared staging directory and were quarantined and re-run (create-feature eval 9 r1
  and eval 1 r2, gap-finder eval 6 r1 and r2). From then on the staging directory stayed empty,
  and each eval that owns a fixture ran alone with only its own file staged.
- **Tool deviations.** `compare_baseline.py` reads only `with_skill/run-1`, so run-2 and the
  mean ± stddev come from `benchmark.json`. `aggregate_benchmark`'s pass rate is the mean of
  per-eval-run rates, not assertion-weighted; both are reported below.

## Models

Fixed for this baseline and every later comparison against it — a different grader model compares
graders, not skills.

| Role | Model |
|---|---|
| Body-eval execution, both arms | **Haiku** — `Agent`, `subagent_type: general-purpose`, `model: "haiku"`; never `fork` |
| Grading, all 13 targets | **Sonnet** — one grader per target, at most three at a time |
| Trigger-eval execution | **`claude-haiku-4-5-20251001`** |
| Orchestration (no answers, no grades) | Opus 5.5 |

## Body evals

"r1" / "r2" are the two measured runs, assertion-weighted. "mean ± sd" is `benchmark.json`
(mean of per-eval-run pass rates, both runs). "Δ" is the mean of r1 and r2 minus the baseline,
assertion-weighted. "gain" / "reg" count evals whose mean measured score is above / below the
baseline's single run.

| Target | Evals | Assertions | r1 | r2 | mean ± sd | Baseline | Δ | gain | reg |
|---|---|---|---|---|---|---|---|---|---|
| `bdd-maintain` | 11 | 39 | 0.92 | 0.92 | 0.92 ± 0.16 | 1.00 | −0.08 | 0 | 4 |
| `data-cy-instrument` | 12 | 44 | 0.98 | 1.00 | 0.99 ± 0.07 | 0.98 | +0.01 | 1 | 1 |
| `gherkin-living-doc-sync` | 17 | 74 | 0.91 | 0.91 | 0.91 ± 0.12 | 0.95 | −0.04 | 3 | 6 |
| `gherkin-step` | 18 | 70 | 0.99 | 0.97 | 0.98 ± 0.07 | 0.99 | −0.01 | 0 | 1 |
| `living-doc-create-feature` | 17 | 75 | 0.92 | 0.87 | 0.91 ± 0.15 | 0.80 | +0.09 | 7 | 2 |
| `living-doc-create-functionality` | 19 | 87 | 0.89 | 0.86 | 0.86 ± 0.26 | 0.82 | +0.06 | 5 | 3 |
| `living-doc-create-user-story` | 23 | 97 | 0.92 | 0.90 | 0.90 ± 0.20 | 0.88 | +0.03 | 4 | 3 |
| `living-doc-gap-finder` | 18 | 77 | 0.90 | 0.83 | 0.86 ± 0.23 | 0.95 | −0.08 | 1 | 8 |
| `living-doc-impact-analysis` | 16 | 65 | 0.92 | 0.92 | 0.93 ± 0.14 | 0.97 | −0.05 | 1 | 5 |
| `living-doc-pageobject-scan` | 17 | 85 | 0.93 | 0.93 | 0.93 ± 0.20 | 0.72 | +0.21 | 6 | 1 |
| ↳ excluding `requires` (eval 6) | 16 | 80 | 0.97 | 0.97 | 0.97 ± 0.07 | 0.76 | +0.21 | 5 | 1 |
| `living-doc-scenario-creator` | 25 | 106 | 0.90 | 0.90 | 0.89 ± 0.18 | 0.82 | +0.08 | 8 | 5 |
| ↳ excluding `requires` (eval 6) | 24 | 102 | 0.92 | 0.92 | 0.92 ± 0.13 | 0.84 | +0.08 | 8 | 5 |
| `living-doc-update` | 18 | 78 | 1.00 | 0.99 | 1.00 ± 0.02 | 0.91 | +0.08 | 4 | 0 |
| `@living-doc-bdd-copilot` | 26 | 133 | 0.53 | 0.54 | 0.56 ± 0.37 | 0.47 | +0.07 | 5 | 0 |
| ↳ excluding `requires` (11 evals) | 15 | 74 | 0.81 | 0.82 | 0.84 ± 0.18 | 0.70 | +0.11 | 4 | 0 |
| **Total** (all evals) | **237** | **1030** | **0.875** | **0.863** | | **0.829** | **+0.040** | **45** | **39** |

The "excluding `requires`" rows drop the evals that need a live MCP Playwright server or project
files. Those evals measure the missing environment and hard-stop identically in every arm.

### Below the baseline — what each drop is

Every eval with a measured run below the baseline was read against its assertion. The skill text behind
the assertion was then compared at `23b36a3` and `4999b05`. The per-assertion verdicts:

- **Single-run misses** (the sibling run passes, the skill text is unchanged): most of the "reg"
  column, including the whole of bdd-maintain's. This is variance, not a regression.
- **Omissions on unchanged text.** Both measured runs miss an assertion the grader confirms, but
  the text behind it is byte-identical in both commits. Examples are gherkin-living-doc-sync's
  confirmation prompt, sync direction and Project Profile note, impact-analysis's fenced signature
  and "repeated = higher risk", and gap-finder's weighted-fraction and bare-tag points. The fix
  pass did not cause them; they are recorded as weak spots. **gap-finder's −0.08 has no fix-pass
  cause.**
- **Regressions caused by a fix-pass edit.** These are confirmed assertions, dropped in both
  runs, where the edited text explains the drop:
  1. **impact-analysis eval 15** — routing new Features to `living-doc-create-feature`. The
     entity-ID rewrite of `SKILL.md:63` removed the skill's only pointer to that skill.
  2. **scenario-creator eval 8** — the coverage table after the feature file. `SKILL.md:222`
     still mandates it, but the new `:232-235` wording ("the summary you write", not script
     output) led both runs to omit it when no script ran.
  3. **create-feature eval 6** — stating that only UI and API surface types exist. The rule
     (`SKILL.md:48`) is unchanged; the runs drafted (the new draft-first rule) instead of asking.
     Low severity.

  Per [eval-protocol.md § 5](eval-protocol.md#5-scope-rules), a confirmed-assertion drop blocks the
  merge until fixed and re-measured. All three are one-line wording fixes.
- **Eval defects.** gap-finder `evals.json:16` contradicts its own fixture (FUNC-002 has
  `ac_count: 5`) and rewards un-normalised script output. gap-finder eval 12 A3 tests a point no
  skill text teaches. scenario-creator eval 5 A2 is ambiguous about tag placement. impact-analysis
  `evals.json:194` still names the retired "Rename a Feature" workflow.

### Defects found in the targets

All were confirmed against the file. These are in addition to the regressions above:

- **Example values leak into answers as facts.** Runs copied concrete values from worked examples:
  - gherkin-living-doc-sync `SKILL.md:171-172` (`CheckoutPage.confirm_order()`, `checkout_steps.py:34`)
  - pageobject-scan `SKILL.md:137-144`, `:319-321`
  - living-doc-update `SKILL.md:375`, `:390` (story titles)
  - create-feature `SKILL.md:175` (`team-notifications`, copied by the agent)

  Mark them as placeholders.
- **gap-finder.** GAP ids depend on set iteration order (`compute_gaps.py:137`), so they are not
  deterministic. Wrong-shaped input silently yields an empty report (`:57-59`). The script emits
  `UNDOCUMENTED_FUNCTIONALITY` where the taxonomy says `UNTESTED_AC` (`:245-250` vs
  `SKILL.md:46-47`), so a correct report depends on manual normalisation. "9 gap types"
  (`SKILL.md:27`) contradicts "Ten" (`:68`). `SKILL.md:39` points readers into `evals/`.
- **pageobject-scan.** Stale key names `data-cy` / `data_cy` in the closeout gate (`SKILL.md:371`,
  `:376`), where the validator sorts by `test_id` (`validate_artifacts.py:95-97`).
- **create-functionality.** The AC-variants rule (`SKILL.md:69`) has no slot in the entity
  template (`:173-176`), and `:66` asks for "3-7 ACs". Eval 19 scores 0/4 in every run of both
  arms; every run splits one variant AC into three.
- **bdd-maintain.** `SKILL.md:106` ("Before any REMOVE operation | All three") contradicts the
  order at `:38` and `:135`.
- **Agent.** `living-doc-bdd-copilot.agent.md:241` names `scripts/next_id.py`, which exists only
  under each create-* skill.

## Trigger evals

347 queries × 3 runs, `--num-workers 1`, one skill at a time with nothing else in flight. A query
passes when its trigger rate is on the right side of 0.5. These figures start a new series:
`run_triggers.sh` now runs every query from an empty project outside any repository, whereas
iteration 2 ran with the user's home folder as the project. They are **not comparable** to
iteration 1's or iteration 2's.

| Skill | Overall | Recall (all positives) | Id-bearing | Paraphrase | Negatives held |
|---|---|---|---|---|---|
| `bdd-maintain` | 19/20 | 9/10 | 3/3 | 6/7 | 10/10 |
| `data-cy-instrument` | 20/22 | 9/11 | 1/1 | 8/10 | 11/11 |
| `gherkin-living-doc-sync` | 26/30 | 11/15 | — | 11/15 | 15/15 |
| `gherkin-step` | 35/38 | 16/19 | — | 16/19 | 19/19 |
| `living-doc-create-feature` | 25/32 | **9/16** | 2/3 | 7/13 | 16/16 |
| `living-doc-create-functionality` | 31/34 | 16/19 | 3/4 | 13/15 | **14/15** |
| `living-doc-create-user-story` | 26/29 | 13/16 | 2/3 | 11/13 | 13/13 |
| `living-doc-gap-finder` | 28/32 | 13/17 | — | 13/17 | 15/15 |
| `living-doc-impact-analysis` | 18/23 | **7/12** | 3/3 | 4/9 | 11/11 |
| `living-doc-pageobject-scan` | 29/30 | 14/15 | — | 14/15 | 15/15 |
| `living-doc-scenario-creator` | 25/29 | 11/15 | 10/12 | 1/3 | 14/14 |
| `living-doc-update` | 23/28 | **10/15** | 6/6 | 4/9 | 13/13 |
| **Total** | **304/347 (0.88)** | **138/180 (0.77)** | 30/35 (0.86) | 108/145 (0.74) | 166/167 |

- **Precision 0.99.** One false fire in 167 negatives:
  `living-doc-create-functionality` fired on 1 of 3 runs of "Update the living doc entity for the
  discount validation Functionality". That request belongs to `living-doc-update`.
- **Every other failure is a miss, not a mis-fire.** 42 positives did not trigger. They cluster
  in two places:
  - **Questions about the domain, with no verb the description names.** For example, "What
    feature owns the checkout screen?", "What is our documentation coverage percentage?", "A test
    is pointing to a deprecated AC — what kind of gap is that?", "An AC was descoped last sprint —
    what should happen to the linked scenario?". Haiku answers these itself.
  - **Requests phrased as a generic coding or editing task.** For example, "Write step definitions
    for the checkout feature file", "Create a feature entity for the authentication module",
    "Update the living doc Functionality entry for the promo validation module". These read as a
    plain coding or editing job.
- **Naming an entity id no longer suppresses triggering.** Id-bearing recall is 0.86, against 0.31
  in iteration 1, and scenario-creator is 10/12 on `US-<id>` queries, against 0/12. Because the
  environment changed, this is a new baseline, not a measured improvement.
- **Weakest recall:**
  - `living-doc-create-feature` 9/16 — 6 of its 7 misses are rate 0.00.
  - `living-doc-impact-analysis` 7/12 — all five misses are rate 0.33, so it sits at the threshold.
  - `living-doc-update` 10/15.
- No `description:` was rewritten. Per
  [eval-protocol.md § 5](eval-protocol.md#5-scope-rules), a rewrite needs its own re-measure.

The 42 failing queries, with their rates, are in `trigger-evals-3/` (`trigger_report.py`).

## Production readiness

| Target | Can it be relied on? |
|---|---|
| `bdd-maintain` | Yes for analysis. Fix the REMOVE ordering contradiction (`SKILL.md:106`) before trusting REMOVE. The suite is saturated, so it guards but cannot show improvement. |
| `data-cy-instrument` | Yes. Saturated, as above. |
| `gherkin-living-doc-sync` | Usable with review. Weak spot: the structured output (DRIFT/SYNC blocks, confirmation prompt, sync direction) slips on question-style prompts, and its example values leak. |
| `gherkin-step` | Yes. |
| `living-doc-create-feature` | Yes for drafts. `FEAT-PENDING` drafting works. Fix the eval 6 regression and the example-value leak. Weakest trigger recall (9/16): it is often not loaded unless asked for by name. |
| `living-doc-create-functionality` | Not for variant ACs: it splits them every time (eval 19). Otherwise yes. |
| `living-doc-create-user-story` | Yes. The gain comes from the AC-variants rule (evals 20-21). |
| `living-doc-gap-finder` | Not unattended. Correct reports depend on manual normalisation of script output, and GAP ids are not stable between runs. |
| `living-doc-impact-analysis` | Yes for tracing. Fix the create-feature routing regression; signature formatting is inconsistent. Trigger recall 7/12, every miss at rate 0.33. |
| `living-doc-pageobject-scan` | Yes for questions and maintenance from supplied details. Live-app scanning is untested (MCP). Fix the stale key names. |
| `living-doc-scenario-creator` | Yes for generation. Fix the coverage-table regression. |
| `living-doc-update` | Yes — 155/156. Remove the concrete story titles from its templates. Trigger recall 10/15: generic "update the entry" phrasings miss. |
| `@living-doc-bdd-copilot` | Its routing and refusals are reliable (0.81 excluding `requires`). Its main path — crawl, scan, generate against a live app — is untested. |

## What this suite does not test

- **The agent's main path.** 11 of its 26 evals need a live MCP Playwright server or project files,
  and hard-stop identically in every arm. Every agent eval has `files: []`, so assertions about
  catalog-derived facts can only pass on invented data (24 suspect pairs per the grader).
- **Live-app scanning** for pageobject-scan (eval 6, `requires: mcp-playwright`), and scenario
  generation against a real project tree (scenario-creator eval 6).
- **Saturation.** data-cy-instrument and bdd-maintain score near 100% in both arms. Most of their
  evals are satisfied by restating the skill, so they guard against a regression but cannot show an
  improvement.
- **"Show me the output of" evals without a fixture.** A schema-shaped example passes them; it
  shows the skill was recited, not that it ran.
- **Triggering inside a real project.** Every trigger query runs cold, from an empty project. In
  a living-doc project the surrounding context should steer the generic phrasings that miss here.
  The suite cannot show that. For example, create-functionality recall was 1/19 to 5/19 in
  iteration 2's contaminated environment and is 16/19 cold here.
- **Fixture isolation.** Runner prompts forbid only `/evals/` paths and stage fixtures in one shared
  directory (`gen_runner_prompts.py`). Four runs read a sibling eval's fixture before the
  one-fixture-at-a-time rule. Stage per eval before the next run.
- **Variance.** Two measured runs give a spread, not a distribution. The baseline arm has one run,
  from another session, so a small difference on unchanged skill text is not signal.

## Regression gate

Run at `4999b05` on macOS:

| Check | Result |
|---|---|
| Every `agentic/skills/**/test_*.py`, Python 3.10.18 | 18/18 pass |
| Same, Python 3.14.7 | 18/18 pass |
| `agentskills validate` per skill (`skills-ref` 0.1.1) | 13/13 valid |
| `sync-canon-copies.sh all`, then `git diff --exit-code -- agentic/skills/shared/references/` | no diff |
| `lychee`, CI arguments, over tracked Markdown | 497/497 OK |

## Reproducing

Send the prompt in [rerun-prompt.md](rerun-prompt.md). Then follow [eval-protocol.md](eval-protocol.md),
with the same models as above:

- Reuse the previous iteration's `with_skill` answers as the new `old_skill` arm with
  `agentic/scripts/evals/prepare_iteration.py`, unless an eval prompt changed.
- Run each eval that owns a fixture alone, with only its fixture staged.
- Run trigger evals with `run_triggers.sh`, with nothing else in flight.
