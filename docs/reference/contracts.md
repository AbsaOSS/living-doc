# Contracts

## Purpose

This page shows which component writes and which reads each of the six contracts, summarising `living-doc-utilities`'
[Documentation contracts](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts.md), where every
contract and rule is defined. It restates no rule.

Read before: [Data flows](data-flows.md) · Next: [Error codes](errors.md)

## Contents

- [The six contracts](#the-six-contracts)
- [The metadata envelope](#the-metadata-envelope)
- [Identity and state](#identity-and-state)
- [Rules](#rules)

## The six contracts

Each file's record roots, and the roles behind each writer and reader:
[Artifact rules — Contracts](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/artifact-rules.md#contracts).
Where each file lands: [Data flows — Files](data-flows.md#files).

| Contract | Artifact | Written by | Read by |
|---|---|---|---|
| `doc-source-v1.0.0` | `doc-source.json` | `collector-gh`, mode `doc-source` | `toolkit` `normalize-docs` and `coverage-matrix` |
| `ui-tests-v1.0.0` | `ui-tests.json` | `collector-gh`, mode `ui-tests` | `toolkit` `normalize-tests` and `coverage-matrix` |
| `generator-ready-v1.0.0` | `generator-ready.json` | `toolkit` `normalize-docs` | `generator-markdown`, document type `technical-project` |
| `ui-test-catalog-v1.0.0` | `ui-test-catalog.json` | `toolkit` `normalize-tests` | `generator-markdown`, document type `ui-test-catalog` |
| `coverage-matrix-v1.0.0` | `coverage-matrix.json` | `toolkit` `coverage-matrix` | `generator-markdown`, document type `coverage-matrix` |
| `doc-entities-v1.0.0` | `doc-entities.json` | planned: `collector-gh` mode `doc-issues`, `collector-ad` | planned: `toolkit` |

## The metadata envelope

Every file carries one `metadata` object, the same model in all six contracts. It records the tool that wrote the
file and its `living-doc-utilities` version, the CI run, the project and the systems the data came from, when the file
was written, and the file's own counts. A `toolkit` output also lists the files it was made from. Its fields:
[The metadata envelope](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/artifact-rules.md#the-metadata-envelope).

## Identity and state

- `entity_id`: the id authored in an entity's header, such as `US-001`; every file joins on it
  ([Entity identity](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/entities-and-state.md#entity-identity)).
- `source_ref`: where the entity was read, with a link back to it; nothing joins on it
  ([Entity identity](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/entities-and-state.md#entity-identity)).
- `state_origin`: whether a person wrote the entity's state or the pipeline derived it, as for every Feature
  ([State and state origin](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/entities-and-state.md#state-and-state-origin)).

## Rules

Every contract rule, R1 to R13 and the named rules, is listed one line each in
[Documentation contracts — Rules](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts.md#rules),
and each line links the page that defines it.
