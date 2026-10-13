# NEXT_STEPS — iteration-3 handoff

> **Temporary. Delete before merge** (the iteration-3 session does it as its last step). Written
> 2026-10-13 by the fixing session. Everything normative lives in
> [`agentic/docs/testing/`](agentic/docs/testing/eval-protocol.md); nothing here is canon.

## 1. State

| Phase | State |
|---|---|
| Iteration 2 — body runs | Complete, 474/474, timings recorded (Mac) |
| Iteration 2 — grading | Complete, 13/13 targets (8 by Opus 5 on the Mac, 5 by Opus 5.5 here — diagnostic only, so the mix does not matter) |
| Iteration 2 — triggers | Complete, 347/347; create-functionality re-run here (§ 4) |
| Fix pass | Done in this session — § 3 |
| Regression gate (local) | Green — script tests 18/18 on Python 3.10 and 3.14 (re-checked after the last fixes), `agentskills validate` 13/13, canon copies match. Link check not run locally (no `lychee`); CI runs it |
| Iteration 3 | **Not started** — the new initial baseline. Prompt in § 2 |

Evidence lives in the gitignored `agentic-evals-workspace/` on this Windows machine: iteration-2
answers, `grading.json`, `GRADER-NOTES.md` per target, `trigger-evals-2/`, and the re-runs in
`trigger-evals-2-rerun/`.

Owner decisions (2026-10-13): iteration 3, not iteration 2, becomes the baseline; body runs on
Haiku, grading on Sonnet for this and every later comparison; the measured arm runs twice;
saturated evals and the agent's environment-blocked evals are recorded as known gaps, not fixed
now; no manual end-to-end test of `@living-doc-bdd-copilot` before merge.

## 2. Prompt for the iteration-3 session

Paste into a fresh session. Orchestrator on **Sonnet**; runners on **Haiku**; graders on **Sonnet**.

````text
Use `@eval-runner` (`.github/agents/eval-runner.agent.md`) and follow
`agentic/docs/testing/eval-protocol.md`. Read `NEXT_STEPS.md` first — it is the handoff from
the fixing session. This prompt is a filled-in `agentic/docs/testing/rerun-prompt.md`; its
ground facts override that page and the agent file where they differ.

**Goal.** Iteration 3 = the new initial baseline. Measure the fixed working tree against the
pre-fix state, then rewrite `agentic/docs/testing/baseline.md`.

## Models — fixed for this run and every later comparison against it

- Orchestrator (you): Sonnet.
- Body-eval runners: **Haiku** (`model: haiku`), every run, both arms. Never a fork-style
  subagent — it inherits your model.
- Graders: **Sonnet** (`model: sonnet`), all 13 targets. Do not mix grader models.
- Trigger runs: `claude-haiku-4-5-20251001` (already set in `run_triggers.sh`).

## Ground facts

- Platform: Windows. Run Python with `PYTHONUTF8=1`; run `run_triggers.sh` from Git Bash.
  `python3` may be a Microsoft Store stub — use `python`.
- Workspace: `agentic-evals-workspace/` (gitignored). `iteration-2/` is complete and graded;
  its `with_skill` answers are the pre-fix skills (commit `23b36a3`) on Haiku.
- **No baseline worktree is needed.** No eval prompt changed in the fix pass, so the
  `old_skill` arm is the iteration-2 `with_skill` answers, reused. Only assertions and
  expected outputs changed; the reused answers are graded again against them.
- Expected counts: `python agentic/scripts/evals-inventory.py` → **237 body / 347 trigger**,
  unchanged from iteration 2. Stop only if they differ.
- Treat the working tree as `with_skill` (the fixes are in it, possibly committed by now).

## Steps

1. Build the iteration, reusing the baseline arm and creating two runs of the measured arm:
   `python agentic/scripts/evals/prepare_iteration.py agentic-evals-workspace 3 2 2`
   It must report every eval's baseline answer as reused. If it lists any eval as needing
   a baseline run, stop and report it — that means an eval prompt changed.
2. `python agentic/scripts/evals/gen_runner_prompts.py agentic-evals-workspace/iteration-3`
   → one `prompt.txt` per `with_skill/run-1` and `with_skill/run-2` (474 total).
   Spawn one Haiku subagent per prompt file, telling it to follow the file exactly. Finish
   one target before the next. After each run lands, record the harness figures:
   `python agentic/scripts/evals/record_timing.py <target_dir> haiku eval-<n>:with_skill/run-<k>:<tokens>:<ms>`
   After each target assert answers == evals x 3 (two measured runs + one reused).
