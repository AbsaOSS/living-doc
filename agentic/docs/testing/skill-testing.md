# Skill Testing Guide

> For running a whole suite — arms and models, the harness behaviours that silently
> produce wrong numbers, grading discipline and what a run must deliver — see
> [eval-protocol.md](eval-protocol.md). The recorded comparison point is
> [baseline.md](baseline.md).

This document provides a comprehensive methodology for testing, evaluating, and optimizing the skills of the agentic layer in `agentic/`. It covers eval creation, fixture management, iterative improvement, trigger testing, and description optimization.

> **What CI runs and what it does not.** `.github/workflows/agentic-tests.yml` runs the layer's
> Python script tests (`agentic/skills/**/test_*.py`, on Python 3.10 and 3.14), checks that the
> canon copies match this commit's `docs/`, and validates each `SKILL.md` folder's format. **It
> runs no eval.** Every loop below is manual: you run it yourself, and the eval files are its
> source material, not a CI suite. Nothing in this repository executes them.
>
> See [agentic/CONTRIBUTING.md](../../CONTRIBUTING.md) for the local commands and the checklist
> for a pull request that changes a skill.

---

## 1. Recommended workflow

What you need: an agent harness that can load a skill from a folder and run a prompt against it, with and without that skill enabled. The commands below are written for a Copilot CLI or Chat session driving Anthropic's [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) skill, which is what this layer was developed with; any harness with the same two abilities works, and `skill-creator` is not vendored here.

0. See what already exists: `python agentic/scripts/evals-inventory.py <skill-name>`
1. Create eval cases in `agentic/skills/<skill-name>/evals/evals.json`
2. Add fixture files under `agentic/skills/<skill-name>/evals/files/` when prompts depend on local files
3. Start a session from the repository root
4. Ask it to use the `skill-creator` skill to test the target skill
5. Review outputs and diffs
6. Improve the skill description or body
7. Re-run targeted evals, then the full suite
8. Repeat until regressions are stable and output quality is consistently better

## 2. Eval Cases

Store evals in `agentic/skills/<skill-name>/evals/evals.json`:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": "happy-path-1",
      "prompt": "A realistic prompt a real user would type, with concrete detail",
      "expected_output": "Short description of what a successful result should do",
      "files": []
    }
  ]
}
```

Write prompts that look like real user requests, not abstract test descriptions. Include a mix of happy-path, regression, output-format, edge, negative, and paraphrased cases.

## 3. Fixtures

If the skill operates on files, place sample inputs in `agentic/skills/<skill-name>/evals/files/` and reference those files from the eval entries. Use small, representative fixtures.

## 4. With/Without Skill Comparisons

Ask for a side-by-side comparison in the Copilot CLI session:

```
Use the skill-creator skill to compare outputs for agentic/skills/my-skill with and without the skill enabled.
Compare on: correctness, structure adherence, completeness, and output verbosity.
Only fix the smallest part of the skill that explains the largest failure cluster. Repeat until all evals pass.
```

Compare correctness, completeness, structure, latency, verbosity, and formatting stability.

## 5. Reviewing Outputs and Diffs

Review changed outputs and fixture diffs. Classify each change as improvement, acceptable variation, regression, or unclear. Avoid making fixtures so strict that harmless wording improvements fail the test.

## 6. Iterative Improvement

When an eval fails, update the smallest possible part of the skill and re-run the affected cases first. Avoid large rewrites unless the skill is fundamentally mis-scoped.

## 7. Regression-First Loop

1. Run the full eval suite and save the baseline
2. Pick the largest failure cluster
3. Make one small edit to the skill
4. Re-run only affected evals and regressions
5. Review output diffs
6. Run the full suite again
7. Keep or revert the change
8. Repeat until stable

## 8. Body vs. Trigger Testing

- **Body testing:** Use `evals/evals.json` to verify that once the skill is active, it behaves correctly.
- **Trigger testing:** Create `agentic/skills/<skill-name>/evals/trigger-eval.json` to test whether the skill activates for the right queries.

The two files have different shapes. `evals.json` is an object (`skill_name` plus an `evals` array, as in section 2); a trigger eval file is a **bare array** of queries, each with the answer you expect from the matcher:

```json
[
  {
    "id": "t01-update-us-explicit",
    "query": "Update User Story US-042 to add a new AC.",
    "should_trigger": true,
    "reason": "'update user story' is a listed trigger phrase."
  },
  {
    "id": "t09-unit-test-request",
    "query": "Write a unit test for the price calculator.",
    "should_trigger": false,
    "reason": "Unit tests are outside this skill's NOT for: boundary."
  }
]
```

Include negative cases (`should_trigger: false`) for adjacent-but-out-of-scope requests, not only positives — a description that fires on everything passes a positives-only set.

## 9. Description Optimization

Ask Copilot to optimize the description against your trigger eval set:

```
Use the skill-creator skill to optimize the description for agentic/skills/my-skill
using agentic/skills/my-skill/evals/trigger-eval.json.
Keep minimalist (≤ 1024 chars); structured domain nouns/verbs preferred over explicit keyword lists.
Include a NOT for: boundary clause. Report precision and recall per candidate. Repeat until all evals pass.
```

A good description uses structured domain nouns and a `NOT for:` boundary. An explicit keyword list is not required.

## 10. What “good enough” looks like

- All smoke tests and known regressions passing
- No critical format failures
- Positive or neutral delta versus baseline
- Stable behavior across paraphrases
- Strong trigger accuracy on both train and validation queries

## 11. Practical Tips

- Use realistic prompts with concrete nouns, filenames, and intent
- Prefer several focused evals over one large vague eval
- Keep fixtures small and scenario-specific
- Update fixtures only after confirming the new behavior is actually better
- Do not optimize solely for exact string matches
- If a change improves one eval but harms unrelated ones, revert it

## 12. Minimal CLI Loop

```
VS Code Copilot Chat (or gh copilot):
→ "Use the skill-creator skill to test my skill at agentic/skills/my-skill.
   Run all evals and report pass rate and baseline delta."
→ inspect results and diffs — classify each change as improvement, regression, or neutral
→ edit SKILL.md or fixtures (smallest change that fixes the largest failure cluster)
→ "Use the skill-creator skill to rerun the evals for agentic/skills/my-skill."
→ "Use the skill-creator skill to optimize the description for agentic/skills/my-skill
   using agentic/skills/my-skill/evals/trigger-eval.json.
   Keep ≤ 1024 chars; include a NOT for: boundary clause. Repeat until all evals pass."
→ repeat until stable
```

---

For more on evals, see [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) and the `skill-creator` skill documentation.
