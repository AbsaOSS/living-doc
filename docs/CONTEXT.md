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
| `reference/` | the canon: glossary, authoring formats, rendering rules; and three summaries of `living-doc-utilities`: data flows, contracts, error codes |
| `tutorials/` | one per source + output combination |
| `projects/` | one page per ecosystem project |
| `examples/` | the canonical minimal input corpus; `_expected/` holds what the pinned collector mines from it and the pinned toolkit writes from that |
| `_integration/` | gate and milestone reports from local integration runs, one folder per gate (`G1/`, `G2/`) or milestone (`MS1/`); a milestone runs `tests/integration/local-integration.sh` |

## Contracts

- Format canon: `reference/authoring-formats.md`, `reference/glossary.md`. `reference/rendering-rules.md` explains the views and coverage, whose normative rules are `living-doc-utilities`' `docs/contracts/rendering.md`; its *What was not loaded* is the canon's own rule, which that page maps onto warning fields. `guides/living-doc-document-types.md` stays the guide and links it.
- `reference/data-flows.md`, `reference/contracts.md` and `reference/errors.md` are not canon: they summarise `living-doc-utilities`' `docs/contracts/pipeline-rules.md`, `docs/contracts.md` with `artifact-rules.md` and `entities-and-state.md`, and `docs/contracts/errors.md`, and link them without restating a rule. Their paths, inputs, commands and who raises a code come from the component pages and code (`collector-gh` `docs/action.md` and mode READMEs, `toolkit` `docs/action.md`, `generator-markdown` `README.md`), so a change there can make them stale. Each marks a part no component ships as planned.
- `reference/errors.md` has one row per code of `living_doc_utilities.contracts.codes.ALL_CODES`, the code alone in backticks in the first column. `tests/examples/examples_check.py` (rule 9) compares the first column of § Codes with the registry of the installed version: a code added to or removed from the registry fails it until the table has its row added or removed.
- `authoring-formats` and `glossary` have generated copies in `agentic/skills/shared/references/` (`agentic/scripts/sync-canon-copies.sh`); a change to either triggers `agentic-tests.yml`.
- Any change under `guides/`, `reference/` or `examples/` triggers `examples-check.yml`, which validates `examples/`, the pairs in `guides/authoring-documentation.md` and the codes in `reference/errors.md` with `tests/examples/examples_check.py`.
- Every change triggers `retired-names.yml`: no retired artifact, field or command name in any file here (`tests/docs/retired_names_check.py` holds the names).

## Conventions

- Sync obligation: a field or rule change in `authoring-formats` or `glossary` updates the matching example in the same PR ([examples/README.md § Sync obligation](examples/README.md#sync-obligation)).
- Renaming or restructuring a doc type cascades in the same PR to every guide, tutorial, project page and example that names the old shape.
- The corpus is one coherent mini project and minimal: each entity file has every required field plus one optional field extension, and each extension appears once across the corpus. Don't add a second instance ([examples/README.md § Conventions](examples/README.md#conventions-used-by-this-corpus)).
- Never hand-edit `examples/_expected/**`, the collector's or the toolkit's; regenerate it with `tests/examples/regen-collector-snapshots.sh`.
- Renaming a heading breaks fragment links elsewhere; lychee checks fragments.
- A moved page keeps a redirect stub at its old path: its `# Title` and one line linking the new page, nothing else.
- Links to `living-doc-utilities` point at `master` until the release repoints them to its tag. The one exception is the source of a copy, which names the version copied: `normalisation_cases.yaml` in `guides/authoring-documentation.md`.

## Invariants and gotchas

- `_integration/`: the repository is public. An internal target's configuration, log and artifacts stay on the machine; only its redacted report row is committed, under an `absa-N` label ([_integration/README.md](_integration/README.md)).
- Pages and tutorials marked *(planned)* describe intended behavior that no tool ships yet.
- `guides/authoring-documentation.md`'s before/after pairs are copied byte for byte from `living-doc-utilities` `living_doc_utilities/authoring/normalisation_cases.yaml` at `v0.8.0`, each under its case id. `tests/examples/examples_check.py` (rule 8) compares each with its case at the tag of the installed version and runs `normalize` over it; it parses each pair as a `**`<case id>`**:` line, then a ` ```text before ` and a ` ```text after ` block, so keep that shape. A move of the `living-doc-utilities` version fails it until the same PR brings the pairs and the version in the page in line ([CONTRIBUTING.md § Regenerating the collector snapshots](../CONTRIBUTING.md#regenerating-the-collector-snapshots)).
