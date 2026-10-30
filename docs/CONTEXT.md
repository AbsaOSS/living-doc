# docs

Parent: [../CONTEXT.md](../CONTEXT.md)

## Purpose

The people docs of the ecosystem, plus the format canon and the example corpus that other repositories, the checks in `tests/` and `agentic/` read.

Not here: each tool's own docs (its repository) and the agentic layer's guides (`agentic/docs/`).

## Layout

| Path | Holds |
|---|---|
| `introduction/` | concept, quickstart, architecture, principles (the frame) |
| `guides/` | how-tos: authoring, document types, collection; two redirect stubs for the moved canon pages |
| `reference/` | the canon: glossary, authoring formats, rendering rules |
| `tutorials/` | one per source + output combination |
| `projects/` | one page per ecosystem project |
| `examples/` | the canonical minimal input corpus; `_expected/` holds what the pinned collector mines from it and the pinned toolkit writes from that |
| `_integration/` | gate reports from local integration runs, one folder per gate |

## Contracts

- Format canon: `reference/authoring-formats.md`, `reference/glossary.md`. `reference/rendering-rules.md` explains the views and coverage, whose normative rules are `living-doc-utilities`' `docs/contracts/rendering.md`. `guides/living-doc-document-types.md` stays the guide and links it.
- `authoring-formats` and `glossary` have generated copies in `agentic/skills/shared/references/` (`agentic/scripts/sync-canon-copies.sh`); a change to either triggers `agentic-tests.yml`.
- Any change under `guides/`, `reference/` or `examples/` triggers `examples-check.yml`, which validates `examples/` with `tests/examples/examples_check.py`.

## Conventions

- Sync obligation: a field or rule change in `authoring-formats` or `glossary` updates the matching example in the same PR ([examples/README.md § Sync obligation](examples/README.md#sync-obligation)).
- Renaming or restructuring a doc type cascades in the same PR to every guide, tutorial, project page and example that names the old shape.
- The corpus is one coherent mini project and minimal: each entity file has every required field plus one optional field extension, and each extension appears once across the corpus. Don't add a second instance ([examples/README.md § Conventions](examples/README.md#conventions-used-by-this-corpus)).
- Never hand-edit `examples/_expected/**`, the collector's or the toolkit's; regenerate it with `tests/examples/regen-collector-snapshots.sh`.
- Renaming a heading breaks fragment links elsewhere; lychee checks fragments.
- A moved page keeps a redirect stub at its old path: its `# Title` and one line linking the new page, nothing else.

## Invariants and gotchas

- `_integration/`: the repository is public. An internal target's configuration, log and artifacts stay on the machine; only its redacted report row is committed, under an `absa-N` label ([_integration/README.md](_integration/README.md)).
- Pages and tutorials marked *(planned)* describe intended behavior that no tool ships yet.
- `guides/authoring-documentation.md`'s before/after pairs are copied byte for byte from `living-doc-utilities` `living_doc_utilities/authoring/normalisation_cases.yaml` at `v0.8.0`, each under its case id. Re-check them when the `living-doc-utilities` pin moves; no check enforces it yet.
