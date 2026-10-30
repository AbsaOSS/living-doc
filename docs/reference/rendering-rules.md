# Rendering rules

## Purpose

This page explains what each view of a technical project shows and drops, and how a coverage matrix counts
acceptance criteria. The normative rules are `living-doc-utilities`'
[Rendering](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md) page; each
line below links the rule it explains, and no table is restated.

Read before: [Living Documentation Document Types](../guides/living-doc-document-types.md) · Next: [Glossary](glossary.md)

## Contents

- [Views](#views)
- [What was not loaded](#what-was-not-loaded)
- [Coverage](#coverage)

## Views

A technical project is generated in one of two views, inner or release, from the same mined data; the view selects
records and changes nothing that was authored
([Records and presentation](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#records-and-presentation)).

- **Inner** shows everything as authored: entities and criteria in every state, and what was not loaded from the
  input ([Fields by view](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#fields-by-view)).
- **Release** shows what was shipped: it drops `planned` and `in_review` entities and criteria, and keeps
  `deprecated` ones, which still describe shipped behaviour
  ([Records and presentation](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#records-and-presentation)).
- A dropped entity takes its criteria with it; a `deprecated` criterion on a kept entity stays.
- Every authored field reaches the generator at the level it was authored: an entity's preconditions are not
  copied into its criteria, and a criterion's own ones show under it as "also …"
  ([Records and presentation](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#records-and-presentation)).
- A Feature is kept or dropped by the state derived from its Functionalities; the release view badges it only when
  it is deprecated ([Fields by view](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#fields-by-view)).
- The release view hides what only the team needs: a Feature's stub reason and an entity's deprecation date and
  reason ([Fields by view](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#fields-by-view)).
- Both views show every criterion header in its canonical form
  ([Fields by view](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#fields-by-view)).

## What was not loaded

A collector that cannot read part of an input reports it as a warning and goes on; the run does not fail on it
(see [Authoring formats — Indentation](authoring-formats.md#indentation)). The inner view shows each warning under
the entity it names: its code, its message and its line, with a link to that line in the source — never the
warning's raw `context`. Every collector warning that names an entity is shown, not only a dropped criterion
(`MALFORMED_AC`): each one means something the author wrote did not reach the document. A collector warning that
names no entity, or an entity the document does not hold — `MISSING_ENTITY_ID`, whose entity was never emitted —
is shown once, for the whole document, with its file and line. The release view shows none of them
([Fields by view](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#fields-by-view)).
The codes are listed in
[`living-doc-utilities`' error codes](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/errors.md#codes).

## Coverage

A coverage matrix answers one question per acceptance criterion: does a test cover it? Coverage is per declared
value; [AC variants](authoring-formats.md#ac-variants) defines the three verdicts.

- `active` and `deprecated` criteria are counted, in both views: a deprecated criterion still describes shipped
  behaviour ([Coverage](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#coverage)).
- `in_review` criteria are not counted: collection runs against `master`, where the tests for work in review do
  not exist yet. A scenario linked to one is the warning `IN_REVIEW_AC_HAS_TESTS`, which usually means the work
  merged and its state was not updated ([Coverage](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#coverage)).
- `planned` criteria, backlog or targeted, are not counted: tests ahead of the implementation are fine, and
  counting unbuilt work would lower the figure. A scenario linked to one is the warning `PLANNED_AC_HAS_TESTS`
  ([Coverage](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#coverage)).
- The coverage figure weighs each counted criterion: covered counts 1, not covered 0, and partly covered its
  share of values, so **1/3** adds a third
  ([Coverage summary](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#coverage-summary)).
- A matrix's view changes how it is presented, never which criteria are counted
  ([Coverage](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#coverage)).
- The summary of planned work — how many criteria are planned, in the backlog and per target version — appears in
  the inner view only
  ([Planned work summary](https://github.com/AbsaOSS/living-doc-utilities/blob/v0.8.0/docs/contracts/rendering.md#planned-work-summary)).
