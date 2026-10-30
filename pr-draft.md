# #72 — PR draft and resume notes (2026-10-30)

## Resume here

- **Branch:** `docs/72-reference-canon-authoring-guide`, cut from `master` `6294418`. The work sits in one
  temporary backup commit, together with this file and `NEXT.md` at the repository root. **Remove both files
  before the PR opens**: they name planning ids and `specs/` paths, which the PR's diff must not carry. Nothing
  was pushed, no PR exists, nothing was posted on #72.
- **Issue:** #72, *Move the canon to reference pages and add an authoring guide*. The task's planning section is
  `P35-LD5b` in `specs/liv-doc-spec/phase-3_5-v3-tasklist.md:131`, and its session prompt is
  `specs/liv-doc-spec/issues/P35-LD5b-prompt.md`.
- **Owner decisions taken this session:**
  - `link-check.yml` gets a lychee `--remap` of this repository's `blob/master` links to the checkout, because the
    new pages 404 on `master` until merge.
  - The five body evals are run by the owner in a `claude --agent eval-runner` session, not here.
- **Open:** the evals (`## Evals` below is pending) and the proposals in [NEXT.md](NEXT.md), several of which wait
  for a yes.
- **Verified locally:**
  - `examples_check.py` OK; `pytest tests/examples` 119 passed; agentic script tests 18/18 on Python 3.14 only.
  - `agentskills validate` 11/11 changed skills; `sync-canon-copies.sh all` gives no further diff.
  - `regen-collector-snapshots.sh` leaves `_expected/` unchanged; `run-testbed-stage.sh` passed.
  - lychee with the remap: 669 links, 0 errors. The four QA greps are empty (use `git grep --untracked`: the
    new pages are untracked until committed).
- **Local tooling:** there is no `python` on PATH, and the session's venv was temporary; recreate one with
  `python3 -m venv` plus both requirements files. Local lychee needs
  `--remap "https://github\.com/AbsaOSS/living-doc/blob/master/(.*) file://$PWD/\$1"` and only tracked + new
  files (`git ls-files --cached --others --exclude-standard '*.md'`), because `specs/` is gitignored.
- **Files:** [NEXT.md](NEXT.md) (next steps), this file (PR title and body), and
  `.local_context/72-reference-canon-authoring-guide/eval-run-prompt.md` (paste into eval-runner; gitignored,
  so not in the backup commit).

---

PR title: `#72: Move the canon to reference pages and add an authoring guide`

---

# Pull Request

## Overview

The format canon was right but sat at the wrong level: the glossary and the header types were references filed as
guides, the header-types page carried the agentic layer's own formats, the GitHub issue-body layout lived in the
corpus README, the view rules in a guide, and no page told an author what the pipeline corrects and what it never
guesses. This PR moves the canon to `docs/reference/`, cuts what belongs to the agentic layer (already in
`agentic-formats.md` with the same text), adds `rendering-rules.md` and the guide
`docs/guides/authoring-documentation.md`, and re-points every link, the canon-copy script and the CI path filters.

No rule changes. The two regenerated agentic copies differ from `master` only by the move: the new heads and
links, the cut sections gone, the two planned sections added.

One CI change was needed beyond the issue: the generated copies and the skills link the canon by absolute
`blob/master` URL, which returns 404 until this PR merges. `link-check.yml` now remaps this repository's
`blob/master` links to the PR's checkout (`--remap`), so they are checked against the files they will point at.
Without it, lychee reports 26 errors on this branch, every one a new-page URL; with it, 0.

## Pages

New, each opening with `## Purpose` (first sentence: what the page is for) and `## Contents`:

| Page | Level | Purpose |
|---|---|---|
| `docs/reference/glossary.md` | L4 reference | defines the entity model: the four entities, IDs and status vocabulary, the AC grammar, ID uniqueness, relationships |
| `docs/reference/authoring-formats.md` | L4 reference | defines the headers an author writes and the rules they share, then the layouts of two planned sources |
| `docs/reference/rendering-rules.md` | L4 reference | explains what each view shows and drops, and how a coverage matrix counts criteria; links `living-doc-utilities` `docs/contracts/rendering.md` and restates no table |
| `docs/guides/authoring-documentation.md` | L2 guide | shows how to write a `.feature` or PageObject header the pipeline reads as meant: write it like this, what the pipeline also accepts, what it never guesses, how to check before you push |