3. `python agentic/scripts/evals/gen_grader_prompts.py agentic-evals-workspace/iteration-3`
   then one Sonnet grader per target pointed at its `grader-prompt.txt`, at most three at a
   time. Graders write each eval's grading.json immediately — never batched.
4. Benchmark per target: `normalize_grading.py`, skill-creator's `aggregate_benchmark`,
   then `fix_benchmark.py <target_dir> haiku sonnet 23b36a3`, then `compare_baseline.py`.
5. Trigger evals — **alone, nothing else in flight**, from Git Bash:
   `TRIGGER_OUT="$(pwd -W)/agentic-evals-workspace/trigger-evals-3" bash agentic/scripts/evals/run_triggers.sh`
   (~3 h unattended; resumable via `.done` markers). It now runs from an empty project
   outside any repository, so figures are NOT comparable to iteration 2's — say so; they
   are the new clean trigger baseline. Then `python agentic/scripts/evals/trigger_report.py agentic-evals-workspace/trigger-evals-3`.
6. Regression gate: every `agentic/skills/**/test_*.py` on Python 3.10 (a `uv venv
   --python 3.10` with `agentic/requirements-agentic-tests.txt`) and 3.14; `agentskills
   validate` per skill (`agentic/requirements-skill-lint.txt`); `sync-canon-copies.sh all`
   then `git diff --exit-code -- agentic/skills/shared/references/` (a line-ending-only
   status change is not a diff — restore those files); link check if `lychee` is installed,
   otherwise say CI runs it.
7. Rewrite `agentic/docs/testing/baseline.md`: validity block (state measured: commit or
   working tree; old_skill = `23b36a3` answers reused from iteration 2; models above; runs
   per arm: with_skill 2, old_skill 1), per-target table with mean ± stddev for with_skill,
   trigger table, one production-readiness line per target, and what the suite does not
   test (start from NEXT_STEPS.md "Known gaps"). Every target with evals labelled `requires`
   (`@living-doc-bdd-copilot`, pageobject-scan, scenario-creator) is reported twice: all evals,
   and excluding the labelled ones — those measure the missing environment, not the skill.
8. Delete `NEXT_STEPS.md`. Leave everything uncommitted.

## What to expect, so you do not misread it

NEXT_STEPS.md "Fix log" lists each change and the direction it should move the score. In
short: create-functionality eval 10 and create-feature eval 8 should now pass (drafts with a
`*-PENDING` placeholder instead of withholding or inventing an ID); assertions that rewarded
invented IDs, error codes, URLs or script runs were corrected, so honest answers stop losing
points; gherkin-step evals 11 and 13 now match the skill's (correct) Cucumber pattern.

## Hard stops

- No git writes. Never edit a skill, an agent, or an eval file. Never rewrite a `description:`.
- Every finding cites `file:line`, confirmed against the file before you report it.
- Keep `agentic-evals-workspace/PROGRESS.md` current after every target.
````

## 3. Fix log — what changed, and which way each score should move

Every fix has a guard: a script test (`agentic/skills/shared/test_skill_doc_consistency.py`,
`test_script_output_encoding.py`) or a corrected/added eval assertion.

