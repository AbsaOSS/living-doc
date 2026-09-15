---
description: Implement a roadmap task end to end, from its spec to a PR-ready description.
argument-hint: <task-id> (e.g. P35-LD2a1) [path-or-URL to the task list, if not the default]
---

You are driving a single roadmap task to completion in `living-doc`.
Follow these steps **in this exact order**. Do not skip or reorder them.

Task ID: `$1`
Task-list source (optional override): `$2`

## 1. Read the task

- Locate task `$1` in the current Phase task list found for this repo (local, gitignored
  planning — see `.gitignore`). If `$2` is given, read it there instead.
- Read the task's **prompt** and its **acceptance criteria** in full. Also read the linked
  GitHub issue if the task names one.
- Write the acceptance criteria out as a numbered checklist you will verify against code /
  docs in step 5. Do not start work until this list is explicit.

## 2. Read every file the task references — before writing any code or docs

- Open every spec, doc, config, and source file named in the task prompt, its "Spec refs"
  line, and its acceptance criteria. Follow one hop of cross-references.
- Read the guides the change touches (`docs/guides/living-doc-header-types.md`,
  `living-doc-document-types.md`, `living-doc-glossary.md`) and `.github/copilot-review-rules.md`,
  so the change matches this repo's format contracts and review expectations.
- If the task touches the example corpus, read `docs/examples/README.md` § "Sync
  obligation" — a format change and its matching `docs/examples/**` update belong in the
  same PR.
- If the task is ambiguous after reading, stop and ask — do not guess.

## 3. Implement to the spec exactly

- Make the smallest change that satisfies the spec. Match existing structure and naming;
  there is no monorepo and no package-dependency rule to respect.
- If the task changes `tools/examples_check.py`, add the matching mutation test in
  `tools/test_examples_check.py` using the `corpus_dir` fixture — use the `test-author`
  agent for the test surface.
- Do not change the format contracts (`docs/guides/living-doc-header-types.md` fields, the
  `AC:<id> (v<version> - <state>)` / `@AC:<id>[/aspect:<value>]` grammar,
  `docs/examples/_expected/**` structure) unless the task explicitly calls for it.
- If the change moves what `docs/examples/**` mines to, or bumps a pin in
  `tools/collector-snapshot-pins.env`, regenerate `docs/examples/_expected/*.json` in this
  same PR per `CONTRIBUTING.md` § "Regenerating the collector snapshots".

## 4. Run the checks until green

- `python tools/examples_check.py` (only if `docs/examples/**`, `docs/guides/**`, or the
  checker changed).
- `python -m pytest tools/test_examples_check.py -q` (only if the checker or its tests
  changed) — the same command `.github/workflows/examples-check.yml` runs.
- There is no `make qa`, no lint, no type-check, and no coverage-percentage gate in this
  repo — do not invent one.
- Fix every failure and re-run. Do not weaken a check to get past a gate.

## 5. Verify each acceptance criterion against the actual code / docs

For every criterion on your step 1 checklist, confirm the **literal claim** by reading the
file that now exists — **not** by checking that a same-named test is green.

- "a rule rejects X" → read the rule in `tools/examples_check.py` and confirm it actually
  produces a `Finding` for X.
- "the guide documents field Y" → open the guide and read the literal field description.
- "the example shows extension Z" → open the example file and confirm Z is literally
  present, and confirm it is the corpus's one instance of that extension (see
  `docs/examples/README.md` "Conventions used by this corpus").
- "the snapshot reflects the change" → confirm `docs/examples/_expected/*.json` was
  regenerated and diffs clean against a fresh `tools/regen-collector-snapshots.sh` run.

Record each criterion as met (with the `file:line` that proves it) or not met. If any
criterion is not met, return to step 3.

## 6. Write the PR description

Write a PR description (to `pr.md` in the repo root unless told otherwise) with exactly
these sections, per `CONTRIBUTING.md`:

- `## Overview` — what changed and why.
- `## Release Notes` — at least one real user-facing bullet (no `TBD`).
- `## Related` — `Closes #<issue>` for the task's issue.

Include a short "Acceptance criteria" checklist mapping each criterion to the `file:line`
that satisfies it (from step 5). Do not stage or commit the local planning directory — it
is gitignored and must never appear in the PR.

## 7. Stop

Do not open the PR, push, or commit. Report: what changed, the check results, and the
acceptance-criteria verification table. Then stop.