Moved or cut sections and their new home:

| Section | Was | Now |
|---|---|---|
| Entity model, AC grammar, ID uniqueness, relationship diagram | `docs/guides/living-doc-glossary.md` | `docs/reference/glossary.md` |
| What each `living-doc-bdd-copilot` skill creates or consumes | glossary | cut; `agentic/skills/shared/references/agentic-formats.md`, linked from the glossary's Purpose |
| Repository adoption scope, Indentation, AC variants, §§ 1–3 (anchors kept) | `docs/guides/living-doc-header-types.md` | `docs/reference/authoring-formats.md` |
| Project Profile, `seed.yaml`, `manifest.json` | header types | cut; `agentic-formats.md`, linked from the page's Purpose |
| GitHub issue-body layout (canonical) | `docs/examples/README.md` | `authoring-formats.md#github-issue-body-layout`, marked planned |
| Azure DevOps authoring note | none | `authoring-formats.md#azure-devops-work-items`, marked planned |
| "Two views", drop rules by state, "What was not loaded" | `docs/guides/living-doc-document-types.md` § Technical project | `rendering-rules.md#views`, `#what-was-not-loaded` |
| Coverage verdicts and counting | document types § Coverage matrix | `rendering-rules.md#coverage`, verdicts by link to `authoring-formats.md#ac-variants` |

Redirects (a `# Title` and one line naming the new page): `docs/guides/living-doc-glossary.md` →
`docs/reference/glossary.md`; `docs/guides/living-doc-header-types.md` → `docs/reference/authoring-formats.md`.

## Links

Re-pointed in this repository:

- `docs/`: `guides/living-doc-document-types.md`, `guides/github-collection.md`, `examples/README.md`,
  `introduction/principles.md`, `introduction/quickstart.md`, `projects/agentic-toolkit.md`,
  `projects/collector-gh.md`, `tutorials/gh-issues-to-markdown.md`, `tutorials/gh-source-to-markdown.md`,
  `tutorials/technical-project-to-pdf.md`; `README.md` lists the new guide.
- `agentic/`: the remote links in nine `SKILL.md`; the "BDD schemas" pointers of `bdd-maintain`,
  `data-cy-instrument`, `living-doc-pageobject-scan` and `living-doc-scenario-creator` and the agent's two
  pointers (`living-doc-bdd-copilot.agent.md:64`, `:190-192`) now send the Project Profile, `seed.yaml` and
  `manifest.json` to `agentic-formats.md`; `agentic-formats.md:82`; `agentic/README.md`; script comments.
- `tests/examples/examples_check.py`: docstring, comments, fix hints and the last output line (no check changed);
  a comment in `test_examples_check.py`.
- `docs/examples/project-profile/.project-profile.yaml:3` (a comment).
- `CONTEXT.md`, `docs/CONTEXT.md`, `agentic/CONTEXT.md`, `.github/CONTEXT.md`, `AGENTS.md`.

Links from other repositories into a moved page. The redirects keep every one resolving, but the three with a
fragment fail `lychee --include-fragments` once this merges. New base:
`https://github.com/AbsaOSS/living-doc/blob/master/docs/reference/`.

`living-doc-utilities` (`master` `d6a82a8`), fragment links first:

| File | Links to | New target |
|---|---|---|
| `docs/authoring/parsers.md:51` | `living-doc-header-types.md#indentation` | `authoring-formats.md#indentation` |
| `docs/authoring/parsers.md:88` | `living-doc-glossary.md#core-entities` | `glossary.md#core-entities` |
| `docs/contracts/entities-and-state.md:37` | `living-doc-glossary.md#acceptance-criterion-ac` | `glossary.md#acceptance-criterion-ac` |
| `docs/authoring.md:21` | glossary, header types | `glossary.md`, `authoring-formats.md` |
| `docs/authoring/parsers.md:25` | glossary, header types | `glossary.md`, `authoring-formats.md` |

