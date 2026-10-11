# Pull Request

## Overview

The agentic layer — the skills and the `living-doc-bdd-copilot` agent that help an author write living-doc
input — moves out of `AbsaOSS/agentic-toolkit` into this repository, under one top-level folder, `agentic/`.
The canon and the skills that write it now live in one repo and ship in one release, and every further canon
change to the layer is made once, here.

The move takes the head of `AbsaOSS/agentic-toolkit#40` (`docs/39-align-living-doc-canon`, `5d356b3`), so its
30 commits of canon alignment are kept. `#40` ends there.

**What moved** (109 files, copied unchanged in the first commit): the nine living-doc skills, the three BDD
skills the agent uses (`data-cy-instrument`, `gherkin-step`, `bdd-maintain`), `skills/shared`, the
`living-doc-bdd-copilot` agent with its evals, 13 skill guides, the two testing guides, the test workflow and
the sync script. The 12 skills and 9 guides that are not about living-doc stay at the source.

**What this PR then does to it:**

- **The canon copies are generated here, not fetched.** `agentic/scripts/sync-canon-copies.sh` lost its `curl`,
  its ref argument and its commit pin: it reads this working tree's `docs/`, so the copies always match the
  commit they are committed in. CI regenerates them and fails on any difference, which is what makes drift
  impossible — the copies used to pin `living-doc@86c756d` and had fallen behind.
- **The copies stay where the skills read them**, because `npx skills add` copies only a skill's folder and
  `shared`'s into a user's project, where this repository's `docs/` does not exist.
- **CI** (`.github/workflows/agentic-tests.yml`) runs the 13 script tests on a Python **3.10 / 3.14 matrix**,
  checks the canon copies, and validates every `SKILL.md` folder's format in its own job.
- **The layer's testing method is adopted, not left behind.** Both testing guides move under
  `agentic/docs/testing/` with every path repointed, and the layer gets its own `agentic/CONTRIBUTING.md` with
  the local test commands and a PR checklist. `agentic/` is a subproject: its pages sit beside the canon
  rather than inside `docs/`, and the root `README.md` and `CONTRIBUTING.md` only point into it.
- **Formats the layer owns** — the Project Profile, `seed.yaml`, `manifest.json` and the skill matrix — are
  collected in `agentic/skills/shared/references/agentic-formats.md`, inside `shared` so an installed skill
  still gets them.

### Acceptance criteria

| Criterion | Where | Status |
|---|---|---|
| The skills, agent, evals, scripts, 13 guides and 2 testing guides are under `agentic/`; nothing outside it | `agentic/` — 109 files in `c6dbcc7`; the test workflow is the only file outside, at `.github/workflows/agentic-tests.yml` | ✅ |
| The first commit is the copy and nothing else, byte-equal to the source, naming it | `c6dbcc7` — verification output below | ✅ |
| Canon copies byte-equal to the script's output from the same commit's `docs/`; no SHA pin, no fetch | `agentic/scripts/sync-canon-copies.sh:47` (TARGETS), `:135` (reads `${REPO_ROOT}/<page>`), no `curl` anywhere in the file; CI job `canon-sync-check` | ✅ |
| CI fails on a hand edit of a copy, and on a canon change without regenerated copies | `agentic-tests.yml:49` (job), `:61-71` (the diff check), `:20-33` (the two canon pages in `paths:`) — both demonstrated below | ⬜ runs to be linked |
| The 13 tests run in CI and pass; skill-format validation passes; link check green | `agentic-tests.yml:75` (`script-tests`), `:137` (`skill-lint`); results below | ✅ |
| Testing guides under `agentic/`, paths inside `agentic/`, numbering consecutive, CI-vs-manual stated | `agentic/docs/testing/skill-testing.md:5`, `agent-testing.md:5`; `agent-testing.md` sections 1–7 | ✅ |
| `agentic/CONTRIBUTING.md` holds the process; root `CONTRIBUTING.md` points at it and repeats none of it | `agentic/CONTRIBUTING.md`, `CONTRIBUTING.md:61-68` | ✅ |
| `agentic/README.md` gives working install commands and says the copies are generated | `agentic/README.md:11` (Install), `:60` (Reference documents), `:77` (Testing and contributing) | ✅ |
| The `#40` checks hold on the moved files | output below | ✅ |
| `README.md` links `agentic/` | `README.md:72` | ✅ |
| Project Profile, `seed.yaml`, `manifest.json` and the skill matrix live under `agentic/` and in no reference page | `agentic/skills/shared/references/agentic-formats.md` | 🔶 the canon page keeps them until the reference-docs rework merges, so nothing breaks on `master`; whichever merges second cuts them |
| `agentic-toolkit#40` closed with a pointer | — | ⬜ |

