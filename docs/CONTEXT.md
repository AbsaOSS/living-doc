# docs

Parent: [../CONTEXT.md](../CONTEXT.md)

## Purpose

The people docs of the ecosystem, plus the format canon and the example corpus that other repositories, the checks in `tests/` and `agentic/` read.

Not here: each tool's own docs (its repository) and the agentic layer's guides (`agentic/docs/`).

## Layout

| Path | Holds |
|---|---|
| `introduction/` | concept, quickstart, architecture, principles (the frame) |
| `guides/` | how-tos and the three format contracts |
| `tutorials/` | one per source + output combination |
| `projects/` | one page per ecosystem project |
| `examples/` | the canonical minimal input corpus; `_expected/` holds what the pinned collector mines from it |
| `_integration/` | gate reports from local integration runs, one folder per gate |

## Contracts

- Format canon: `guides/living-doc-header-types.md`, `guides/living-doc-glossary.md`, `guides/living-doc-document-types.md`.
- `header-types` and `glossary` have generated copies in `agentic/skills/shared/references/` (`agentic/scripts/sync-canon-copies.sh`); a change to either triggers `agentic-tests.yml`.
- Any change under `guides/` or `examples/` triggers `examples-check.yml`, which validates `examples/` with `tests/examples/examples_check.py`.

## Conventions

- Sync obligation: a field or rule change in `header-types` or `glossary` updates the matching example in the same PR ([examples/README.md § Sync obligation](examples/README.md#sync-obligation)).
- Renaming or restructuring a doc type cascades in the same PR to every guide, tutorial, project page and example that names the old shape.
- The corpus is one coherent mini project and minimal: each entity file has every required field plus one optional field extension, and each extension appears once across the corpus. Don't add a second instance ([examples/README.md § Conventions](examples/README.md#conventions-used-by-this-corpus)).
- Never hand-edit `examples/_expected/**`; regenerate it with `tests/examples/regen-collector-snapshots.sh`.
- Renaming a heading breaks fragment links elsewhere; lychee checks fragments.

## Invariants and gotchas

- `_integration/`: the repository is public. An internal target's configuration, log and artifacts stay on the machine; only its redacted report row is committed, under an `absa-N` label ([_integration/README.md](_integration/README.md)).
- Pages and tutorials marked *(planned)* describe intended behavior that no tool ships yet.
