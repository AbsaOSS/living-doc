---
description: Verify a branch is PR-ready — acceptance criteria checked against code/docs, checks green, reviewer pass. Outputs one yes/no.
argument-hint: <task-id> (e.g. P35-LD2a1) [path-or-URL to the task list, if not the default]
---

You are the final gate before a PR is opened. This is the **verify-only** companion to
`/implement-task` — assume a human (or a prior run) did most of the implementation and you
are applying the same rigor as a last check. Do not implement features here; only verify,
and list fixes if it is not ready.

Task ID: `$1`
Task-list source (optional override): `$2`

## 1. Re-check every acceptance criterion against code/docs

- Read task `$1`'s acceptance criteria from the provided task list (or `$2`).
- For each criterion, confirm the **literal claim** against the file that currently exists
  on this branch — the guide's field description, the rule in `tools/examples_check.py`,
  the example file's literal content, the `docs/examples/_expected/*.json` diff. **Do not**
  accept "a test with that name passes" as evidence.
- Produce a table: criterion → met / not met → the `file:line` that proves it (or the gap).

## 2. Run the checks

- `python tools/examples_check.py` and `python -m pytest tools/test_examples_check.py -q`
  if `docs/examples/**` or `tools/*` changed.
- Confirm `docs/examples/_expected/**` is regenerated and diffs clean if the branch changed
  anything `.github/workflows/real-collector-snapshot.yml` mines from.
- There is no `make qa`, lint, type-check, or coverage gate in this repo — do not report one
  as missing.
- Any red check ⇒ not PR-ready.

## 3. Run the reviewer agent

- Run the `reviewer` agent (`.github/agents/reviewer.agent.md`) over the branch diff,
  following `.github/copilot-review-rules.md`.
- Fold its Blocker / Important findings into the verdict. Nits are noted, not blocking.

## 4. Output a single verdict

Print exactly one of:

- `PR-READY: yes` — all acceptance criteria met against code/docs, checks green, no
  reviewer blockers. Follow with the criterion→`file:line` table.
- `PR-READY: no` — followed by a specific, ordered fix list: each item names the failing
  criterion or check, the `file:line`, and the concrete change needed.

Do not open the PR, push, or commit.
