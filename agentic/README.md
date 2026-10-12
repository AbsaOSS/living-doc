# Agentic layer

The skills and the agent that help an author write living-doc input: User Story, Feature and
Functionality entities, Gherkin `.feature` files, and the PageObject and BDD artifacts around
them.

**The pipeline runs without any of this.** Collectors, toolkit and generators are AI-free, and
every input this layer produces can be written by hand — it accelerates authoring, it is never
required.

## Install

Two separate things, installed two different ways: the **skills** come from the skills CLI, the
**agent** is a file you copy. The agent is useless without the skills, so do the skills first.

### Prerequisites

| To | You need |
|---|---|
| install a skill | Node, for `npx` |
| run a skill's bundled scripts | Python 3.10+ with `PyYAML` and `jsonschema`, in an **activated virtual environment** — the commands in each skill are written as `python` |
| use `living-doc-pageobject-scan`, or the agent's crawl, re-scan and healing modes | an MCP Playwright server connected in your editor; those modes stop without it |

### Skills — 13 installs, because `shared` counts

Skills install one at a time. See what the CLI finds here before you start:

```bash
npx skills add https://github.com/AbsaOSS/living-doc --list
```

**`shared` is not optional.** All twelve skills read the canon reference documents next to it, and
six of them bundle scripts that import its library and exit with an error without it. `npx skills
add` copies only the selected skill's folder and `shared`'s into your project, which is why the
canon copies travel with the skill — this repository's `docs/` does not exist there.

```bash
R=https://github.com/AbsaOSS/living-doc

npx skills add $R -g --skill shared                        # required by all twelve below

npx skills add $R -g --skill living-doc-create-user-story
npx skills add $R -g --skill living-doc-create-feature
npx skills add $R -g --skill living-doc-create-functionality
npx skills add $R -g --skill living-doc-update
npx skills add $R -g --skill living-doc-gap-finder
npx skills add $R -g --skill living-doc-impact-analysis
npx skills add $R -g --skill living-doc-pageobject-scan
npx skills add $R -g --skill living-doc-scenario-creator
npx skills add $R -g --skill gherkin-living-doc-sync
npx skills add $R -g --skill gherkin-step
npx skills add $R -g --skill bdd-maintain
npx skills add $R -g --skill data-cy-instrument
```

Install only the ones you need — they work individually, as long as `shared` is there. `-g`
installs for your user, so every project sees them; drop it to install into the current project
only.

### Agent — copy the file

The skills CLI installs skills, and `@living-doc-bdd-copilot` is not one: no `--skill` selector
reaches it. Copy it into the `.github/agents/` directory of the repository you want to use it in:

```bash
mkdir -p .github/agents
curl -o .github/agents/living-doc-bdd-copilot.agent.md \
  https://raw.githubusercontent.com/AbsaOSS/living-doc/master/agentic/agents/living-doc-bdd-copilot.agent.md
```

> Whether the skills CLI can also install an agent has not been verified — it is documented for
> skills only. If it turns out to support them, this step collapses to one command; until then the
> copy above is the procedure.

**The agent needs the skills.** It carries no behaviour of its own — every mode dispatches to one
of the twelve. Installed alone it will answer, route to a skill that is not there, and fail at the
first real task.

### If something is missing

- A script printing `shared library not found` means the `shared` skill was not installed, or not
  installed beside the skill that is calling it.
- A script failing on `No module named 'yaml'` or `jsonschema` means the interpreter running it is
  not the virtual environment from the prerequisites.
- `@living-doc-bdd-copilot` not responding to an `@`-mention means the agent file is not in
  `.github/agents/` of the repository you have open. It is never auto-triggered; only skills are.

> **Why no path is needed.** The CLI looks for skills in a repository's `skills/` directory
> first and falls back to a recursive search when it finds none there. This repository has no
> top-level `skills/`, so the fallback finds the skills under `agentic/skills/` and `--skill
> <name>` selects by name. **Do not add a top-level `skills/` directory** to this repository: it
> would satisfy the primary search and hide this layer's skills from the CLI.

## Skills

