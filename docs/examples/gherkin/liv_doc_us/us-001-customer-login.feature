# =============================================================================
# LIVING DOC — US-001 · Customer Login
# =============================================================================
# source:          https://github.com/AbsaOSS/living-doc/issues/9    ← optional
# status:          active
# business_value:
#   - Registered customers can reach their account area, so returning users
#     convert without friction.
#
# acceptance_criteria:
#
#   AC:US-001-01 (v1.0.0 - active)
#     - A customer who submits valid credentials lands on the account dashboard.
#     preconditions:                      ← optional; AC-level extension (one optional field for this file)
#       - A registered customer account exists and is not locked.
#
#   AC:US-001-02 (v1.0.0 - active)
#     - An inline error is shown when the customer submits invalid credentials,
#       without leaving the login screen.
# =============================================================================

@US_ID:US-001
Feature: Customer Login
  As a registered customer, I can sign in with my email and password, so that I can reach my account area.

  # AC:US-001-01 (v1.0.0 - active) — valid credentials land on the account dashboard
  @AC:US-001-01
  Scenario: Customer signs in with valid credentials
    Given a registered customer is on the login screen
    When the customer submits valid credentials
    Then the account dashboard is displayed

  # AC:US-001-02 (v1.0.0 - active) is intentionally left UNCOVERED —
  # no scenario carries @AC:US-001-02, so it is reported as an uncovered AC
  # in the coverage matrix. AC:US-001-01 above is the covered counterpart.
