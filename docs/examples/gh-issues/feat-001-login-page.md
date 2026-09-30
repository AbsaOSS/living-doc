<!--
GitHub issue body for a Feature mined by collector-gh `doc-issues`.
Label: DocumentedFeature    Title: FEAT-001 · Login Page
A Feature carries no `## Status` and no `## Deprecated At`: its state is derived from its
Functionalities, and the deprecation date is derived with it.
`## Notes` is the corpus's single instance of the entity-level note section.
Layout: see ../README.md (GitHub issue-body layout)
-->

## Description

The screen where a registered customer enters an email and password to sign in.

## Surface Type

UI

## Owners

Identity Team

## User Stories

US-001

## Functionalities

FUNC-001, FUNC-002

## External Dependencies

auth-api

## Notes

- The sign-in form markup comes from the shared identity template, so the surface can change without
  any commit in this repository.
- The customer-facing name of this screen is "Sign in"; "Login Page" is the internal name the team and
  the test suite use.
