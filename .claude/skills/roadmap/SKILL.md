---
name: roadmap
description: Plan an ecosystem release of the living-doc repositories as a chain table, in conversation with the owner. Adds a goal as a column, traced from its visible result down to the canon and designed back up; cuts the release's issues from all closed columns; classifies a finding made while the release is built; closes a shipped release with a retro of what didn't go well; reviews the debt the release woke. Use when the owner gives a goal or a group of goals, asks what a goal needs across the repositories, wants the issues of a release, reports a finding or a process problem during the build, closes a release, or asks for the debt review.
---

# Roadmap

This skill is how an agent runs [CONTRIBUTING.md § Planning ecosystem work](../../../CONTRIBUTING.md#planning-ecosystem-work)
with the owner. That section is the version for people. When the two disagree, CONTRIBUTING.md wins, and this skill
gets fixed.

There are five modes: `goal`, `cut`, `found`, `close` and `debt`. The owner names one, as in `/roadmap goal <goal>`,
or describes the need; pick the mode that fits. The owner's guide is [README.md](README.md).

Planning is a conversation:

- Ask one decision at a time with AskUserQuestion. Give your recommendation, and show real examples: an input,
  today's output, and the output under each option.
- Reply in the owner's language. Issue, epic and PR texts stay English.
- Never write to GitHub before the owner has seen the text and said yes.

## The release epic

- Each release has one epic in this repository. It is labelled `type:epic` and titled `Ecosystem release vX.Y.Z`.
- The epic body is the only place the plan's state lives. Start it from [epic-template.md](epic-template.md).
- Progress is the state of the epic's sub-issues. Nothing is ticked by hand, and no other file mirrors it.
- Working notes go in `.local_context/roadmap/vX.Y.Z.md`. They hold each column's two passes with their evidence until
  the column's issues are cut. After the cut, delete them: the issues hold the facts.
- Edit the epic body only for these: a column joins, the cut, a finding (a replan, a candidate or a retro note), and
  the release shipping.

## The chain table

Each column is a goal. Each row is a layer, listed from the end of the chain down to the canon:

| Row | What it holds |
|---|---|
| End | what someone sees once the goal is met: each done criterion with one example, an input and what comes out |
| `living-doc` integration | tutorials, the integration runner, the testbed checks |
| `living-doc-testbed` | the input that proves the result |
| `living-doc-generator-markdown` | what gets rendered |
| `living-doc-toolkit` | what gets normalized, filtered and cross-referenced |
| `living-doc-collector-gh` | what gets collected |
| `living-doc-utilities` | contracts, parsers and rules |
| Canon | this repository's `docs/reference/`, the document types guide, and the frame in Principles |

- `living-doc-generator-pdf`, `living-doc-collector-ad` and the agentic layer get a row only when a goal touches them.
- `living-doc` is the repository that ties the others together. It holds the canon, the integration, the epic and the
  release, so one goal may have several issues here.

Each cell has two halves:

- **missing**, filled by the down pass;
- **change**, filled by the up pass.

A cell with nothing missing reads `✓`, followed by its evidence.

## Mode `goal`: add a column

1. **Intake.** The owner gives one sentence and the done criteria.
   - Each criterion needs one observable example. Ask for it when it is missing.
   - A group of small goals, for example several debt issues of one topic, makes one column.
2. **Baseline.** Each row starts from two things:
   - its repository's `origin/master`: fetch the sibling clones, or clone with `git clone --filter=blob:none`;
   - every change the earlier columns of this release plan for that row.
3. **Down pass.** Work from End down. For each row, ask: what must this layer have or receive so that the row above it
   can deliver? Does it have that on the baseline?
   - Use real evidence. The newest committed run under `docs/_integration/` holds the output of each layer:
     `collector-gh/`, `toolkit/`, and the documents. The code gives a `file:line`.
   - Send one Explore agent per row, in parallel. Give each the row's question and the evidence it needs. Each agent
     returns "has" or "lacks", with paths and lines.
   - Every "missing" names the requirement from the row above that caused it.
   - The pass ends at the canon. Record what the canon says, what it leaves out, and what it contradicts.
4. **Choices.** Where a row could go more than one way, the owner decides now, from examples.
   - A question may stay open on its issue only when no row above depends on the answer.
   - A question that needs an experiment, or someone else's input, becomes a spike. The column waits for the spike's
     answer.
5. **Up pass.** Work from the canon up, and write each row's change:
   - The lowest row that introduces an interface defines it exactly. An interface is a contract field, an action
     input, a file name or a code. Rows above name it and never restate it.
   - A row's "what must work" example uses only inputs that exist when its work starts: its repository's fixtures, or
     changes from rows below.
   - A row that an earlier column already covers reads "covered by <column>". A row that extends an earlier column's
     change says what it adds.
6. **Closure.** The column is closed when all six hold:
   1. End has an observable example for every done criterion.
   2. Every "missing" has a change in its row, or the owner took it out of the goal. Taking it out changes the done
      criteria, not the chain.
   3. Every input a change consumes either exists on the baseline, with evidence, or is made by a row below, in this
      column or an earlier one.
   4. Every interface is defined in exactly one cell.
   5. Every "what must work" example uses only inputs that exist when its work starts.
   6. No decision that a row above depends on is still open.
7. **Record.** Show the column to the owner, then add it to the epic's goals and table.

A goal that is agreed after the cut joins the release only while none of the rows it touches has started. Otherwise
it becomes a candidate for the next release.

## Mode `cut`: issues from all columns

When the owner closes the release's set of goals, cut the issues from every column at once, using what all of them
plan.

### Size

- An issue is one reviewable PR in one repository.
- Cells of several goals in one repository merge into one issue when they change the same files or the same
  interface, and stay reviewable together.
- A large cell splits along its independent parts.
- Each issue names the cells it delivers.

### Fields

Use the repository's issue form and labels: `type:*` in `living-doc` and `living-doc-generator-markdown`, plain names
in the other repositories. Each issue carries:

- what is missing, and why;
- the change;
- a "what must work" example at that layer;
- numbered acceptance criteria;
- the canon criterion, which names the canon row's issue or the canon pages the change agrees with.

### Order

The issues land in this order, bottom-up:

1. **The canon issue** lands first. Each page it changes says, in one line, that the part is planned for the release.
   The exception is a statement that a check compares with a pinned release. Examples are the codes in
   `docs/reference/errors.md` and the before/after pairs in the authoring guide, which `tests/examples/examples_check.py`
   compares. Such a statement lands with the PR that moves that pin.
2. **`living-doc-utilities`.** The last criterion of its last issue is the final release, `0.N.0`, and the components
   pin it. Cut a release candidate only when someone must use the version before its release.
3. **`living-doc-collector-gh`, `living-doc-toolkit` and `living-doc-generator-markdown`.** The last criterion of each
   one's last issue sets its version and re-pins `living-doc-utilities`. That is step 1 of its `DEVELOPER.md`
   § Release.
4. **`living-doc-testbed`, then the `living-doc` integration.** A check that guards a lower repository lands before
   what it guards.
5. **The release.** One issue per PR that
   [§ Releasing the ecosystem](../../../CONTRIBUTING.md#releasing-the-ecosystem) lands.

### Filing

1. Draft every issue and show them to the owner.
2. On the owner's yes, file them as sub-issues of the epic, in landing order.
3. Put each issue's link in its cells of the table, then delete the working notes.

After filing, an issue's body changes only through a replan.

## Mode `found`: a finding during the build

Classify each finding as soon as it is found. Never fix it in the PR that is running.

| Class | Test | Action |
|---|---|---|
| Blocks the goal | a done criterion can't be met without it | **Replan.** Rerun the column from the row the finding hits. A new cell becomes a new issue; a changed cell gets one edit of its issue. Add a line to the epic's Replans: date, cell and cause. |
| Doesn't block | the goal is met without it | **Debt.** File an issue in the repository at fault, labelled tech debt, with a topic and the wake tag `when:release`. Its row joins the next sync of [the debt overview](../../../docs/_backlog/debt-overview.md). |
| A new need | it adds an observable result | **Candidate.** Add a line under the epic's Candidates, for a later release. |
| A process problem | a planning, PR or release rule made the work slower or worse | **Retro note.** Add a line under the epic's Retro, with what happened and where. The retro decides it; the rules don't change during the release. |

When a blocking finding hits `living-doc-utilities` after its release, the fix is a patch or minor release, never a
release candidate.

## Mode `debt`: the review after a release

After each release of goals:

1. List the debt overview's rows that the release woke: every `when:release` row, plus every tag the owner names.
   Read each issue.
2. For each one, propose an outcome and give the reason:
   - **take** it into the next round;
   - **keep** it, with the wake tag that fits now;
   - **close** it, because it is done or no longer true.
3. What the owner takes becomes the next release's columns: one column per group that belongs together, by one topic
   or one canon area. Run `goal` for each column.

Rounds alternate: a release of goals, then a release of the debt this review picked.

## Mode `close`: closing a release

When the release has shipped:

1. Turn every open line of the epic into debt or a candidate, through `found`.
2. **Retro.** Collect what didn't go well, and treat each item as a chance to improve the process:
   - the epic's Retro notes;
   - every replan, and every edit of a filed issue made outside a replan;
   - every correction the owner made to a plan, an issue or a PR;
   - every step that waited, failed twice, or was done by hand when a rule could have done it.

   For each item, name its cause and propose one change to this skill, to CONTRIBUTING.md § Planning ecosystem
   work or to § Releasing the ecosystem. The owner decides on each one. The accepted changes land in one PR before the
   next release is planned. Report the counts too: replans and edits outside a replan should both be zero.
3. Close the epic with a comment that names where each leftover went and which process changes were accepted.
4. Run `debt`.

## Rules that hold through a release

- The issue is the contract. Its PR delivers its acceptance criteria and nothing else.
- The planning rules a release starts with hold until it ships. A proposed change to them is a Retro note, decided
  when the release closes.
