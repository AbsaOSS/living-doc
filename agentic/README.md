# Agentic layer

The skills and the agent that help an author write living-doc input: User Story, Feature and
Functionality entities, Gherkin `.feature` files, and the PageObject and BDD artifacts around
them.

**The pipeline runs without any of this.** Collectors, toolkit and generators are AI-free, and
every input this layer produces can be written by hand — it accelerates authoring, it is never
required.

## Install

Skills install one at a time, each alongside `shared`, which carries the shared library and the
reference documents every skill reads:

```bash
npx skills add https://github.com/AbsaOSS/living-doc -g --skill living-doc-update
npx skills add https://github.com/AbsaOSS/living-doc -g --skill shared
```

Check what the CLI finds here before installing:

```bash
npx skills add https://github.com/AbsaOSS/living-doc --list
```

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

The agent lives here, apart from `.github/agents/`, which holds this repository's own development
agents and has nothing to do with the layer.

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

CI runs the Python script tests, the canon-copy check and `SKILL.md` format validation. It runs no
eval: the eval loops in both guides are manual.
