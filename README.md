# Living Documentation

## Purpose

Living Documentation generates a project's documentation from what its repository already holds: User Story,
Feature and Functionality headers in source code, and Gherkin `.feature` files. The documentation is regenerated on
every run, so it never drifts from the work. This repository is the ecosystem's entry: the concept, the shape of the
system, the format canon, and one card per repository.

This documentation describes `v0.1.0`. For another tag, see that release's notes.

## Contents

- [Where to start](#where-to-start)
- [The idea](#the-idea)
- [Reference](#reference)
- [Projects](#projects)
- [Contributing](#contributing)
- [License](#license)

## Where to start

**I want documentation out of my repository.**

1. [Living Documentation in 5 Minutes](docs/introduction/quickstart.md): is this for me, and what do I prepare?
2. [Choosing a documentation source](docs/guides/choosing-a-documentation-source.md): what the pipeline mines.
3. [Build a pipeline](docs/guides/build-a-pipeline.md): collect, normalize, generate, and the tutorial to copy.

**I write the User Stories.**

1. [Authoring documentation](docs/guides/authoring-documentation.md): write it like this.
2. [Authoring formats](docs/reference/authoring-formats.md) and [Glossary](docs/reference/glossary.md): the exact
   layouts and the entity model.
3. [Example corpus](docs/examples/README.md): a worked mini project to copy.

**I build on these contracts, or change this repository.**

1. [Projects](#projects): which repository does what.
2. [Contracts](docs/reference/contracts.md): the six contracts, and which component writes and reads each.
3. [CONTRIBUTING.md](CONTRIBUTING.md): branches, pull requests, the page rules and the checks.

## The idea

An author writes each User Story, Feature and Functionality once, as a header in source code, by hand or with the
optional AI layer. A **collector** mines the headers and the test scenarios, the **toolkit** normalizes them into one
canonical shape, and a **generator** renders a document from it. Each stage is a GitHub Action, and the pipeline
runs AI-free. GitHub issues and Azure DevOps work items as sources, and PDF output, are planned.

- The concept and the problem it solves: [What is Living Documentation?](docs/introduction/what-is-living-documentation.md)
- The stages and how one run flows: [Architecture](docs/introduction/architecture.md)
- What each part does and must not do: [Principles](docs/introduction/principles.md)
- The three documents a pipeline renders: [Document types](docs/guides/living-doc-document-types.md)

## Reference

- [Glossary](docs/reference/glossary.md): the entity model, the IDs and the acceptance-criterion grammar.
- [Authoring formats](docs/reference/authoring-formats.md): the exact header layouts an author writes.
- [Rendering rules](docs/reference/rendering-rules.md): what each view of a document shows, and how coverage is counted.
- [Data flows](docs/reference/data-flows.md): which component writes and which reads each file.
- [Contracts](docs/reference/contracts.md): the six contracts between the components.
- [Error codes](docs/reference/errors.md): every error and warning code, what it means and what to do.

## Projects

| Repository | Role | Card |
|---|---|---|
| [`agentic/`](agentic/README.md), in this repository | Authoring acceleration, optional | [agentic](docs/projects/agentic.md) |
| [living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) | Collector: GitHub | [collector-gh](docs/projects/collector-gh.md) |
| [living-doc-collector-ad](https://github.com/AbsaOSS/living-doc-collector-ad) | Collector: Azure DevOps, planned | [collector-ad](docs/projects/collector-ad.md) |
| [living-doc-utilities](https://github.com/AbsaOSS/living-doc-utilities) | Shared library: contracts and parsers | [utilities](docs/projects/utilities.md) |
| [living-doc-toolkit](https://github.com/AbsaOSS/living-doc-toolkit) | Normalizer | [toolkit](docs/projects/toolkit.md) |
| [living-doc-generator-markdown](https://github.com/AbsaOSS/living-doc-generator-markdown) | Generator: Markdown | [generator-markdown](docs/projects/generator-markdown.md) |
| [living-doc-generator-pdf](https://github.com/AbsaOSS/living-doc-generator-pdf) | Generator: PDF, planned | [generator-pdf](docs/projects/generator-pdf.md) |

## Contributing

Report a bug or propose a feature in [GitHub Issues](https://github.com/AbsaOSS/living-doc/issues). Branches, pull
requests, the page rules and the checks: [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Licensed under the [Apache License 2.0](LICENSE).
