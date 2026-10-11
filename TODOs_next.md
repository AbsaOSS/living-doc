# TODOs — finishing the agentic-layer issue (#52)

Everything that still needs **your** hands. The file work is done and verified locally; what is
left is git, the PR, and the two CI demonstrations the acceptance criteria ask to be *shown* in
the pull request.

Branch: `feature/52-agentic-layer` · copy commit: `c6dbcc7` (not pushed) · 38 paths in the working
tree (33 modified, 5 new).

---

## 1. Amend the copy commit's message

`c6dbcc7` holds the right 109 files but its message is auto-generated and does not name the source
commit, which one acceptance criterion requires. It is not pushed, so the amend is safe.

```bash
git commit --amend -m "agentic: copy the living-doc layer from agentic-toolkit@5d356b3

109 files, unchanged, from origin/docs/39-align-living-doc-canon (PR #40)."
```

## 2. Commit the rewiring, one part per commit

The acceptance criterion is that every change to the copied files sits in its own later commit, so
a reviewer can read the change without reading the 109 copied files. Suggested split and messages:

**A — canon copies generated here, and every link repointed** (26 paths)

```bash
git add agentic/scripts/sync-canon-copies.sh \
        agentic/skills/shared/references/living-doc-glossary.md \
        agentic/skills/shared/references/living-doc-bdd-schemas.md \
        agentic/skills/shared/references/schemas/ \
        agentic/skills/shared/SKILL.md agentic/skills/shared/lib/README.md \
        agentic/skills/*/SKILL.md agentic/skills/*/scripts/*.py \
        agentic/agents/living-doc-bdd-copilot.agent.md \
        agentic/docs/guides/living-doc-bdd-copilot.md
git commit -m "agentic: generate the canon copies here and repoint every link"
```

Covers: the sync script loses its fetch, its ref argument and its SHA pin and reads the working
tree; both copies regenerated from today's canon; 45 `AbsaOSS/agentic-toolkit` URLs repointed; the
agent's 12 skill-dispatch paths and 4 reference paths prefixed with `agentic/`; 4 anchors that had
rotted against the old pinned copy fixed.

**B — CI**

```bash
git add .github/workflows/agentic-tests.yml agentic/requirements-agentic-tests.txt agentic/requirements-skill-lint.txt
git commit -m "agentic: CI — script tests on 3.10/3.14, canon-copy check, skill-format lint"
```

**C — the layer's formats page**

```bash
git add agentic/skills/shared/references/agentic-formats.md
git commit -m "agentic: add agentic-formats.md — the formats the layer owns"
```

Note: `agentic-formats.md` is also referenced by commit A (the schemas and
`living-doc-pageobject-scan/SKILL.md` point at it, and the bdd-schemas addendum links it). If you
would rather not have A reference a file that arrives in C, commit C first.

**D — testing documentation and the layer's process**

```bash
git add agentic/docs/testing/ agentic/CONTRIBUTING.md agentic/README.md
git commit -m "agentic: adopt the testing guides and the layer's contributor process"
```

**E — root pages, and the two canon lines the move made false** (4 paths)

```bash
git add README.md CONTRIBUTING.md docs/guides/living-doc-glossary.md docs/guides/living-doc-header-types.md
git commit -m "agentic: point the root pages at agentic/, fix the two copy-mechanism lines"
```

The five groups cover all 38 paths with no overlap: 26 + 3 + 1 + 4 + 4. After the last commit
`git status` should be clean apart from this file.

