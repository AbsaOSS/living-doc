# What is Living Documentation?

Living Documentation is documentation that is **generated from the systems a team already works in** — issue trackers, work item boards, pipelines — rather than written and maintained as a separate artifact.

## The problem it solves

Hand-written documentation drifts from reality: a wiki page or design doc is accurate the day it's written and stale a month later, because nothing forces it to track the underlying work. Teams either let it rot or spend real time keeping it in sync.

## The approach

Instead of asking people to write and update docs, Living Documentation treats the source system — GitHub issues, Azure DevOps work items — as the source of truth, and regenerates documentation from it on a schedule or on every change:

1. **Collect** — pull structured data (issues, labels, work items, boards) out of the source system.
2. **Normalize** — transform that data into one canonical shape, regardless of where it came from.
3. **Generate** — render the canonical data into a target format: Markdown, or PDF reports.

Because the pipeline runs automatically (e.g. as a scheduled GitHub Action), the resulting documentation is never more than one run behind the actual state of the project.

## Principles

- **Source of truth lives in the tracker, not in prose.** Issues, labels, and work items already describe scope, status, and ownership — documentation should reflect them, not duplicate them by hand.
- **Docs as a build artifact.** Documentation is generated output, checked or published like any other pipeline artifact — not a file people edit directly.
- **Pluggable by source and by output.** Any collector can feed any generator through the shared canonical dataset, so a team using Azure DevOps and one using GitHub can both produce the same Markdown or PDF output.

See [Architecture](architecture.md) for how the pieces of the ecosystem implement this, or jump
straight to [Living Documentation in 5 Minutes](quickstart.md) to stand up a pipeline now.
