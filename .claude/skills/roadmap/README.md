# Working with the roadmap skill

This guide is for the person who plans a release with the `roadmap` skill. The agent follows
[SKILL.md](SKILL.md), and the rules are in
[CONTRIBUTING.md § Planning ecosystem work](../../../CONTRIBUTING.md#planning-ecosystem-work).

## What it does

| Command | When | You get |
|---|---|---|
| `/roadmap goal <one sentence>` | you have a goal for a release | its column of the chain table, traced down to the canon and back up, after a few questions |
| `/roadmap cut` | the release's goals are complete | issue drafts for all columns, in landing order |
| `/roadmap found <what happened>` | something unexpected came up during the build | its class (replan, debt, candidate or retro note) and the drafted step |
| `/roadmap close` | the release has shipped | the leftovers moved, the retro, the closing comment |
| `/roadmap debt` | after the close | take, keep or close for each woken debt issue, and the next round's columns |

Plain words work as well, for example "add PDF output as a goal for v0.4.0".

## Prepare a goal

A good goal is one sentence plus done criteria, and each criterion has one example someone could check: an input,
and what they see.

| Weak | Strong |
|---|---|
| Better PDF support. | A project that runs the GitHub Source tutorial gets `technical-project-inner.pdf` next to the Markdown file, with the same chapters. |
| Unify the labels. | `gh label list` gives the same `type:*` labels in all seven `living-doc*` repositories, and each issue form sets one of them. |
| The tutorial should be easier. | A reader who copies § 2 of the tutorial into an empty repository gets the three documents from one push, with no edit except the paths. |

- Several small items that belong together, such as three debt issues on one topic, make one goal.
- Goals that aren't planned yet can wait in a local list that git doesn't track, for example `GOALS.md` at the
  repository root, listed in `.git/info/exclude`. Paste a goal from it into `/roadmap goal`.
- Start with the goal that changes the lower layers or the rules. Later columns build on what the earlier ones plan.

## During a column

- **Evidence.** Every "has" or "lacks" comes with a path, a line or a run's artifact. Open a few of them. Push back on
  any claim that has none.
- **Choices.** The agent asks one question at a time, each with real examples. If the examples don't settle it, ask for
  another one. Answer before the column closes: a choice may wait only when no layer above depends on it.
- **Closure.** Ask the agent to show the column's six closure rules, each one ticked. Don't cut while one fails.
- **Sessions.** A large goal can take more than one session. The working notes in `.local_context/roadmap/` carry the
  column over. Start the next session with `/roadmap goal`, and say "continue v0.4.0".

## The cut and the build

- Read the drafts repository by repository. An issue should be one pull request you can review in one sitting: split
  one that isn't, and merge two that change the same files.
- Filing needs `gh issue create` and `gh issue edit`. In auto mode, allow them with a permission rule, or file the
  drafts yourself.
- Once an issue is filed, don't edit it by hand. Use `/roadmap found`, and the replan logs the change in the epic.
- A pull request does its issue's acceptance criteria and nothing more. Everything else goes to `/roadmap found`,
  including "while I'm here" fixes.

## After the release

`/roadmap close` runs the retro. It lists what didn't go well: the retro notes, the replans, the edits of filed issues,
your corrections, and the steps that waited or failed twice. It proposes one change per item. Decide on each one; the
accepted changes land before the next release is planned. Then `/roadmap debt` picks the next round.

## Getting the best result

- Give real material: a document snippet, a run folder, a pull request link, a pilot's message.
- Say so at once when an assumption is wrong. The agent fixes the column, not only its reply.
- Keep the epic open in the browser. Its table is the plan.
- Don't change the planning rules during a release. Add a retro note instead.