⚠️ **Decide on the two `docs/guides/` lines before committing E.** Both said the copy is synced
from `agentic-toolkit`; they describe the mechanism this issue replaced, so they are now false and
the text ships inside the generated copies. The other 7 stale `agentic-toolkit` mentions in
`docs/` (the agent's home, `docs/projects/`, `quickstart.md`, `collector-gh.md`) were deliberately
left for the documentation sweep. If you want these two lines left alone as well:

```bash
git checkout -- docs/guides/living-doc-glossary.md docs/guides/living-doc-header-types.md
bash agentic/scripts/sync-canon-copies.sh all   # regenerate, or CI will fail
```

## 3. Push and open the PR as a draft

```bash
git push -u origin feature/52-agentic-layer
```

Title: `#52: the agentic layer moves in from agentic-toolkit`

Body needs `## Overview`, `## Release Notes`, `## Related` (`Closes #52`, plus the `P35-AG7`
issue once it exists), a per-criterion table pointing at file and line, and the evidence from
step 4. Release notes: the living-doc skills and the `living-doc-bdd-copilot` agent now ship from
`living-doc` under `agentic/`; install instructions changed.

Open it as a **draft** — it is marked ready only once `P35-AG7` is on the same branch.

## 4. Paste the evidence into the PR body

Three criteria ask for commands and their output in the PR. Run these on the pushed branch and
paste what you get; each line says what a pass looks like.

**The copy, against its source** — every difference must be a file that stays behind:

```bash
SRC=5d356b3
D=$(mktemp -d)
git -C ../agentic-toolkit archive "$SRC" skills .github/agents docs/guides docs/testing scripts | tar -x -C "$D"
diff -r "$D/skills" agentic/skills            # only the 12 skills that stay behind
diff -r "$D/docs/guides" agentic/docs/guides  # only the 9 guides that stay behind
diff -r "$D/docs/testing" agentic/docs/testing
git show --name-only --format= c6dbcc7 | wc -l   # 109
```

Run the first three against commit `c6dbcc7`, not the branch tip — the later commits change the
copied files on purpose.

**The `#40` checks** — expected result in the comment:

```bash
grep -rn "future_release" agentic | grep -v CONTRIBUTING.md      # nothing
grep -rnE 'status:\s*descoped' agentic                           # nothing
grep -rn "pageobject_statuses" agentic                           # only the schema's
                                 # "not": {"required": [...]} and the test that asserts rejection
grep -rnE '[A-Za-z0-9](–|—)[A-Za-z0-9]' agentic                  # only numeric ranges and prose
grep -n "stub-reason" agentic/skills/data-cy-instrument/SKILL.md # removes the line, writes no status
```

**Tests, lint and links** — these all passed here on 2026-10-10:

```
script tests, Python 3.10.18 : 13/13
script tests, Python 3.14.7  : 13/13
agentskills validate         : 13/13 skill folders
lychee --offline --include-fragments : 223 OK, 0 errors
external links in the copies : 52/52 OK
```

**Still unverified by a run:** `npx skills add https://github.com/AbsaOSS/living-doc --list`
should list the 13 skills. The local `node` is broken (`icu4c` missing), so nothing backs this
yet. It should work via the CLI's recursive fallback — this repository has no top-level `skills/`
— and `agentic/README.md` records that **adding a root `skills/` directory would hide the layer's
skills from the CLI**.

## 5. Demonstrate the two CI failures (acceptance criterion 3)

The criterion asks the PR to *show* that CI fails in both directions. Do each as a throwaway
commit, link the red run in the PR, then undo it.

**A hand edit of a generated copy must fail:**

```bash
printf '\n<!-- hand edit -->\n' >> agentic/skills/shared/references/living-doc-glossary.md
git commit -am "temp: prove CI rejects a hand-edited canon copy" && git push
# link the red canon-sync-check run in the PR, then:
git reset --hard HEAD~1 && git push --force-with-lease
```

**A canon change without regenerated copies must fail:**

```bash
printf '\n' >> docs/guides/living-doc-glossary.md   # any real edit works
git commit -am "temp: prove CI rejects a canon change without regenerated copies" && git push
# link the red run, then:
git reset --hard HEAD~1 && git push --force-with-lease
```

## 6. Check CI is green

- `Agentic layer tests` — three jobs: `canon-sync-check`, `script-tests` (3.10 and 3.14),
  `skill-lint`. First run ever for this workflow, so read the logs rather than just the tick.
- `Markdown Link Check` — lychee runs with `--include-fragments`, so anchors count. Green locally.
- `Examples check` — should not trigger, but it watches `docs/guides/**`, and commit E touches two
  pages there, so expect it to run.

## 7. Close the source PR

`AbsaOSS/agentic-toolkit#40`, with a comment pointing at this PR. You said you would do this one.

---

## Not part of this issue

- **`P35-AG7`** — the `FEATURE_WITHOUT_*` code rename and dropping Feature `deprecated_at`. Lands
  on this same branch as its own commits; the PR is marked ready only after it.
- **The second half of acceptance criterion 9** — the Project Profile, `seed.yaml`, `manifest.json`
  and skill matrix sections leaving `living-doc`'s reference pages. Whichever of this PR and the
  reference-docs rework merges second cuts them. Until then the canon page keeps them, so nothing
  breaks on `master`, and the duplication is intentional.
- **The remaining 7 stale `agentic-toolkit` mentions in `docs/`** — the documentation sweep.
- **`docs/projects/agentic-toolkit.md`** — still describes the external repository, which still
  exists with its other 12 skills. The sweep rewrites it.

## About this file

`TODOs_next.md` at the repository root is **not** gitignored, unlike `specs/`, so it will appear in
`git status` and can be swept into a commit. Either keep it out of every `git add` and delete it
when done, or add it to `.gitignore`:

```bash
printf '\n# Local scratch TODO list — never shipped.\nTODOs_next.md\n' >> .gitignore
```
