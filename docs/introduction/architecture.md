# Architecture

The ecosystem is split into three stages — **collect**, **normalize**, **generate** — connected by a shared JSON data shape defined in [living-doc-utilities](https://github.com/AbsaOSS/living-doc-utilities). Every project in the stack plugs into exactly one stage, which is what lets any collector feed any generator.

## Pipeline overview

```mermaid
flowchart LR
    subgraph Sources
        GH[(GitHub Issues & Labels,<br/>Repository Source Code)]
        AD[(Azure DevOps<br/>Work Items)]
    end

    subgraph Collect
        CGH[living-doc-collector-gh]
        CAD[living-doc-collector-ad]
    end

    subgraph Normalize
        TK[living-doc-toolkit]
    end

    subgraph Generate
        GM[living-doc-generator-markdown]
        GPDF[living-doc-generator-pdf]
    end

    subgraph Outputs
        OM[Markdown files]
        OPDF[PDF reports]
    end

    GH --> CGH
    AD --> CAD
    CGH -- JSON --> TK
    CAD -- JSON --> TK
    TK -- canonical dataset --> GM --> OM
    TK -- canonical dataset --> GPDF --> OPDF

    UTIL[living-doc-utilities<br/>shared models & serialization]
    UTIL -.-> CGH
    UTIL -.-> CAD
    UTIL -.-> TK
    UTIL -.-> GM
    UTIL -.-> GPDF
```

## Stage responsibilities

| Stage | Project(s) | Responsibility |
|---|---|---|
| Collect | `collector-gh`, `collector-ad` | Talk to one source system's API, mine issues / work items / labels / source code, emit JSON. |
| Shared model | `utilities` | Define the data models and (de)serialization logic every other project imports, so collector output and generator input agree on shape. |
| Normalize | `toolkit` | Take one or more collector outputs and produce a single canonical dataset — resolving format differences between sources. |
| Generate | `generator-markdown`, `generator-pdf` | Take the canonical dataset and render one target format. |

## Typical run (GitHub Action)

```mermaid
sequenceDiagram
    participant Trigger as Schedule / Push
    participant Collector as collector-gh
    participant Toolkit as toolkit
    participant Generator as generator-*
    participant Repo as Docs output (repo/site)

    Trigger->>Collector: run action
    Collector->>Collector: mine issues, labels, metadata
    Collector-->>Toolkit: JSON payload
    Toolkit->>Toolkit: normalize into canonical dataset
    Toolkit-->>Generator: canonical dataset
    Generator->>Generator: render target format
    Generator-->>Repo: commit / publish output
```

Each stage runs as an independent GitHub Action, so a pipeline is assembled by chaining actions in a workflow file — see [Getting Started](../guides/getting-started.md).
