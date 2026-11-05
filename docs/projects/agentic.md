# Agentic layer

## Purpose

This page is the card of the agentic layer in [`agentic/`](../../agentic/README.md): what it accelerates, and that
the pipeline never needs it.

- **Role:** authoring acceleration, optional: the `living-doc-bdd-copilot` agent and its twelve task skills, plus
  the companion skill `shared`, which holds the entity-ID and AC-tag grammar the other skills import.
- **Accelerates:** writing User Story, Feature and Functionality headers and the Gherkin `.feature` files bound to
  them, with the test surface those tests need (PageObjects, test ids, gap reports), in the format
  [living-doc-collector-gh](collector-gh.md) mines. It ships from this repository.
- **Not a dependency:** the pipeline runs AI-free, and everything the layer writes can be written by hand.
- **Reads:** copies generated from [Glossary](../reference/glossary.md) and
  [Authoring formats](../reference/authoring-formats.md).
- **Its own formats:** the Project Profile, `seed.yaml` and `manifest.json`, in
  [agentic-formats.md](../../agentic/skills/shared/references/agentic-formats.md).
- **Pages:** [README](../../agentic/README.md), to install and use it;
  [CONTRIBUTING](../../agentic/CONTRIBUTING.md), to change it.