### The copy, verified against its source

```
$ SRC=5d356b3
$ D=$(mktemp -d)
$ git -C ../agentic-toolkit archive "$SRC" skills .github/agents docs/guides docs/testing scripts | tar -x -C "$D"
$ diff -r "$D/skills" agentic/skills
Only in .../skills: create-issue
Only in .../skills: create-repository
Only in .../skills: create-repository-workspace
Only in .../skills: pr-review
Only in .../skills: python-standards
Only in .../skills: tdd-workflow
Only in .../skills: test-data-management
Only in .../skills: test-mocking-patterns
Only in .../skills: test-unit-review
Only in .../skills: test-unit-standards
Only in .../skills: test-unit-write
Only in .../skills: token-saving

$ diff -r "$D/docs/guides" agentic/docs/guides
Only in .../docs/guides: agent-design.md
Only in .../docs/guides: pr-review.md
Only in .../docs/guides: tdd-workflow.md
Only in .../docs/guides: test-data-management.md
Only in .../docs/guides: test-mocking-patterns.md
Only in .../docs/guides: test-unit-review.md
Only in .../docs/guides: test-unit-standards.md
Only in .../docs/guides: test-unit-write.md
Only in .../docs/guides: token-saving.md

$ diff -r "$D/docs/testing" agentic/docs/testing      # no output
$ git show --name-only --format= c6dbcc7 | wc -l
109
```

Every difference is a file that stays at the source: the 12 skills and 9 guides that are not about living-doc.
The agent, its evals, both testing guides, the sync script and the test workflow are byte-equal. Run the three
`diff`s against `c6dbcc7`, not the branch tip — the later commit changes the copied files on purpose.

### The `#40` checks, now here

```
$ grep -rn "future_release" agentic | grep -v CONTRIBUTING.md
(no hits)

$ grep -rnE 'status:\s*descoped|"descoped"' agentic
(no hits — every mention of descoping states that there is no `descoped` state and the AC
 drops back to `planned`)

$ grep -rn "pageobject_statuses" agentic
agentic/skills/shared/references/schemas/project-profile.schema.json:14:    "required": ["pageobject_statuses"]
agentic/skills/shared/references/schemas/test_project_profile_schema.py:70:def test_pageobject_statuses_key_rejected():
(the schema line sits inside `"not": { "required": [...] }` — it forbids the key; the test
 asserts the rejection. Both are the documented exceptions.)

$ grep -rnE '[A-Za-z0-9](–|—)[A-Za-z0-9]' agentic
(only numeric ranges and prose: "30–45 min", "Steps 1–2", "sources A–E", "Features—smaller".
 No dash inside an id, key or state value. The one structural format that carries an em dash,
 `LIVING DOC — FEAT-<nnn> · <name>`, matches the canon exactly:
 docs/guides/living-doc-header-types.md:310 and docs/examples/pageobject/LoginPage.ts:2.)

$ grep -n "stub-reason" agentic/skills/data-cy-instrument/SKILL.md
207:- Remove the `stub-reason:` line if no un-instrumented elements remain — a PageObject header
     carries no `status:` field to flip; the surface is instrumented once `stub-reason:` is gone.

$ grep -rn "status" agentic | grep -i feature     # no Feature status is ever produced
(every hit states the opposite: "FEAT-003 never gets a status field — a Feature's state is
 derived from its Functionalities, never authored")
```

### Test, lint and link results

