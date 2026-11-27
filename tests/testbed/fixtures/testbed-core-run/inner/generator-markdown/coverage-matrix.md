# Coverage matrix

*View: inner*

## Summary

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 88.2% | 24 | 20 | 2 | 2 |

## Planned work

Planned criteria are not counted.

- **Planned:** 5
- **Backlog:** 2
- **v1.2.0:** 3

## User Stories

### US-001

**US-001 · Borrow a Book** `ACTIVE`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 66.7% | 3 | 2 | 0 | 1 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| US-001-01 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_us/us-001-borrow-a-book.feature/member-borrows-an-available-book |
| US-001-02 | active | `NOT COVERED` | — |
| US-001-04 | deprecated | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_us/us-001-borrow-a-book.feature/member-is-offered-a-loan-slip |

### US-002

**US-002 · Join the Library** `ACTIVE`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 100.0% | 3 | 3 | 0 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| US-002-01 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_us/us-002-join-the-library.feature/applicant-joins-the-library |
| US-002-02 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_us/us-002-join-the-library.feature/applicant-joins-the-library |
| US-002-03 | active | `COVERED` | per aspect, below |

**US-002-03** `COVERED`

| Aspect | Status | Scenarios |
|---|---|---|
| adult | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_us/us-002-join-the-library.feature/adult-applicant-gets-an-adult-card |
| junior | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_us/us-002-join-the-library.feature/junior-applicant-gets-a-junior-card |

### US-003

**US-003 · Register at the Desk** `DEPRECATED`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 100.0% | 1 | 1 | 0 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| US-003-01 | deprecated | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_us/us-003-register-at-the-desk.feature/desk-staff-register-a-resident |

## Functionalities

### FUNC-001

**FUNC-001 · Catalogue Search Page - Filter Search Results** `ACTIVE`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 75.0% | 2 | 1 | 1 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| FUNC-001-01 | active | `PARTIALLY COVERED` 1/2 | per aspect, below |
| FUNC-001-02 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-001-filter-search-results.feature/clearing-the-filters-restores-every-result |

**FUNC-001-01** `PARTIALLY COVERED` 1/2

| Aspect | Status | Scenarios |
|---|---|---|
| author | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-001-filter-search-results.feature/filtering-by-author-keeps-only-that-authors-books |
| subject | not covered | — |

### FUNC-002

**FUNC-002 · Catalogue Search Page - Sort by Popularity** `DEPRECATED`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 100.0% | 1 | 1 | 0 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| FUNC-002-01 | deprecated | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-002-sort-by-popularity.feature/results-are-ordered-by-recent-loans |

### FUNC-003

**FUNC-003 · My Loans Page - Renew Loan** `IN REVIEW`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| not applicable | 0 | 0 | 0 | 0 |

No counted criteria.

### FUNC-004

**FUNC-004 · My Loans Page - Show Overdue Badge** `PLANNED`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| not applicable | 0 | 0 | 0 | 0 |

No counted criteria.

### FUNC-005

**FUNC-005 · Membership Sign-up Wizard - Validate Required Details** `ACTIVE`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 88.9% | 3 | 2 | 1 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| FUNC-005-01 | active | `COVERED` | per aspect, below |
| FUNC-005-02 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-005-validate-required-details.feature/future-date-of-birth-is-rejected |
| FUNC-005-03 | active | `PARTIALLY COVERED` 2/3 | per aspect, below |

**FUNC-005-01** `COVERED`

| Aspect | Status | Scenarios |
|---|---|---|
| name | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-005-validate-required-details.feature/empty-name-is-rejected |
| date-of-birth | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-005-validate-required-details.feature/empty-date-of-birth-is-rejected |
| address | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-005-validate-required-details.feature/empty-address-is-rejected |

**FUNC-005-03** `PARTIALLY COVERED` 2/3

| required\_detail | Status | Scenarios |
|---|---|---|
| name | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-005-validate-required-details.feature/filling-in-the-name-clears-its-error |
| date-of-birth | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-005-validate-required-details.feature/filling-in-the-date-of-birth-clears-its-error |
| address | not covered | — |

### FUNC-006

**FUNC-006 · Membership Sign-up Wizard - Submit Application** `ACTIVE`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 50.0% | 2 | 1 | 0 | 1 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| FUNC-006-01 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-006-submit-application.feature/joining-creates-a-membership |
| FUNC-006-02 | active | `NOT COVERED` | — |

### FUNC-007

**FUNC-007 · Printable Loan Slip - Print Slip** `DEPRECATED`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 100.0% | 1 | 1 | 0 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| FUNC-007-01 | deprecated | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-007-print-loan-slip.feature/member-prints-a-loan-slip |

### FUNC-008

**FUNC-008 · Catalogue Search Page - Sort Results** `ACTIVE`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 100.0% | 3 | 3 | 0 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| FUNC-008-01 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-008-sort-results.feature/results-are-ordered-by-relevance |
| FUNC-008-02 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-008-sort-results.feature/results-are-ordered-newest-first |
| FUNC-008-03 | active | `COVERED` | per aspect, below |

**FUNC-008-03** `COVERED`

| sort\_order | Status | Scenarios |
|---|---|---|
| relevance | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-008-sort-results.feature/relevance-order-continues-on-the-next-page |
| newest-first | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-008-sort-results.feature/newest-first-order-continues-on-the-next-page |

### FUNC-009

**FUNC-009 · My Loans Page - Loan List States** `ACTIVE`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 100.0% | 2 | 2 | 0 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| FUNC-009-01 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-009-loan-list-states.feature/member-with-loans-sees-their-loans |
| FUNC-009-02 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-009-loan-list-states.feature/member-without-loans-sees-the-empty-state |

### FUNC-010

**FUNC-010 · My Loans Page - Total Fines Owed** `ACTIVE`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 100.0% | 2 | 2 | 0 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| FUNC-010-01 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-010-total-fines-owed.feature/total-fines-add-up-across-loans |
| FUNC-010-02 | active | `COVERED` | per aspect, below |

**FUNC-010-02** `COVERED`

| fine\_state | Status | Scenarios |
|---|---|---|
| paid | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-010-total-fines-owed.feature/a-settled-fine-is-left-out-of-the-total |
| waived | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-010-total-fines-owed.feature/a-settled-fine-is-left-out-of-the-total |
| written-off | covered | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-010-total-fines-owed.feature/a-settled-fine-is-left-out-of-the-total |

### FUNC-011

**FUNC-011 · Membership Sign-up Wizard - Redirect Existing Members** `ACTIVE`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| 100.0% | 1 | 1 | 0 | 0 |

| Criterion | State | Status | Scenarios |
|---|---|---|---|
| FUNC-011-01 | active | `COVERED` | AbsaOSS/living-doc-testbed/projects/core/tests/e2e/features/liv\_doc\_func/func-011-redirect-existing-members.feature/signed-in-member-is-redirected-to-my-loans |

### FUNC-012

**FUNC-012 · Loan Detail Page - Show Renewal History** `PLANNED`

| Coverage | Counted | Covered | Partially covered | Not covered |
|---|---|---|---|---|
| not applicable | 0 | 0 | 0 | 0 |

No counted criteria.
