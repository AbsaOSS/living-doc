# Living Documentation

**Living Documentation** is an approach to keeping project documentation continuously up to date by generating it directly from the systems teams already use — GitHub, Azure DevOps — instead of maintaining it by hand. 

This repository is the entry point for the whole topic: it explains the concept, the architecture, and links out to every tool in the ecosystem.

## Start here

- [Living Documentation in 5 Minutes](docs/introduction/quickstart.md) — copy one workflow file and go
- [What is Living Documentation?](docs/introduction/what-is-living-documentation.md) — the concept and why it exists
- [Architecture](docs/introduction/architecture.md) — how collectors, the toolkit, and generators fit together
- [Getting Started](docs/guides/getting-started.md) — set up your first pipeline

## Guides

- [Living Documentation Document Types](docs/guides/living-doc-document-types.md)
- [Collecting from GitHub](docs/guides/github-collection.md)
- [Collecting from Azure DevOps](docs/guides/azure-devops-collection.md)
- [Choosing a Generator](docs/guides/choosing-a-generator.md)

## Tutorials

One per **source + output** combination — see [Getting Started & Worked examples](docs/guides/getting-started.md#worked-examples) for the full matrix.

- [GitHub Issues → Markdown](docs/tutorials/gh-issues-to-markdown.md)
- [GitHub Source Code → Markdown](docs/tutorials/gh-source-to-markdown.md)
- [Azure DevOps Work Items → Markdown](docs/tutorials/ado-workitems-to-markdown.md)
- [User Stories → PDF](docs/tutorials/user-stories-to-pdf.md)
- [GitHub Source Code → PDF](docs/tutorials/gh-source-to-pdf.md)

## Ecosystem

The pipeline has four stages: content is **authored**, a **collector** mines it into a common JSON shape, the **toolkit** normalizes it into a canonical dataset, and a **generator** renders that dataset into a documentation format.

### Authoring

Content can be authored by hand or AI-accelerated — the pipeline itself always runs AI-free downstream of authoring. User Stories, Features, and Functionalities specifically can be authored two ways: directly in source code (preferred), or as issues/work items in GitHub or Azure DevOps.

### What gets mined

| Source | Objects | Status |
|---|---|---|
| GitHub | Issues (User Stories, Features, Functionalities), labels | Available |
| Source code | User Stories, Features, Functionalities, Gherkin test scenarios | Specced, not yet built |
| Azure DevOps | Work items | Planned |
| Azure DevOps | Boards, pipelines, test plans, release notes | Planned |

### Document types

What the pipeline produces. Each can be rendered as Markdown or PDF.

| Document type | Built from | Requires |
|---|---|---|
| **Technical project** — User Stories, Features, Functionalities | Mined from issues or source code (never hand-edited output) | A collector source |
| **Test catalog** — the behaviours covered by Gherkin scenarios | Mined from `.feature` files | Gherkin feature files in the repo |
| **Coverage matrix** — which acceptance criteria have tests | Cross-referencing the two above | Technical project **and** test catalog, for the same system |

The **technical project** has two views: *inner* (everything, as-is) and *release* (planned and no-longer-active / delivered ACs filtered out). Full structure, purpose, and the prerequisite matrix: [Living Documentation Document Types](docs/guides/living-doc-document-types.md).

### What you get

| Output | Best for | Status |
|---|---|---|
| Plain Markdown | Docs committed alongside code | Early stage |
| PDF | Point-in-time deliverables — user stories, UI test catalogs, coverage matrices | Available |

### Projects

| Project | Role | Purpose |
|---|---|---|
| [agentic-toolkit](https://github.com/AbsaOSS/agentic-toolkit) | Authoring acceleration (optional) | General-purpose AI-skills library; its `living-doc-bdd-copilot` agent + skill family *accelerates* authoring User Story/Feature/Functionality entities and Gherkin `.feature` files in the format `living-doc-collector-gh` mines — not required, since the whole pipeline runs AI-free and the same content can be hand-written. |
| [living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) | Collector | Mines a GitHub repository into JSON, in three toggleable modes: documentation issues (plus GitHub Projects state), living-doc header blocks in source code, and Gherkin UI-test scenarios. |
| [living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad) | Collector | Mines an Azure DevOps organization's work items into JSON. *(boards, pipelines, test plans, and release notes modes are planned, not yet built)* |
| [living-doc-utilities](https://github.com/AbsaOSS/living-doc-utilities) | Shared library | Core data models, transformation, and serialization logic shared by collectors, the toolkit, and generators. |
| [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) | Toolkit | Normalizes collector output into a canonical dataset consumed by generators. |
| [living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown) | Generator | Renders the canonical dataset as plain Markdown. *(early stage)* |
| [living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf) | Generator | Renders structured JSON (user stories, test catalogs, coverage matrices) as PDF via Jinja2 + WeasyPrint. |

See [docs/projects](docs/projects/) for a dedicated page per project. The table above describes the intended pipeline.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming, PR conventions, and how to report issues.

## License

Licensed under the [Apache License 2.0](LICENSE).
