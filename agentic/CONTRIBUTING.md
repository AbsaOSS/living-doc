# Contributing to the agentic layer

This covers changes to the skills, the agent and their reference documents under `agentic/`. For
branch naming, PR naming and the repository's general conventions, see the root
[CONTRIBUTING.md](../CONTRIBUTING.md). For what the layer is and how to install a skill, see
[README.md](README.md).

The layer is optional: the living-doc pipeline is AI-free and runs without it. A change here
cannot break a collector, the toolkit or a generator — but it can mislead an author, so the canon
it describes has to stay exact.

## Running the tests locally

Each skill's Python scripts are covered by `test_*.py` files next to them. They are standalone
scripts, not pytest tests — each asserts in plain functions and exits non-zero from its own
`__main__` block:

```bash
pip install -r agentic/requirements-agentic-tests.txt
find agentic/skills -type f -name "test_*.py" | sort | xargs -n1 python
```

> **A bare `pytest` tells you nothing here.** Every one of these files carries
> `__test__ = False`, so `pytest` collects none of them and reports success. Use the command
> above, which is what CI runs.

They must pass on **Python 3.10** as well as 3.14: 3.10 is the floor `living-doc-utilities`
declares, and a skill's scripts run under whatever interpreter the user's project has.

Validating a skill's folder format needs Python 3.11 or newer, because `skills-ref` does:

```bash
pip install -r agentic/requirements-skill-lint.txt
agentskills validate agentic/skills/<name>
```

After changing a canon page under `docs/`, regenerate the copies the skills read:

```bash
bash agentic/scripts/sync-canon-copies.sh all
```

CI (`.github/workflows/agentic-tests.yml`) runs all three: the script tests on 3.10 and 3.14, the
skill-format validation, and a canon-copy check that fails when a committed copy differs from what
the script generates for that commit.

## Testing a skill or the agent

CI proves the scripts work. It says nothing about whether a skill *behaves* well — whether it
triggers on the right prompts and produces the right output. That is eval work, it is manual, and
it has its own guides.

Before starting a loop, see what material exists and that none of it is broken:

```bash
python agentic/scripts/evals-inventory.py              # body and trigger counts per skill
python agentic/scripts/evals-inventory.py --check      # shape only, exit 1 on a problem
python agentic/scripts/evals-inventory.py <skill>      # one skill
```

It is an aid, not a test, and deliberately not in CI — nothing here runs an eval. The guides:

- [docs/testing/skill-testing.md](docs/testing/skill-testing.md) — eval cases, fixtures,
  with/without comparison, the regression-first loop, trigger testing, description optimisation
- [docs/testing/agent-testing.md](docs/testing/agent-testing.md) — body evals for `.agent.md`,
  which is `@`-mentioned rather than auto-triggered

Nothing in this repository executes an eval. The files under `evals/` are the source material for
those loops.

## Pull request checklist

For a change to a skill:

- [ ] Folder name matches the `name` frontmatter field exactly
- [ ] `name` is kebab-case, 64 characters or fewer, no consecutive hyphens
- [ ] `description` covers both *what it does* and *when to trigger*, and carries a `NOT for:`
      boundary clause
- [ ] `description` is 1024 characters or fewer and not padded with filler
- [ ] `SKILL.md` body is under 500 lines, or uses progressive disclosure via `references/`
- [ ] No credentials, secrets or internal paths in the body or in any script
- [ ] Every script in `scripts/` is referenced from `SKILL.md` with usage guidance
- [ ] The description does not shadow or conflict with another skill's
- [ ] Evals exist, or a note in the PR says why they do not apply
- [ ] `agentskills validate agentic/skills/<name>` passes
- [ ] The skill is listed in the catalog table in [README.md](README.md)

For a change to the agent:

- [ ] Every tool the body references is in the frontmatter `tools:` list
- [ ] Scope boundaries match the `## Scope` and `## Does NOT` sections
- [ ] Mode dispatch still fires on its keywords, and handoff targets are right

For any change here:

- [ ] The script tests pass on 3.10 and 3.14
- [ ] If a canon page changed, the copies are regenerated in the same commit
- [ ] No hand edit to a generated copy under `skills/shared/references/`
- [ ] The layer writes the release canon: one dash in a structural position, the four AC states
      with `(planned)` for backlog, authored status on User Stories and Functionalities only, no
      Feature status, no `descoped` or `future_release`