Also in `living-doc-utilities`: `docs/contracts/rendering.md:50` links `living-doc-document-types.md#technical-project`
for *What was not loaded*, which still resolves; the rule now lives at `rendering-rules.md#what-was-not-loaded`.
Mentions that are no link: `living_doc_utilities/authoring/normalisation_cases.yaml:4-5`,
`living_doc_utilities/contracts/CONTEXT.md:32`, `living_doc_utilities/contracts/testing.py:428`,
`tests/authoring/test_notes.py:611`.

`living-doc-collector-gh` (`master` `93faed7`), no fragment:

| File | Links to | New target |
|---|---|---|
| `README.md:83` | header types | `authoring-formats.md` |
| `doc_source/README.md:119` | header types, glossary | `authoring-formats.md`, `glossary.md` |
| `docs/action.md:140` | header types | `authoring-formats.md` |
| `ui_tests/README.md:96` | header types, glossary | `authoring-formats.md`, `glossary.md` |

`living-doc-toolkit` (`master` `0601fa1`): `packages/core/README.md:87` links `living-doc-document-types.md`, which
stays; how each view is shown is now `rendering-rules.md#views`.

## Canon

Each rule this change carries, with its page. None changed.

| Rule | Here | `living-doc-utilities` `v0.8.0` |
|---|---|---|
| Entity model, AC grammar and states, ID uniqueness | `docs/reference/glossary.md` | `docs/authoring/ac-grammar.md` |
| `.feature` and PageObject headers, Indentation, AC variants, adoption scope | `docs/reference/authoring-formats.md` | `docs/authoring.md`, `docs/authoring/parsers.md` |
| GitHub issue-body layout; which heading fills which field | `authoring-formats.md#github-issue-body-layout` | `docs/authoring/parsers.md#issue-body` |
| Azure DevOps: the same `##` sections, HTML read as an issue body | `authoring-formats.md#azure-devops-work-items` | `docs/authoring/normalisation.md#source-formats` |
| What each view shows and drops; authored fields reach the generator at their level | `docs/reference/rendering-rules.md#views` | `docs/contracts/rendering.md#records-and-presentation`, `#fields-by-view` |
| What was not loaded | `rendering-rules.md#what-was-not-loaded` | `docs/contracts/rendering.md#fields-by-view` (last row) |
| Coverage per value; `active` and `deprecated` counted, `in_review` and `planned` not; the weighted figure; planned summary inner only | `rendering-rules.md#coverage` | `docs/contracts/rendering.md#coverage`, `#coverage-summary`, `#planned-work-summary` |
| Variants the pipeline corrects (16 before/after pairs, each equal to its case's `input` and `expected`) | `docs/guides/authoring-documentation.md#what-the-pipeline-also-accepts` | `living_doc_utilities/authoring/normalisation_cases.yaml`, `docs/authoring/normalisation.md#rules` |
| What it never guesses: missing or short version, misspelt state or status, missing id, `Aspect:` plus a keyword | `authoring-documentation.md#what-it-never-guesses` | `docs/authoring/ac-grammar.md#dropped-criteria`, `docs/authoring/parsers.md#status-derivation`, `docs/contracts/errors.md#codes` |

Every pair and every "never guesses" row was run through `living-doc-utilities` 0.8.0 before it was written.
Wording that changed without a rule: the issue-body layout loses its history paragraph and the sentence naming the
deleted `toolkit/docs/contracts.md` synonym table, replaced by the `living-doc-utilities` heading-to-field link; the
document-types drop table's note that state matching is case-insensitive is gone, because states reach the view
filter already canonical.

## Evals

The pointer change touches the body of four skills and the agent, so their body evals run against
`agentic/docs/testing/baseline.md`. The skill and agent text of these five targets on `master` equals the state
the baseline measured.

| Target | Evals | Assertions | Baseline r1 / r2 (baseline.md) | This PR r1 / r2 | `old_skill` (`master`) | Δ | Drops, classified |
|---|---|---|---|---|---|---|---|
| `bdd-maintain` | 11 | 39 | 0.92 / 0.92 | _pending_ | _pending_ | | |
| `data-cy-instrument` | 12 | 44 | 0.98 / 1.00 | _pending_ | _pending_ | | |
| `living-doc-pageobject-scan` | 17 | 85 | 0.93 / 0.93 | _pending_ | _pending_ | | |
| `living-doc-scenario-creator` | 25 | 106 | 0.90 / 0.90 | _pending_ | _pending_ | | |
| `@living-doc-bdd-copilot` | 26 | 133 | 0.53 / 0.54 | _pending_ | _pending_ | | |

Executor Haiku, grader Sonnet, as in the baseline. The other seven skills' `SKILL.md` edits change a URL and no
rule; the script tests (18/18), `agentskills validate` (11/11 changed skills valid) and the canon-copy job cover
them.

## Acceptance criteria

| Criterion | Delivered at |
|---|---|
| Three reference pages exist; old paths are redirects; corpus README links the layout | `docs/reference/{glossary,authoring-formats,rendering-rules}.md`; `docs/guides/living-doc-glossary.md:3`, `living-doc-header-types.md:3`; `docs/examples/README.md:28-33` |
| `authoring-formats.md` holds adoption scope, Indentation, AC variants, no agentic format; glossary has no matrix; both link `agentic-formats.md` | `authoring-formats.md:28`, `:44`, `:126`; `authoring-formats.md:9`, `glossary.md:8` |
| `rendering-rules.md` explains views and coverage, links `rendering.md`, no table; document types links it, restates neither | `rendering-rules.md:7`, `:18`, `:53`; `living-doc-document-types.md:8`, `:59`, `:121` |
| Guide has four sections; keyword criterion; `Aspect:` plus keyword drops it; pairs equal their cases | `authoring-documentation.md:21`, `:107`, `:434`, `:451`; `:91`; `:447`; 16 pairs from `:117` |
| Script reads the moved pages; copies regenerated; filters | `agentic/scripts/sync-canon-copies.sh:47-48`; `agentic-tests.yml:24-25`, `:31-32`; `examples-check.yml:25`, `:33` |
| No link to a moved page or cut section; context files name the new pages; other repos listed | § Links; `CONTEXT.md:49-50`, `:58-59`, `:83`; `docs/CONTEXT.md:17`, `:25-27`; `agentic/CONTEXT.md:33`; `.github/CONTEXT.md:13`; `AGENTS.md:84` |
| Purpose then Contents on every new page | `glossary.md:3`, `:14`; `authoring-formats.md:3`, `:15`; `rendering-rules.md:3`, `:12`; `authoring-documentation.md:3`, `:14` |
| Link check, examples check, agentic tests green; five evals | local runs below; § Evals |
| In sync with the canon | § Canon |
| Framework box | below |

Local runs: `examples_check.py` OK; `pytest tests/examples` 119 passed; agentic script tests 18/18 (Python 3.14);
`sync-canon-copies.sh all` leaves only the two copies and `agentic-formats.md` changed against `master`;
`regen-collector-snapshots.sh` leaves `docs/examples/_expected/` unchanged; `run-testbed-stage.sh` passed;
lychee with the CI arguments and the remap, over tracked and new Markdown: 669 links, 0 errors.

## Release Notes
- The format canon now lives in `docs/reference/`: `glossary.md`, `authoring-formats.md` and the new
  `rendering-rules.md`, which explains what each view shows and how coverage is counted. The old guide paths
  redirect to them.
- New guide `docs/guides/authoring-documentation.md`: the canonical form of each header, the variants the pipeline
  corrects (before/after pairs from `living-doc-utilities` 0.8.0), the mistakes it never guesses with the warning
  you see, and how to check before you push.
- The GitHub issue-body layout and an Azure DevOps note moved into `authoring-formats.md`, both marked planned.
- The agentic layer's Project Profile, `seed.yaml` and `manifest.json` formats and its skill matrix are documented
  only in `agentic/skills/shared/references/agentic-formats.md`; the skills and the agent point there.
- The link check verifies this repository's own `blob/master` links against the pull request's files.

## Framework
- [x] Stays inside the frame (F1–F7)
- [ ] Bends frame row F_ — exception E_ added to `docs/introduction/principles.md` in this PR

## Related
Closes #72

🤖 Generated with [Claude Code](https://claude.com/claude-code)
