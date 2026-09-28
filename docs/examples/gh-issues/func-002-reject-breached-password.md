<!--
GitHub issue body for a Functionality mined by collector-gh `doc-issues`.
Label: DocumentedFunctionality    Title: FUNC-002 · Login Page - Reject Breached Password
The dependency on FEAT-002 is authored in the `.feature` form of this Functionality; this form
spends its one optional field extension on the Preconditions section instead.
Layout: see ../README.md (GitHub issue-body layout)
-->

## Description

Rejects a candidate password that the breach check reports as compromised, before the login form is submitted.

## Status

planned

## Parent Feature

FEAT-001

## Func Type

field_validation

## Preconditions

- The breach check is reachable from the login surface.

## Acceptance Criteria

### AC:FUNC-002-01 (planned)

- Returns valid=false when the candidate password appears in the breached-password list.
