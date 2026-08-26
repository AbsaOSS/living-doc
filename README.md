# Living Documentation

**Living Documentation** is an approach to keeping project documentation continuously up to date by generating it directly from the systems teams already use — GitHub, Azure DevOps — instead of maintaining it by hand. 

This repository is the entry point for the whole topic: it explains the concept, the architecture, and links out to every tool in the ecosystem.

## Start here

- [What is Living Documentation?](docs/introduction/what-is-living-documentation.md) — the concept and why it exists
- [Architecture](docs/introduction/architecture.md) — how collectors, the toolkit, and generators fit together
- [Getting Started](docs/guides/getting-started.md) — set up your first pipeline

## Guides

- [Collecting from GitHub](docs/guides/github-collection.md)
- [Collecting from Azure DevOps](docs/guides/azure-devops-collection.md)
- [Choosing a Generator](docs/guides/choosing-a-generator.md)

## Tutorials

- [GitHub Issues → Markdown](docs/tutorials/gh-issues-to-markdown.md)
- [Azure DevOps Work Items → Markdown](docs/tutorials/ado-workitems-to-markdown.md)
- [User Stories → PDF](docs/tutorials/user-stories-to-pdf.md)

## Ecosystem

The pipeline is: content gets **authored** in the source system (by hand, or AI-accelerated — the pipeline itself runs AI-free either way), a **collector** mines it into a common JSON shape, the **toolkit** normalizes it into a canonical dataset, and a **generator** renders that dataset into a documentation format.

TODO - there are two ways how to manage User Stories (US), Features (Feat), and Functionalities (Fund) - in source code preferred or in issues in GitHub or Azure DevOps
TODO - mdoc repo is depreated, as this path was ABSA internal solution, which is no more supported

| Project | Role | Purpose |
|---|---|---|
| [agentic-toolkit](https://github.com/AbsaOSS/agentic-toolkit) | Authoring acceleration (optional) | General-purpose AI-skills library; its `living-doc-bdd-copilot` agent + skill family *accelerates* authoring User Story/Feature/Functionality entities and Gherkin `.feature` files in the format `living-doc-collector-gh` mines — not required, since the whole pipeline runs AI-free and the same content can be hand-written. |
| [living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) | Collector | Mines a GitHub repository's issues, labels, and metadata into JSON. |
| [living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad) | Collector | Mines an Azure DevOps organization's work items into JSON. *(boards, pipelines, test plans, and release notes modes are planned, not yet built)* |
| [living-doc-utilities](https://github.com/AbsaOSS/living-doc-utilities) | Shared library | Core data models, transformation, and serialization logic shared by collectors, the toolkit, and generators. |
| [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) | Toolkit | Normalizes collector output into a canonical dataset consumed by generators. |
| [living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown) | Generator | Renders the canonical dataset as plain Markdown. *(early stage)* |
| [living-doc-generator-mdoc](https://github.com/AbsaOSS/living-doc-generator-mdoc) | Generator | Renders GitHub issue/label data as Markdown formatted for an MDoc viewer. |
| [living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf) | Generator | Renders structured JSON (user stories, test catalogs, coverage matrices) as PDF via Jinja2 + WeasyPrint. |

See [docs/projects](docs/projects/) for a dedicated page per project. The table above describes the intended pipeline.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming, PR conventions, and how to report issues.

## License

Licensed under the [Apache License 2.0](LICENSE).