| Target | Change | Expected effect |
|---|---|---|
| create-functionality | Unresolved parent Feature → `FEAT-PENDING` placeholder, JSON still emitted (`SKILL.md` Step 2 + Step 5 rules). This was the merge blocker: eval 10 withheld the entity | eval 10 ↑ (eval now asserts the placeholder) |
| create-functionality | No error code in the prompt → propose one, labelled as a proposal | evals 1, 2, 16 ↑ (assertions now accept labelled proposals) |
| create-functionality | Eval 14 asked for a `next_id.py` run with no catalog, contradicting its own honesty assertion | eval 14: honest "derived from the stated range" answer now passes |
| create-functionality | AC-variants pointer; `func_type` table wording | small |
| create-feature | No catalog → draft with `FEAT-PENDING` instead of deferring (eval 8 regression); "only claim a command ran if it ran" now covers every script, not just `next_id.py`; wrong slug example (`FEAT-010`) fixed | eval 8 ↑; evals 1, 9, 16, 17 rewritten to stop rewarding invented IDs |
| create-user-story | AC-variants rule now reachable; shared-Functionality clause on the split anti-pattern; eval 14 like create-functionality's; eval 1's never-firing conditional replaced | small ↑ |
| gherkin-step | Removed behave decorator hooks and playwright-bdd `async ({ fixture })` examples that contradicted the skill's own scope note | evals 9, 11, 12, 13 corrected to the skill's (right) Cucumber pattern — the two "drops" disappear |
| data-cy-instrument | No made-up issue URL/version in the WORK_LOG example; project-specific paths (`aul-ui/…`, `BD_CTX_API`) generalised; Phase 6 routes promotion through `living-doc-update` first; planted "if asked React/Vue, say X" line removed | eval 8 now rewards placeholders; eval 7 now tests substance — may drop slightly where an answer only recites |
| gherkin-living-doc-sync | Names `STALE_AC_REF`; proposes AC mappings only when a catalog is available; eval 10 (scan_ac_links) matched to the script's real findings and flags | evals 1, 3, 4, 10 stop rewarding invented paths/IDs |
| gap-finder | Shared path prefix is not ownership (`/account/preferences` contradiction); taxonomy table now names the codes; eval 1 matched to its snapshot (it cited FEAT-005/008, which do not exist) | eval 1 ↑ for correct answers |
| bdd-maintain | Script scope documented truthfully (fixtures.ts + PageObject files are scanned); eval 5 now tests the real false-positive causes; eval 10's unfalsifiable assertion replaced | eval 5 discriminates now |
| All 15 command-line skill scripts | Crashed with exit 1 (= "findings") when an agent piped their output on Windows — on their own ✅/⚠️ markers, and on any non-ASCII user data (a Czech entity name crashed `validate_entity.py`); now write UTF-8 | not visible in evals; guard test runs both cases under a cp1252 pipe |
| Eval tooling | Portable paths, UTF-8 I/O, Windows trigger wrapper, multi-run support, `prepare_iteration.py`, triggers run from an empty project | iteration 3 needs 474 Haiku runs, not 948 |
| pageobject-scan | MCP pre-flight now gates only runs against the live app; questions and example answers are answered from the supplied details (it hard-stopped on conceptual questions — eval 9 lost 0 vs 5). Header migration no longer sits behind the MCP check. RE-SCAN rows say what they mean (a renamed test id is *Missing* → BREAKING CHANGE). Python example follows the skill's own `get_by_test_id` rule. STUB rationale from canon | evals 4, 9, 11 ↑; eval 8 corrected to the locator rule; evals 3, 4, 16 stop rewarding invented step text or script runs; eval 6 labelled `requires: mcp-playwright` |
| impact-analysis | Provenance rule no longer contradicted (`:261`); unknown ids stay visible placeholders, never `FEAT-cart`-style slugs; pattern note covers bare-file-name matching (`trace_impact.py:182`) | evals 1, 8, 13 stop requiring a registry lookup with no catalog; eval 15 corrected to `catalog.json` (was `feature_registry.json`) |
| scenario-creator | Removed the eval-fitted `CheckoutPage → FEAT-003` hard-code; facts the prompt states are used, not refused (evals 16, 19 regressed by over-refusal); `in_review` counted as the script does; coverage template marked as a summary, not script output, plus zero-padding note; regression rule allows one scenario per declared value; output-format rule allows the Entity header block | evals 16, 19 ↑; evals 3, 4, 8, 10, 11, 14, 15, 19, 23 corrected; eval 6 labelled `requires: project-fixture` |
| living-doc-update | Change-summary examples no longer carry concrete values answers copied as supplied (`AC:US-042-04`, `422`, `SHIPPING_ZONE_EXCLUDED` — the first was eval 1's own scenario); unsupplied values stay placeholders or labelled proposals; AC-variants pointer; `FEATURE_WITHOUT_USER_STORY` reason corrected (`compute_gaps.py:183`); Feature creation is a hand-off to `living-doc-create-feature` | eval 1 ↑; evals 2, 4, 8, 16, 17 corrected (no invented entity data, error codes or `feature_registry.json`) |
| Entity IDs (owner decision 2026-10-13) | An entity's ID never changes — not on a rename, not after it is retired, not in history. `living-doc-update` "Rename a Feature" is now name-only, with a new "Split or merge a Feature" workflow (new Features, re-parent, `superseded_by`); create-feature, impact-analysis and gap-finder aligned. Canon rule still to introduce — `specs/debt.md` D57 | create-feature eval 15 and living-doc-update eval 16 rewritten to the rule (both previously expected an ID cascade or contradicted the skill) |
| `@living-doc-bdd-copilot` | "Load one skill per session" no longer contradicts the three-skill deprecation chain; a variant AC stays one AC (the agent showed only the `aspect` tag and said "atomic ACs only", so eval 26 split one requirement into three ACs in both arms) | eval 26 ↑; 11 environment-blocked evals labelled `requires`; two assertions rewarded `known_routes`, a key `seed.schema.json` does not have |
| bdd-maintain (via the agent's grading) | REMOVE procedure deleted scenarios, steps and PageObjects before asking the user to confirm the list — now two confirmation gates, before any file is touched | guard test added |
| impact-analysis (via the agent's grading) | No longer tells the model to infer scenario titles (its example carried an invented "422"); scenarios are identified by their `@AC:` tag | eval 15 of the agent stops copying it |

Skipped on purpose:
- create-feature `SKILL.md:192` — the grader said the duplicate-name row was missing; it exists.
- bdd-maintain `SKILL.md:126-132` barrel re-export — unverified, not confirmed.
- Minor, low risk: data-cy shadow-DOM wording, gherkin-living-doc-sync `@AC:` consumers, the
  create-user-story vague-outcome warning, gherkin-step evals `:131` / `:219`, create-feature evals
  `:190` / `:217` (suspect only).

### Iteration-2 grading of the five targets graded in this session (Opus 5.5)

| Target | with_skill | old_skill | Below baseline | Verdict |
|---|---|---|---|---|
| pageobject-scan | 60/85 | 61/85 | evals 6, 8, 9 | genuine — the MCP pre-flight over-reached (eval 9: 0 vs 5); fixed |
| impact-analysis | 57/65 | 60/65 | evals 10, 11, 16 | 10/11 are format misses in "Required changes" despite `SKILL.md:246-247` (single run, cause unverified); 16 minor |
| scenario-creator | 88/106 | 81/106 | evals 16, 19 | genuine over-refusal; fixed |
| living-doc-update | 69/78 | 70/78 | eval 8 | not a regression — the assertion asked for an error code the prompt never mentions; fixed |
| `@living-doc-bdd-copilot` | 63/133 | 61/133 | evals 3, 13, 19 | 3: over-refusal (covered by the scenario-creator fix); 13 minor; 19 labelling only |

The agent's low absolute score is mostly the eval set: 11 evals (1, 2, 4, 5, 7, 8, 14, 16, 18, 19, 23) hard-stop
identically in both arms for want of an MCP Playwright server or project files — now labelled `requires` — and 50
assertions can only pass on invented data because every agent eval has `files: []`. Eval 25 is not blocked: both
arms correctly route unit tests away.

Not acted on: impact-analysis eval-mirroring text (`SKILL.md:120-124`, `:206`, `:222-226` — saturation, known gap); the
impact-analysis and scenario-creator `evals/fixture-map.md` files are stale (authors' notes only — runners never read them);
pageobject-scan's Python header format vs the schema's ` * ` marker is UNVERIFIED (needs the collector's header parser);
scenario-creator eval 21's ordering assertion is vacuous with one AC.


## 4. Known gaps — for `baseline.md` § "what the suite does not test"

- **create-functionality trigger recall is not a trustworthy production signal.** Positives: Mac
  5/19, here 1/19, and the queries that passed differ between runs. Diagnosis: Haiku reads a
  context-free *"Create a functionality for X"* as a coding request ("I'll help you create cart
  validation functionality") and starts exploring; *"…functionality **entity**…"* loads the skill.
  A front-loaded rewrite of the description changed nothing (1/19), so the description was kept. In
  a living-doc project the surrounding context should steer it; the eval measures the cold case.
- **The iteration-2 trigger figures were measured in a contaminated environment.** `run_eval.py`
  ran with the user's home folder as the project, and a run spent its first tool call reading the
  home project's `MEMORY.md` — scored as a miss. `run_triggers.sh` now runs from an empty project
  outside any repository, so iteration-3 trigger figures start a new series.
- **Saturation.** data-cy-instrument and bdd-maintain score near 100% in both arms; most of those
  evals are satisfied by restating the skill. They still guard against a regression, but cannot
  show an improvement. Three evals were made discriminating (bdd-maintain 5, 10; data-cy 7).
- **`@living-doc-bdd-copilot`'s main path is untested.** Evals that need a live MCP Playwright
  server or project files hard-stop identically in both arms — see § 3 for the confirmed list.
- **One measured run per arm** in iteration 2; iteration 3 runs the measured arm twice.
- **No fixture for most "show me the output of" evals**, so a schema-shaped example passes.
