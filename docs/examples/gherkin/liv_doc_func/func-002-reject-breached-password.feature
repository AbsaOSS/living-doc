# =============================================================================
# LIVING DOC — FUNC-002 · Login Page - Reject Breached Password
# =============================================================================
# status:    planned
# parent:    FEAT-001
# func_type: field_validation
# feature_dependencies: FEAT-002
#
# acceptance_criteria:
#
#   AC:FUNC-002-01 (planned)
#     - Returns valid=false when the candidate password appears in the breached-password list.
# =============================================================================

@FUNC_ID:FUNC-002
@domain_authentication
Feature: Login Page - Reject Breached Password
  Rejects a candidate password that the breach check reports as compromised, before the login form is submitted.

  # No scenarios yet: the behaviour is planned, so its declared dependency on FEAT-002 is an
  # untested integration point - a declared edge with no linked scenario. That is what this
  # file shows, and it is deliberate.
