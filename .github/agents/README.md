# `.github/agents/` — this repository's own development agents

These agents help develop **this** repository. They are not published, not installed into anyone's
project, and have nothing to do with the agentic layer under `agentic/`. `.claude/README.md` calls
them "the board" and treats them as the source of truth for role behaviour.

This page exists because the boundary below was implicit and was crossed once: `eval-runner` was
first added under `agentic/agents/`, next to the agent users install, although it is a development
tool for testing the layer.

## Which directory

| | `.github/agents/` | `agentic/agents/` |
|---|---|---|
| What it is | a development agent of this repository | the agent the **agentic layer ships** |
| Who runs it | a maintainer working in this checkout | a user who installed the layer, by `@`-mention in their own project |
| Frontmatter | `name:` + `description:` | `description:` + `tools:` |
| Guide | none | `agentic/docs/guides/<name>.md` |
| Eval set | none — see below | `agentic/agents/evals/<name>/` |
| Listed in | this page, and `.claude/README.md` where it drives a command | `agentic/README.md` § Agent |

**The test:** would this agent be useful to someone who installed the layer into their own project
and never opens this repository? If no, it belongs here.

## Conventions for an agent here

- One file, `<name>.agent.md`, frontmatter `name:` and `description:` only. No `tools:` key — the
  five original agents have none, so platform defaults apply. Adding one buys little: any agent
  granted terminal access can reach everything anyway, so a narrow list reads as a guarantee it
  does not provide. Put the real constraints in the body, as hard stops, and rely on review.
- `description:` says what the agent does **and what it must not do**. For an agent that writes to
  the tree, name the forbidden actions explicitly; that line is the first thing a reader sees.
- No eval set, and none is expected. `agentic/docs/testing/agent-testing.md` covers the shipped
  agent and says these are "a different thing and not covered". If one of these agents ever needs
  measuring, decide where its evals live before writing them — do not assume
  `agentic/agents/evals/`, which belongs to the layer.
- No guide page. The agent file is the documentation.

## The board

| Agent | Role |
|---|---|
| `specification-master` | Specification and planning behaviour |
| `senior-developer` | Implementation behaviour |
| `sdet` | Automated test coverage, determinism, fast feedback |
| `reviewer` | Correctness, performance, contract stability; invoked by `/verify-pr-ready` |
| `devops-engineer` | CI, workflows, release plumbing |
| `eval-runner` | Runs the agentic layer's eval suite per `agentic/docs/testing/eval-protocol.md` |