| Skill | What it does | Guide |
|---|---|---|
| `living-doc-create-user-story` | Creates a well-formed User Story with business-level ACs | [guide](docs/guides/living-doc-create-user-story.md) |
| `living-doc-create-feature` | Defines a system surface (UI screen or API endpoint) as a Feature | [guide](docs/guides/living-doc-create-feature.md) |
| `living-doc-create-functionality` | Defines an atomic, testable behaviour with its ACs | [guide](docs/guides/living-doc-create-functionality.md) |
| `living-doc-update` | Updates or deprecates existing entities and their ACs | [guide](docs/guides/living-doc-update.md) |
| `living-doc-gap-finder` | Audits the catalog for gaps, bottom-up and top-down | [guide](docs/guides/living-doc-gap-finder.md) |
| `living-doc-impact-analysis` | Traces a code change to the entities it affects | [guide](docs/guides/living-doc-impact-analysis.md) |
| `living-doc-pageobject-scan` | Discovers and maintains PageObjects by exploring a web app | [guide](docs/guides/living-doc-pageobject-scan.md) |
| `living-doc-scenario-creator` | Generates Gherkin scenarios and feature files from ACs | [guide](docs/guides/living-doc-scenario-creator.md) |
| `gherkin-living-doc-sync` | Keeps feature files and the catalog's AC links in step | [guide](docs/guides/gherkin-living-doc-sync.md) |
| `bdd-maintain` | Lifecycle cleanup of BDD artifacts: removal, dead code, healing | [guide](docs/guides/bdd-maintain.md) |
| `gherkin-step` | Implements clean, reusable Gherkin step definitions | [guide](docs/guides/gherkin-step.md) |
| `data-cy-instrument` | Resolves missing `data-cy` attributes and syncs PageObjects | [guide](docs/guides/data-cy-instrument.md) |
| `shared` | Not a task skill: the shared library and reference documents | — |

## Agent

`agents/living-doc-bdd-copilot.agent.md` drives the whole lifecycle and dispatches to the skills
above. Invoke it by `@`-mention; it is not auto-triggered.
[Guide](docs/guides/living-doc-bdd-copilot.md) · [evals](agents/evals/living-doc-bdd-copilot/)

The agent lives here, apart from [`.github/agents/`](../.github/agents/README.md), which holds this
repository's own development agents and has nothing to do with the layer. The test for which
directory an agent belongs in: would it be useful to someone who installed the layer and never opens
this repository? If no, it goes to `.github/agents/`. That page records the rest of the convention —
frontmatter keys, and why those agents carry no guide and no eval set.

## Reference documents

`skills/shared/references/` holds what every skill reads:

| File | Source |
|---|---|
| `living-doc-glossary.md` | **Generated** from `docs/guides/living-doc-glossary.md` |
| `living-doc-bdd-schemas.md` | **Generated** from `docs/guides/living-doc-header-types.md` |
| `agentic-formats.md` | Hand-maintained: the Project Profile, `seed.yaml`, `manifest.json` and the skill matrix — formats the layer owns |
| `schemas/*.schema.json` | Hand-maintained JSON schemas for the three formats above |

The two generated copies are rewritten from this repository's `docs/` at the same commit by
[`scripts/sync-canon-copies.sh`](scripts/sync-canon-copies.sh), and CI fails if a committed copy
differs. **Do not edit them by hand.** They exist because `npx skills add` copies only a skill's
folder and `shared`'s into a user's project, where this repository's `docs/` does not exist — so a
skill reads the copy next to it, and the copy cannot drift from the canon it was generated from.

## Testing and contributing

- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to run the layer's tests, and the checklist for a
  pull request that changes a skill or the agent
- [`docs/testing/skill-testing.md`](docs/testing/skill-testing.md) — eval creation, fixtures,
  regression loops, trigger and description optimisation
- [`docs/testing/agent-testing.md`](docs/testing/agent-testing.md) — body evals for the
  `.agent.md` file
- [`docs/testing/eval-protocol.md`](docs/testing/eval-protocol.md) — how to run a whole suite so
  its numbers can be trusted, compared and reproduced: arms and models, the harness behaviours that
  silently produce wrong figures, grading discipline, and what a run must deliver
- [`docs/testing/baseline.md`](docs/testing/baseline.md) — the recorded result every later run is
  compared against
- [`scripts/evals/`](scripts/evals/README.md) — the deterministic half of a run (scaffolding,
  timing, grading normalisation, benchmark correction, baseline comparison)

CI runs the Python script tests, the canon-copy check and `SKILL.md` format validation. It runs no
eval: the eval loops in both guides are manual.
