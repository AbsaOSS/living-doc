# `.claude/` helper set

Productivity helpers for roadmap/spec-driven work in `living-doc`. Copied and adapted from
the ecosystem reference copy in `living-doc-toolkit/.claude/` (the repo-specific parts here
are the lack of any `make`/package vocabulary, the mock/fixture table for the examples
corpus, and the doc-guide contract paths).

These helpers are **acceleration, not dependency**. Every task they describe can be done by
hand, just slower. Nothing in CI or the release path requires them.

## What's here

| File | Kind | Purpose |
|---|---|---|
| `commands/implement-task.md` | slash command | Drive one roadmap task from its spec to a PR-ready description. |
| `commands/verify-pr-ready.md` | slash command | Verify-only gate: is this branch PR-ready? one yes/no. |
| `agents/test-author.md` | subagent | Write deterministic pytest tests using this repo's real mock/fixture surface. |

`settings.json` is not listed here — it carries local owner configuration and is untouched
by this set.

**Not carried over from `living-doc-toolkit/.claude/`:** `rules/docs-lifecycle.md`. That
rule moves an implemented `SPEC.md` section into the live docs; this repo has no `SPEC.md`
— its planning docs are local and gitignored (see `.gitignore`), never reaching a PR, so
there is nothing for that rule to move. See the audit note in
`.github/copilot-review-rules.md`.

## How the two commands relate

Both check **acceptance criteria against the actual file** — reading the guide's literal
field description, the rule in `tools/examples_check.py`, the example file's literal
content — never "a test with that name is green".

- **`/implement-task <id>`** is the full lifecycle: read the task → read every referenced
  file → implement → run `python tools/examples_check.py` / `python -m pytest
  tools/test_examples_check.py -q` until green → verify each acceptance criterion against
  code/docs → write the `## Overview` / `## Release Notes` / `## Related` PR description →
  stop. It collapses the `specification-master` → `senior-developer` → `sdet` →
  `reviewer` agent sequence into one driven command.

- **`/verify-pr-ready <id>`** is the lighter companion for right before opening a PR —
  useful when a human did most of the implementation. It re-checks every acceptance
  criterion against code/docs, runs the same checks, runs the `reviewer` agent, and
  outputs a single `PR-READY: yes/no` with a specific fix list when the answer is no. It
  does not implement anything.

Typical flow: `/implement-task` to build it, then `/verify-pr-ready` as the final gate
before opening the PR.

## Relationship to `.github/agents/`

The `.github/agents/` board (`specification-master`, `senior-developer`, `sdet`,
`reviewer`, `devops-engineer`) stays the source of truth for role behavior. `test-author`
here is `sdet` plus the concrete repo mock table; `/verify-pr-ready` invokes `reviewer`.

The concrete mock/fixture cheat-table that drives test implementation lives in
`agents/test-author.md` — this is the single source of truth for which boundary to
isolate and how, updated whenever a rule or fixture changes.
