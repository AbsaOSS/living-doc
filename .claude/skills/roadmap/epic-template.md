# Release epic template

Copy everything below the rule into the body of the release epic, which is titled `Ecosystem release vX.Y.Z` and
labelled `type:epic`.

The headings follow the epic issue form:

| Heading | What it holds |
|---|---|
| Background | why the release exists |
| Goals | one block per column |
| Subtasks | the chain table, the release issues, the replans, the candidates and the retro notes |
| Related / References | links to earlier work |

A cell holds one line, the row's change. After the cut it holds the issue's link instead. GitHub shows each issue's
state, so nothing in the body is ticked by hand.

---

### Background

<Two or three sentences on where the goals come from, such as a pilot's feedback or the debt review after
`vX.Y.W`, and what the release ships.>

### Goals

**G1: <goal in one sentence>**

- <done criterion>: <example: an input, and what someone sees>

**G2: <goal in one sentence>**

- <done criterion>: <example>

### Subtasks

Every issue is a sub-issue of this epic, in landing order.

| Row | G1 | G2 |
|---|---|---|
| End | <what someone sees> | <what someone sees> |
| `living-doc` integration | <change, then #issue> | ✓ <evidence> |
| `living-doc-testbed` | | |
| `living-doc-generator-markdown` | | |
| `living-doc-toolkit` | | |
| `living-doc-collector-gh` | | |
| `living-doc-utilities` | | |
| Canon | | |

**Release:** <the release issues, one per PR that CONTRIBUTING.md § Releasing the ecosystem lands>

**Replans**

- <date>, <row × goal>: <cause> → <issue>

**Candidates**

- <a new need, for a later release>, found in <issue>

**Retro**

- <what made the work slower or worse, and where>; the retro decides it when the release closes

### Related / References

- <the previous release's epic, and the debt review that picked this release's debt goals>
