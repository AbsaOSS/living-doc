# testbed-core

*View: release · version 1.0.0 · 16 of 20 entities and 24 of 27 acceptance criteria selected*

## Contents

- User Stories
    - [US-001](#us-001) US-001 · Borrow a Book
    - [US-002](#us-002) US-002 · Join the Library
    - [US-003](#us-003) US-003 · Register at the Desk
- Features
    - [FEAT-001](#feat-001) FEAT-001 · Catalogue Search Page
    - [FEAT-005](#feat-005) FEAT-005 · Printable Loan Slip
    - [FEAT-003](#feat-003) FEAT-003 · Membership Sign-up Wizard
    - [FEAT-002](#feat-002) FEAT-002 · My Loans Page
- Functionalities
    - [FUNC-001](#func-001) FUNC-001 · Catalogue Search Page - Filter Search Results
    - [FUNC-002](#func-002) FUNC-002 · Catalogue Search Page - Sort by Popularity
    - [FUNC-005](#func-005) FUNC-005 · Membership Sign-up Wizard - Validate Required Details
    - [FUNC-006](#func-006) FUNC-006 · Membership Sign-up Wizard - Submit Application
    - [FUNC-007](#func-007) FUNC-007 · Printable Loan Slip - Print Slip
    - [FUNC-008](#func-008) FUNC-008 · Catalogue Search Page - Sort Results
    - [FUNC-009](#func-009) FUNC-009 · My Loans Page - Loan List States
    - [FUNC-010](#func-010) FUNC-010 · My Loans Page - Total Fines Owed
    - [FUNC-011](#func-011) FUNC-011 · Membership Sign-up Wizard - Redirect Existing Members

## User Stories

### US-001

**US-001 · Borrow a Book** `ACTIVE`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_us/us-001-borrow-a-book.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_us/us-001-borrow-a-book.feature)

**Business value**

- Members can take a book home without queuing at the desk, so the desk staff spend their time on enquiries instead of checkouts.

**Preconditions**

- The member is signed in with an account in good standing.

**Not in scope**

- Borrowing from a partner library through inter-library loan.

**Acceptance criteria**

#### AC:US-001-01 (v1.0.0 - active)

A member who borrows an available book from the catalogue sees the loan on the My Loans page with its due date.

#### AC:US-001-02 (v1.0.0 - active)

A member who already holds the maximum number of loans cannot borrow another book and is told why.

- **Also requires:**
    - The loan limit for the member's category is set.

#### AC:US-001-04 (v1.0.0 - deprecated - removal planned v2.0.0)

A printable loan slip is offered after a book is borrowed.

- removal planned v2.0.0
- **Rationale:** The due date is now shown on My Loans and sent by email, so the slip is no longer needed.

### US-002

**US-002 · Join the Library** `ACTIVE`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_us/us-002-join-the-library.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_us/us-002-join-the-library.feature)
- **Linked issue:** [https&#58;//github.com/AbsaOSS/living-doc-testbed/blob/master/projects/core/README.md](https://github.com/AbsaOSS/living-doc-testbed/blob/master/projects/core/README.md)

**Business value**

- New members can join online at any hour, so sign-ups no longer depend on desk opening times.
    - Most sign-up requests used to arrive by email outside opening hours.
- Desk staff stop re-typing paper forms.

**Notes**

- The sign-up wizard is also used by desk staff on the desk terminal.

**Acceptance criteria**

#### AC:US-002-01 (v1.0.0 - active)

An applicant who completes the sign-up wizard sees a membership number on the confirmation step.

#### AC:US-002-02 (v1.0.0 - active)

The applicant receives a confirmation email with the membership number.

#### AC:US-002-03 (v1.0.0 - active)

The applicant can choose the card type that matches their age.

- **Aspect:** adult, junior

### US-003

**US-003 · Register at the Desk** `DEPRECATED`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_us/us-003-register-at-the-desk.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_us/us-003-register-at-the-desk.feature)
- **Superseded by:** [US-002](#us-002)

**Business value**

- Residents without internet access can still become members.

**Acceptance criteria**

#### AC:US-003-01 (v1.0.0 - deprecated - removal planned v2.0.0)

Desk staff can register a resident from a paper form and hand over a printed membership card.

- removal planned v2.0.0

## Features

### FEAT-001

**FEAT-001 · Catalogue Search Page**

The screen where a member searches the library catalogue, narrows the results and borrows an available book.

- **Source:** [GitHub projects/core/tests/e2e/pages/CatalogueSearchPage.ts](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/pages/CatalogueSearchPage.ts)
- **Surface:** UI
- **Owners:** Discovery Team
- **User stories:** [US-001](#us-001)
- **Functionalities:** [FUNC-001](#func-001), [FUNC-002](#func-002), [FUNC-008](#func-008)
- **External dependencies:** catalogue-search-index

**Notes**

- Results are paged 20 at a time; filters and sorting apply to every page.

**Pages**

- /catalogue: CatalogueSearchPage.ts (primary). The screen where a member searches the library catalogue, narrows the results and borrows an available book.
    - **Owners:** Discovery Team

### FEAT-005

**FEAT-005 · Printable Loan Slip** `DEPRECATED`

A printable page with the title, member number and due date of a new loan.

- **Source:** [GitHub projects/core/tests/e2e/pages/LoanSlipPage.ts](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/pages/LoanSlipPage.ts)
- **Surface:** UI
- **Owners:** Lending Team
- **User stories:** [US-001](#us-001)
- **Functionalities:** [FUNC-007](#func-007)
- **Superseded by:** [FEAT-002](#feat-002)

**Pages**

- /account/loans/\{loanId\}/slip: LoanSlipPage.ts (primary). A printable page with the title, member number and due date of a new loan.
    - **Owners:** Lending Team

### FEAT-003

**FEAT-003 · Membership Sign-up Wizard**

Multi-step wizard where a resident joins the library and receives a membership number.

- **Source:** [GitHub projects/core/tests/e2e/pages/MembershipWizardPage.ts](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/pages/MembershipWizardPage.ts)
- **Surface:** UI
- **Owners:** Membership Team
- **User stories:** [US-002](#us-002), [US-003](#us-003)
- **Functionalities:** [FUNC-005](#func-005), [FUNC-006](#func-006), [FUNC-011](#func-011)
- **External dependencies:** address-lookup-service, email-gateway
- **Wizard steps:** Details, Card Type, Confirm

**Pages**

- /join: MembershipWizardPage.ts (primary). Multi-step wizard where a resident joins the library and receives a membership number.
    - **Owners:** Membership Team
- /join (wizard stays on this URL): MembershipWizardConfirmStep.ts. Step 3 (Confirm) — the applicant reviews the details and joins.
    - **Owners:** Membership Team
- /join (wizard stays on this URL): MembershipWizardDetailsStep.ts. Step 1 (Details) — the applicant's name, date of birth and home address.
    - **Owners:** Membership Team
    - **Functionalities:** [FUNC-005](#func-005)
    - **Notes:**
        - The address field suggests matches as the applicant types.

### FEAT-002

**FEAT-002 · My Loans Page**

The screen where a member sees the books they have on loan, with due dates, and renews a loan.

- **Source:** [GitHub projects/core/tests/e2e/pages/MyLoansPage.ts](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/pages/MyLoansPage.ts)
- **Surface:** UI
- **Owners:** Lending Team, Finance Team
- **User stories:** [US-001](#us-001)
- **Functionalities:** FUNC-003, FUNC-004, [FUNC-009](#func-009), [FUNC-010](#func-010)

**Pages**

- /account/loans: MyLoansPage.ts (primary). The screen where a member sees the books they have on loan, with due dates, and renews a loan.
    - **Owners:** Lending Team, Finance Team

## Functionalities

### FUNC-001

**FUNC-001 · Catalogue Search Page - Filter Search Results** `ACTIVE`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_func/func-001-filter-search-results.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_func/func-001-filter-search-results.feature)
- **Type:** component\_action
- **Parent:** [FEAT-001](#feat-001)
- **Rationale:** Filtering narrows the results already shown; it never runs a new search, so it stays a separate behaviour from the search box.

**Preconditions**

- A search has returned results from more than one author and subject.

**Acceptance criteria**

#### AC:FUNC-001-01 (v1.0.0 - active)

Selecting a filter value keeps only the results that match it.

- **Aspect:** author, subject

#### AC:FUNC-001-02 (v1.0.0 - active)

Clearing all filters restores the full result list.

### FUNC-002

**FUNC-002 · Catalogue Search Page - Sort by Popularity** `DEPRECATED`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_func/func-002-sort-by-popularity.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_func/func-002-sort-by-popularity.feature)
- **Type:** component\_action
- **Parent:** [FEAT-001](#feat-001)
- **Superseded by:** [FUNC-008](#func-008)

**Notes**

- The popularity score is refreshed overnight from the previous day's loans.

**Acceptance criteria**

#### AC:FUNC-002-01 (v1.0.0 - deprecated - removal planned v2.0.0)

Choosing "Most popular" orders the results by the number of loans in the last 90 days, highest first.

- removal planned v2.0.0

### FUNC-005

**FUNC-005 · Membership Sign-up Wizard - Validate Required Details** `ACTIVE`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_func/func-005-validate-required-details.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_func/func-005-validate-required-details.feature)
- **Linked issue:** [https&#58;//github.com/AbsaOSS/living-doc-testbed/blob/master/projects/core/README.md](https://github.com/AbsaOSS/living-doc-testbed/blob/master/projects/core/README.md)
- **Type:** field\_validation
- **Parent:** [FEAT-003](#feat-003)

**Acceptance criteria**

#### AC:FUNC-005-01 (v1.0.0 - active)

Leaving a required detail empty shows an inline error under it and keeps the applicant on the details step.

- **Aspect:** name, date-of-birth, address

#### AC:FUNC-005-02 (v1.0.0 - active)

A date of birth in the future is rejected with an inline error.

#### AC:FUNC-005-03 (v1.0.0 - active)

Filling in the \{required-detail\} clears the inline error under it.

- **required\_detail:** name, date-of-birth, address

### FUNC-006

**FUNC-006 · Membership Sign-up Wizard - Submit Application** `ACTIVE`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_func/func-006-submit-application.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_func/func-006-submit-application.feature)
- **Type:** button\_action
- **Parent:** [FEAT-003](#feat-003)

**Preconditions**

- The applicant has completed the details and card type steps.

**Acceptance criteria**

#### AC:FUNC-006-01 (v1.0.0 - active)

Pressing "Join" creates the membership and shows its number on the confirmation step.

#### AC:FUNC-006-02 (v1.0.0 - active)

Pressing "Join" a second time does not create a second membership.

### FUNC-007

**FUNC-007 · Printable Loan Slip - Print Slip** `DEPRECATED`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_func/func-007-print-loan-slip.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_func/func-007-print-loan-slip.feature)
- **Type:** button\_action
- **Parent:** [FEAT-005](#feat-005)

**Acceptance criteria**

#### AC:FUNC-007-01 (v1.0.0 - deprecated - removal planned v2.0.0)

Pressing "Print" opens the browser print dialog with the slip's title, member number and due date.

- removal planned v2.0.0

### FUNC-008

**FUNC-008 · Catalogue Search Page - Sort Results** `ACTIVE`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_func/func-008-sort-results.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature)
- **Type:** component\_action
- **Parent:** [FEAT-001](#feat-001)

**Not in scope**

- Sorting by popularity, which was retired.
- Saving a sort order between visits.

**Acceptance criteria**

#### AC:FUNC-008-01 (v1.0.0 - active)

Results are ordered by relevance by default.

#### AC:FUNC-008-02 (v1.0.0 - active)

Choosing "Newest first" orders the results by publication date, newest first.

#### AC:FUNC-008-03 (v1.0.0 - active)

The \{sort-order\} applies to every page of results, not only the first.

- **sort\_order:** relevance, newest-first

### FUNC-009

**FUNC-009 · My Loans Page - Loan List States** `ACTIVE`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_func/func-009-loan-list-states.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_func/func-009-loan-list-states.feature)
- **Type:** component\_state
- **Parent:** [FEAT-002](#feat-002)

**Acceptance criteria**

#### AC:FUNC-009-01 (v1.0.0 - active)

A member with loans sees one row per loan with its title and due date.

#### AC:FUNC-009-02 (v1.0.0 - active)

A member with no loans sees "You have no books on loan" and a link to the catalogue.

### FUNC-010

**FUNC-010 · My Loans Page - Total Fines Owed** `ACTIVE`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_func/func-010-total-fines-owed.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_func/func-010-total-fines-owed.feature)
- **Type:** calculation
- **Parent:** [FEAT-002](#feat-002)
- **Rationale:** The total is shown on its own, not on payment, so members see what they owe before they come to the desk.

**Acceptance criteria**

#### AC:FUNC-010-01 (v1.0.0 - active)

The total shown is the sum of the fines on every loan, to the cent.

#### AC:FUNC-010-02 (v1.0.0 - active)

A fine that is \{fine-state\} is left out of the total.

- **fine\_state:** paid, waived, written-off

### FUNC-011

**FUNC-011 · Membership Sign-up Wizard - Redirect Existing Members** `ACTIVE`

- **Source:** [GitHub projects/core/tests/e2e/features/liv\_doc\_func/func-011-redirect-existing-members.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/36a0ee65ad11df7588cd74a505ea1ace1ef7abc9/projects/core/tests/e2e/features/liv_doc_func/func-011-redirect-existing-members.feature)
- **Type:** navigation\_rule
- **Parent:** [FEAT-003](#feat-003)

**Acceptance criteria**

#### AC:FUNC-011-01 (v1.0.0 - active)

A signed-in member who opens the sign-up wizard is taken to the My Loans page instead.