| Check | Result |
|---|---|
| `Script tests (Python 3.10)` | pass |
| `Script tests (Python 3.14)` | pass |
| `Canon copies match this commit's docs/` | pass |
| `Skill format validation` | pass — 13/13 skill folders |
| `Markdown Link Check` | pass — lychee with `--include-fragments`, 275/275 OK |
| `Examples check` | pass |

Three findings came out of running these rather than assuming them:

1. **The skill-format validator is called `agentskills`, not `skills-ref`.** The `skills-ref` package installs
   exactly one console script, `agentskills` (`skills_ref.cli:main`). The instruction inherited from the
   source's `CONTRIBUTING.md` §6 named a `skills-ref` executable that does not exist; the CI job and
   `agentic/CONTRIBUTING.md` use the real command, and `agentic/requirements-skill-lint.txt` records why.
2. **Four anchors had rotted** against the copy pinned at `86c756d` and only showed up once the copies were
   regenerated from today's canon (`#pageobject-file-header`, `#us-feature-file-header`,
   `#functionality-feature-file-header`, `#form_fixtures-…-how-the-agent-resolves-…`). Fixed; `form_fixtures`
   now points at `agentic-formats.md`, the header formats at the current canon anchors.
3. **The agent's 12 skill-dispatch paths** were repo-root paths from the source (`skills/<name>/SKILL.md`), so
   nothing resolved after the move and no link checker could see it — they are code spans, not links. Prefixed
   and verified.

`[remote]` links in the skill headers point at the **canon pages** under `docs/guides/`, not at the generated
copies: the copies do not exist on `master` until this merges, and the canon page is the source of truth anyway.

### Python versions

The script tests run on **3.10 and 3.14**. 3.10 is the floor `living-doc-utilities` declares
(`requires-python = ">=3.10"`) and a skill's scripts run under whatever interpreter the user's project has, so
the floor is what protects them; 3.14 is what every other workflow here uses. All 30 `.py` files compile under
3.10 and nothing in them needs anything newer.

`agentskills` requires Python ≥ 3.11, so skill-format validation runs in its own 3.14 job and its
requirements are pinned in a separate file — installing it into the 3.10 leg would fail. It is maintainer
tooling and does not raise the layer's floor.

### Notes for the reviewer

- **The tests are not pytest tests.** Each carries `__test__ = False`, asserts in plain functions and exits
  from its own `__main__` block, so a bare `pytest` collects none of them and reports success. CI discovers and
  runs each one; `agentic/CONTRIBUTING.md` says so where the local command is documented. Converting them was
  considered and rejected: it would touch 13 copied files for no new coverage.
- **Two canon lines changed.** `docs/guides/living-doc-glossary.md:7` and
  `docs/guides/living-doc-header-types.md:10` said the copy is synced from `agentic-toolkit`. They describe the
  mechanism this PR replaced, and the text ships inside the generated copies, so they now name the script and
  the CI check. The other stale `agentic-toolkit` mentions in `docs/` are left for the documentation sweep.
- **`agentic-formats.md` duplicates the canon page** for now, by design: the sections leave the reference page
  only when the reference-docs rework merges, so no link breaks on `master` in the meantime.

## Release Notes

- The living-doc skills and the `living-doc-bdd-copilot` agent now ship from this repository, under `agentic/`.
  Install them from `AbsaOSS/living-doc` instead of `AbsaOSS/agentic-toolkit`:
  `npx skills add https://github.com/AbsaOSS/living-doc -g --skill <skill>` plus `--skill shared`.
- The canon references the skills read are generated from this repository's `docs/` at the same commit and
  checked by CI, so they can no longer drift from the canon.
- The layer carries its own contributor and testing documentation: `agentic/README.md`,
  `agentic/CONTRIBUTING.md` and the guides under `agentic/docs/testing/`.

## Framework

- [x] Stays inside the frame (F1–F7)
- [ ] Bends frame row F_ — exception E_ added to `docs/introduction/principles.md` in this PR

F6 Agentic is where this layer belongs: it accelerates authoring of entity headers and the BDD tests bound to
them, and the pipeline (F2–F4) runs AI-free without it. Nothing in the pipeline reads anything this layer
writes beyond the entity headers F1 already defines.

## Related

Closes #52
