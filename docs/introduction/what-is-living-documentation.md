# What is Living Documentation?

## Purpose

This page is the concept: the problem living documentation solves, how it solves it, and the principles it follows.

Read before: [README](../../README.md) · Next: [Architecture](architecture.md)

## Contents

- [The problem it solves](#the-problem-it-solves)
- [The approach](#the-approach)
- [Principles](#principles)

## The problem it solves

Hand-written documentation drifts from reality: a wiki page or design doc is accurate the day it's written and stale a month later, because nothing forces it to track the underlying work. Teams either let it rot or spend real time keeping it in sync.

## The approach

Living Documentation is documentation that is **generated from what a team already works in** rather than written and maintained as a separate artifact. It treats the source system as the source of truth: today the source code and its `.feature` files; GitHub issues and Azure DevOps work items are planned. It regenerates documentation from it on a schedule or on every change:

1. **Collect** — pull structured data (header blocks and test scenarios; issues and work items once those sources land) out of the source system.
2. **Normalize** — transform that data into one canonical shape, regardless of where it came from.
3. **Generate** — render the canonical data into a target format: Markdown today, PDF reports once PDF output lands.

Because the pipeline runs automatically (e.g. as a scheduled GitHub Action), the resulting documentation is never more than one run behind the actual state of the project.

## Principles

- **Source of truth lives where the work is described, not in prose.** Today that is the User Story, Feature and Functionality headers in source code and the Gherkin scenarios beside them; issues and work items are planned. They already describe scope, status and ownership — documentation should reflect them, not duplicate them by hand.
- **Docs as a build artifact.** Documentation is generated output, checked or published like any other pipeline artifact — not a file people edit directly.
- **Pluggable by source and by output.** Collectors and generators meet only at the toolkit's canonical dataset, so a planned source (GitHub issues, Azure DevOps) or output (PDF) plugs in without changing the parts around it.

See [Architecture](architecture.md) for how the pieces of the ecosystem implement this, or jump
straight to [Living Documentation in 5 Minutes](quickstart.md) to stand up a pipeline now.
