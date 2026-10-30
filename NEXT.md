# #72 — next steps (2026-10-30)

Proposals for the open judgement calls and the work not done. Three items edit the task list, and two
are outward-facing; none has been applied. Mark each **yes** / **no** before the next session acts on it.
Resume state and the PR body: [pr-draft.md](pr-draft.md).

## Judgement calls

| # | Call | Recommendation | Next step |
|---|---|---|---|
| 1 | Issue-body layout: dropped the history paragraph and the sentence citing the deleted synonym table | Keep. No rule changed, and the `utilities` heading-to-field table states the mapping exactly. | None. It's already declared in the PR body § Canon. |
| 2 | Document types: dropped the "state matching is case-insensitive" note | Keep. | None. Also declared in § Canon. |
| 3 | "What was not loaded" moved to `rendering-rules.md` | Keep. The AC says document types restates no view rule. | **Task list edit (needs yes):** `P35-UT17`'s measured list (`:182`) says `rendering.md:50` "stays". Change it to re-point to `rendering-rules.md#what-was-not-loaded`, and add `tests/authoring/test_notes.py:611`, a fifth mention it doesn't list. `toolkit` `packages/core/README.md:87` still resolves, so leave it for `toolkit`'s next docs task. |
| 4 | New guide added to README § Guides | Keep. Without it the guide is reachable only through other new pages. | None. `P35-LD3` rebuilds the README by role, and the docs map already puts this guide first on the author path. |
| 5 | "Authored fields reach the generator" line in `rendering-rules.md` | Keep. The docs map makes this page that fact's home. | None. |
| 6 | Three link labels fixed in `living-doc-pageobject-scan` | Keep. The eval run covers this skill anyway. | None. |
| 7 | `DEC-74` left at `compute_gaps.py:38` and `:338` | Don't widen this PR. | Add one line to the agentic debt list: "planning ids in shipped script comments, `compute_gaps.py:38`, `:338`". Before that, grep `agentic/` for other planning ids so the item states its full size. |

## Not done

1. **Evals.** Start `claude --agent eval-runner` early in a quota window and paste
   `.local_context/72-reference-canon-authoring-guide/eval-run-prompt.md`. When it reports:
   - Copy its table into the PR body's `## Evals` ([pr-draft.md](pr-draft.md)).
   - A drop the grader confirms blocks the merge (eval protocol § 5). It would most likely be a runner that
     didn't follow a new pointer. Fix the pointer's wording, then re-run that target only.
   - A drop on unchanged text, or one where the assertion itself is wrong, goes into the PR body as a
     finding but doesn't block.

   Open the PR before the run, as a draft if preferred, so CI covers the Python 3.10 script tests that
   didn't run locally.

2. **Commit and PR.** One commit, since this repo squash-merges. Title:
   `#72: Move the canon to reference pages and add an authoring guide`. The body is in
   [pr-draft.md](pr-draft.md) with `## Evals` still pending.
   - **Order after merge:** `P35-UT17` must land before any other `utilities` PR. Its three fragment links
     fail that repo's link check from the moment #72 merges. `P35-CGH8` can follow later, because
     `collector-gh`'s links land on the redirect pages.

3. **Remap note on #72 (outward-facing, needs yes).** Post it before the PR opens, so the CI change isn't
   a surprise in review. Draft:
   > The moved pages are linked by absolute `blob/master` URLs (the generated agentic copies, the skills'
   > remote links), which return 404 until this merges. `link-check.yml` therefore gains one `--remap` that
   > checks this repository's own `blob/master` links against the PR's checkout. On this branch that turns
   > 26 errors, all new-page URLs, into 0.

4. **The spec citation in the glossary.** `P35-LD3` already plans to rewrite it (tasklist `:341`), but its
   pointer is stale. **Task list edit (needs yes):** change `docs/guides/living-doc-glossary.md:362-365` and
   the copy's `:365-368` to `docs/reference/glossary.md:356` and the copy's `:359`.

5. **Pair format, for `P35-LD2a3`.** Its check (tasklist `:204`) will parse the guide's pairs.
   **Task list edit (needs yes):** record the format the guide now uses in that section: a bold case id
   line, then a `text before` block and a `text after` block, 16 pairs, all rewriting cases from the three
   formats.

After the merge, the tasklist's `living-doc` baseline paragraph (`:56`), which still says the sync sources
live in `docs/guides/`, should be re-measured as usual before `P35-UT17` is drafted.
