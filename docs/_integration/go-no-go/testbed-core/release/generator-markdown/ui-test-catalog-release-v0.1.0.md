# UI test catalog

- [User Stories](#user-stories)
    - [US-001](#us-001)
    - [US-002](#us-002)
    - [US-003](#us-003)
- [Functionalities](#functionalities)
    - [FUNC-001](#func-001)
    - [FUNC-002](#func-002)
    - [FUNC-005](#func-005)
    - [FUNC-006](#func-006)
    - [FUNC-007](#func-007)
    - [FUNC-008](#func-008)
    - [FUNC-009](#func-009)
    - [FUNC-010](#func-010)
    - [FUNC-011](#func-011)
- [User Story tests](#user-story-tests)
    - [us-001-borrow-a-book.feature](#us-001-borrow-a-bookfeature)
    - [us-002-join-the-library.feature](#us-002-join-the-libraryfeature)
    - [us-003-register-at-the-desk.feature](#us-003-register-at-the-deskfeature)
- [Functionality tests](#functionality-tests)
    - [func-001-filter-search-results.feature](#func-001-filter-search-resultsfeature)
    - [func-002-sort-by-popularity.feature](#func-002-sort-by-popularityfeature)
    - [func-005-validate-required-details.feature](#func-005-validate-required-detailsfeature)
    - [func-006-submit-application.feature](#func-006-submit-applicationfeature)
    - [func-007-print-loan-slip.feature](#func-007-print-loan-slipfeature)
    - [func-008-sort-results.feature](#func-008-sort-resultsfeature)
    - [func-009-loan-list-states.feature](#func-009-loan-list-statesfeature)
    - [func-010-total-fines-owed.feature](#func-010-total-fines-owedfeature)
    - [func-011-redirect-existing-members.feature](#func-011-redirect-existing-membersfeature)

---

## User Stories

3 User Stories: each tested criterion with its state and the tests that cover it.

---

### US-001

4 tests.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| US-001-01 | `ACTIVE` | [Member borrows an available book](#test-member-borrows-an-available-book) | — | — | @Regression |
| US-001-01 | `ACTIVE` | [Borrowed books are listed with their due dates (us-001-borrow-a-book)](#test-borrowed-books-are-listed-with-their-due-dates-us-001-borrow-a-book) | — | — | — |
| US-001-02 | `ACTIVE` | [Member at the loan limit is told why they cannot borrow](#test-member-at-the-loan-limit-is-told-why-they-cannot-borrow) | — | — | — |
| US-001-04 | `DEPRECATED` | [Member is offered a loan slip](#test-member-is-offered-a-loan-slip) | — | — | — |

---

### US-002

3 tests.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| US-002-01 | `ACTIVE` | [Applicant joins the library](#test-applicant-joins-the-library) | — | — | @Regression |
| US-002-02 | `ACTIVE` | [Applicant joins the library](#test-applicant-joins-the-library) | — | — | @Regression |
| US-002-03 | `ACTIVE` | [Adult applicant gets an adult card](#test-adult-applicant-gets-an-adult-card) | — | adult | — |
| US-002-03 | `ACTIVE` | [Junior applicant gets a junior card](#test-junior-applicant-gets-a-junior-card) | — | junior | — |

---

### US-003

1 test.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| US-003-01 | `DEPRECATED` | [Desk staff register a resident](#test-desk-staff-register-a-resident) | — | — | — |

[Home](#ui-test-catalog)

---

## Functionalities

9 Functionalities: each tested criterion with its state and the tests that cover it.

---

### FUNC-001

2 tests.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| FUNC-001-01 | `ACTIVE` | [Filtering by author keeps only that author's books](#test-filtering-by-author-keeps-only-that-authors-books) | — | author | — |
| FUNC-001-02 | `ACTIVE` | [Clearing the filters restores every result](#test-clearing-the-filters-restores-every-result) | — | — | — |

---

### FUNC-002

1 test.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| FUNC-002-01 | `DEPRECATED` | [Results are ordered by recent loans](#test-results-are-ordered-by-recent-loans) | — | — | — |

---

### FUNC-005

6 tests.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| FUNC-005-01 | `ACTIVE` | [Empty name is rejected](#test-empty-name-is-rejected) | — | name | — |
| FUNC-005-01 | `ACTIVE` | [Empty date of birth is rejected](#test-empty-date-of-birth-is-rejected) | — | date-of-birth | — |
| FUNC-005-01 | `ACTIVE` | [Empty address is rejected](#test-empty-address-is-rejected) | — | address | — |
| FUNC-005-02 | `ACTIVE` | [Future date of birth is rejected](#test-future-date-of-birth-is-rejected) | — | — | — |
| FUNC-005-03 | `ACTIVE` | [Filling in the name clears its error](#test-filling-in-the-name-clears-its-error) | — | name | — |
| FUNC-005-03 | `ACTIVE` | [Filling in the date of birth clears its error](#test-filling-in-the-date-of-birth-clears-its-error) | — | date-of-birth | — |

---

### FUNC-006

1 test.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| FUNC-006-01 | `ACTIVE` | [Joining creates a membership](#test-joining-creates-a-membership) | — | — | — |

---

### FUNC-007

1 test.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| FUNC-007-01 | `DEPRECATED` | [Member prints a loan slip](#test-member-prints-a-loan-slip) | — | — | — |

---

### FUNC-008

4 tests.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| FUNC-008-01 | `ACTIVE` | [Results are ordered by relevance](#test-results-are-ordered-by-relevance) | — | — | — |
| FUNC-008-02 | `ACTIVE` | [Results are ordered newest first](#test-results-are-ordered-newest-first) | — | — | — |
| FUNC-008-03 | `ACTIVE` | [Relevance order continues on the next page](#test-relevance-order-continues-on-the-next-page) | — | relevance | — |
| FUNC-008-03 | `ACTIVE` | [Newest-first order continues on the next page](#test-newest-first-order-continues-on-the-next-page) | — | newest-first | — |

---

### FUNC-009

5 tests, 1 skipped.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| FUNC-009-01 | `ACTIVE` | [Member with loans sees their loans](#test-member-with-loans-sees-their-loans) | — | — | — |
| FUNC-009-01 | `ACTIVE` | [Borrowed books are listed with their due dates (func-009-loan-list-states)](#test-borrowed-books-are-listed-with-their-due-dates-func-009-loan-list-states) | — | — | — |
| FUNC-009-02 | `ACTIVE` | [Member without loans sees the empty state](#test-member-without-loans-sees-the-empty-state) | — | — | — |
| FUNC-009-02 | `ACTIVE` | [The empty state shows its message in full](#test-the-empty-state-shows-its-message-in-full) | — | — | — |
| FUNC-009-03 | `ACTIVE` | [Member whose loans fail to load sees the error state](#test-member-whose-loans-fail-to-load-sees-the-error-state) | `SKIPPED` | — | @skip |

---

### FUNC-010

4 tests, 1 skipped.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| FUNC-010-01 | `ACTIVE` | [Total fines add up across loans](#test-total-fines-add-up-across-loans) | — | — | — |
| FUNC-010-01 | `ACTIVE` | [Small fines add up to the cent](#test-small-fines-add-up-to-the-cent) | `SKIPPED` | — | @skip |
| FUNC-010-01 | `ACTIVE` | [The total adds up for any number of loans](#test-the-total-adds-up-for-any-number-of-loans) | — | — | — |
| FUNC-010-02 | `ACTIVE` | [A settled fine is left out of the total](#test-a-settled-fine-is-left-out-of-the-total) | — | — | — |

---

### FUNC-011

1 test.

| AC | AC state | Test | Test state | Aspect | Tags |
|---|---|---|---|---|---|
| FUNC-011-01 | `ACTIVE` | [Signed-in member is redirected to My Loans](#test-signed-in-member-is-redirected-to-my-loans) | — | — | — |

[Home](#ui-test-catalog)

---

## User Story tests

3 feature files, 8 tests, each with its metadata and steps.

- [us-001-borrow-a-book.feature](#us-001-borrow-a-bookfeature)
- [us-002-join-the-library.feature](#us-002-join-the-libraryfeature)
- [us-003-register-at-the-desk.feature](#us-003-register-at-the-deskfeature)

---

### us-001-borrow-a-book.feature

- **Entity:** [US-001](#us-001)
- **Source:** [us-001-borrow-a-book.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-001-borrow-a-book.feature)

**Background**

```gherkin
Given a member in good standing is signed in
```

#### Test: Member borrows an available book

- **Covers:** [US-001-01](#us-001)
- **Tags:** @Regression
- **Source:** [us-001-borrow-a-book.feature\#L56](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-001-borrow-a-book.feature#L56)

```gherkin
Given the book "The Hobbit" is available
When the member borrows "The Hobbit" from the catalogue
Then "The Hobbit" is listed on the My Loans page
And the loan shows a due date
```

#### Test: Member is offered a loan slip

- **Covers:** [US-001-04](#us-001)
- **Source:** [us-001-borrow-a-book.feature\#L64](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-001-borrow-a-book.feature#L64)

```gherkin
Given the book "Dune" is available
When the member borrows "Dune" from the catalogue
Then a printable loan slip for "Dune" is offered
```

**Rule background:** A member borrows within the loan limit of their category

```gherkin
Given the loan limit for the member's category is 3
```

#### Test: Borrowed books are listed with their due dates (us-001-borrow-a-book)

- **Rule:** A member borrows within the loan limit of their category
- **Covers:** [US-001-01](#us-001)
- **Source:** [us-001-borrow-a-book.feature\#L76](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-001-borrow-a-book.feature#L76)

```gherkin
Given the member holds 2 loans
And the book "Emma" is available
When the member borrows "Emma" from the catalogue
Then "Emma" is listed on the My Loans page with its due date
```

#### Test: Member at the loan limit is told why they cannot borrow

- **Rule:** A member borrows within the loan limit of their category
- **Covers:** [US-001-02](#us-001)
- **Source:** [us-001-borrow-a-book.feature\#L84](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-001-borrow-a-book.feature#L84)

```gherkin
Given the member holds 3 loans
And the book "Emma" is available
When the member tries to borrow "Emma" from the catalogue
Then the loan is refused with "You have reached your loan limit of 3"
```

[Home](#ui-test-catalog)

---

### us-002-join-the-library.feature

- **Entity:** [US-002](#us-002)
- **Source:** [us-002-join-the-library.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-002-join-the-library.feature)

#### Test: Applicant joins the library

- **Covers:** [US-002-01](#us-002), [US-002-02](#us-002)
- **Outline:** 2 examples
- **Tags:** @Regression
- **Source:** [us-002-join-the-library.feature\#L38](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-002-join-the-library.feature#L38)

```gherkin
Given an applicant named "<name>" is on the sign-up wizard
When the applicant completes every step of the wizard
Then a membership number is shown on the confirmation step
And a confirmation email with that membership number is sent to "<email>"
Examples:
  | name         | email                 |
  | Ada Lovelace | ada@example.org       |
  | Alan Turing  | alan.t@example.org    |
```

#### Test: Adult applicant gets an adult card

- **Covers:** [US-002-03](#us-002) (adult)
- **Source:** [us-002-join-the-library.feature\#L51](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-002-join-the-library.feature#L51)

```gherkin
Given an applicant aged 34 is on the card type step
Then the "Adult" card type is offered
```

#### Test: Junior applicant gets a junior card

- **Covers:** [US-002-03](#us-002) (junior)
- **Source:** [us-002-join-the-library.feature\#L57](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-002-join-the-library.feature#L57)

```gherkin
Given an applicant aged 12 is on the card type step
Then the "Junior" card type is offered
```

[Home](#ui-test-catalog)

---

### us-003-register-at-the-desk.feature

- **Entity:** [US-003](#us-003)
- **Source:** [us-003-register-at-the-desk.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-003-register-at-the-desk.feature)

#### Test: Desk staff register a resident

- **Covers:** [US-003-01](#us-003)
- **Source:** [us-003-register-at-the-desk.feature\#L26](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_us/us-003-register-at-the-desk.feature#L26)

```gherkin
Given a resident hands in a completed paper form
When the desk staff register the resident
Then a membership card is printed for the resident
```

[Home](#ui-test-catalog)

---

## Functionality tests

9 feature files, 26 tests, each with its metadata and steps.

- [func-001-filter-search-results.feature](#func-001-filter-search-resultsfeature)
- [func-002-sort-by-popularity.feature](#func-002-sort-by-popularityfeature)
- [func-005-validate-required-details.feature](#func-005-validate-required-detailsfeature)
- [func-006-submit-application.feature](#func-006-submit-applicationfeature)
- [func-007-print-loan-slip.feature](#func-007-print-loan-slipfeature)
- [func-008-sort-results.feature](#func-008-sort-resultsfeature)
- [func-009-loan-list-states.feature](#func-009-loan-list-statesfeature)
- [func-010-total-fines-owed.feature](#func-010-total-fines-owedfeature)
- [func-011-redirect-existing-members.feature](#func-011-redirect-existing-membersfeature)

---

### func-001-filter-search-results.feature

- **Entity:** [FUNC-001](#func-001)
- **Source:** [func-001-filter-search-results.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-001-filter-search-results.feature)

#### Test: Filtering by author keeps only that author's books

- **Covers:** [FUNC-001-01](#func-001) (author)
- **Source:** [func-001-filter-search-results.feature\#L30](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-001-filter-search-results.feature#L30)

```gherkin
Given the search for "dragons" shows books by "J. R. R. Tolkien" and "Naomi Novik"
When the member filters by the author "Naomi Novik"
Then only books by "Naomi Novik" are listed
```

#### Test: Clearing the filters restores every result

- **Covers:** [FUNC-001-02](#func-001)
- **Source:** [func-001-filter-search-results.feature\#L37](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-001-filter-search-results.feature#L37)

```gherkin
Given the search for "dragons" is filtered by the author "Naomi Novik"
When the member clears all filters
Then every result of the search for "dragons" is listed
```

[Home](#ui-test-catalog)

---

### func-002-sort-by-popularity.feature

- **Entity:** [FUNC-002](#func-002)
- **Source:** [func-002-sort-by-popularity.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-002-sort-by-popularity.feature)

#### Test: Results are ordered by recent loans

- **Covers:** [FUNC-002-01](#func-002)
- **Source:** [func-002-sort-by-popularity.feature\#L28](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-002-sort-by-popularity.feature#L28)

```gherkin
Given the search for "dragons" shows "Temeraire" with 40 recent loans and "The Hobbit" with 12
When the member sorts by "Most popular"
Then "Temeraire" is listed before "The Hobbit"
```

[Home](#ui-test-catalog)

---

### func-005-validate-required-details.feature

- **Entity:** [FUNC-005](#func-005)
- **Source:** [func-005-validate-required-details.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-005-validate-required-details.feature)

#### Test: Empty name is rejected

- **Covers:** [FUNC-005-01](#func-005) (name)
- **Source:** [func-005-validate-required-details.feature\#L31](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-005-validate-required-details.feature#L31)

```gherkin
Given the applicant is on the details step
When the applicant continues with the name left empty
Then an inline error is shown under the name
```

#### Test: Empty date of birth is rejected

- **Covers:** [FUNC-005-01](#func-005) (date-of-birth)
- **Source:** [func-005-validate-required-details.feature\#L38](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-005-validate-required-details.feature#L38)

```gherkin
Given the applicant is on the details step
When the applicant continues with the date of birth left empty
Then an inline error is shown under the date of birth
```

#### Test: Empty address is rejected

- **Covers:** [FUNC-005-01](#func-005) (address)
- **Source:** [func-005-validate-required-details.feature\#L45](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-005-validate-required-details.feature#L45)

```gherkin
Given the applicant is on the details step
When the applicant continues with the address left empty
Then an inline error is shown under the address
```

#### Test: Future date of birth is rejected

- **Covers:** [FUNC-005-02](#func-005)
- **Source:** [func-005-validate-required-details.feature\#L52](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-005-validate-required-details.feature#L52)

```gherkin
Given the applicant is on the details step
When the applicant enters a date of birth of 2099-01-01
Then an inline error is shown under the date of birth
```

#### Test: Filling in the name clears its error

- **Covers:** [FUNC-005-03](#func-005) (name)
- **Source:** [func-005-validate-required-details.feature\#L59](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-005-validate-required-details.feature#L59)

```gherkin
Given the applicant is on the details step
And the applicant has continued with the name left empty
When the applicant enters the name "Ada Lovelace"
Then no error is shown under the name
```

#### Test: Filling in the date of birth clears its error

- **Covers:** [FUNC-005-03](#func-005) (date-of-birth)
- **Source:** [func-005-validate-required-details.feature\#L67](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-005-validate-required-details.feature#L67)

```gherkin
Given the applicant is on the details step
And the applicant has continued with the date of birth left empty
When the applicant enters a date of birth of 1990-05-14
Then no error is shown under the date of birth
```

[Home](#ui-test-catalog)

---

### func-006-submit-application.feature

- **Entity:** [FUNC-006](#func-006)
- **Source:** [func-006-submit-application.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-006-submit-application.feature)

#### Test: Joining creates a membership

- **Covers:** [FUNC-006-01](#func-006)
- **Source:** [func-006-submit-application.feature\#L27](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-006-submit-application.feature#L27)

```gherkin
Given the applicant is on the confirm step
When the applicant presses "Join"
Then a membership number is shown
```

[Home](#ui-test-catalog)

---

### func-007-print-loan-slip.feature

- **Entity:** [FUNC-007](#func-007)
- **Source:** [func-007-print-loan-slip.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-007-print-loan-slip.feature)

#### Test: Member prints a loan slip

- **Covers:** [FUNC-007-01](#func-007)
- **Source:** [func-007-print-loan-slip.feature\#L25](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-007-print-loan-slip.feature#L25)

```gherkin
Given the member is on the loan slip of "Dune"
When the member presses "Print"
Then the print dialog shows "Dune" with the member number and the due date
```

[Home](#ui-test-catalog)

---

### func-008-sort-results.feature

- **Entity:** [FUNC-008](#func-008)
- **Source:** [func-008-sort-results.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature)

#### Test: Results are ordered by relevance

- **Covers:** [FUNC-008-01](#func-008)
- **Source:** [func-008-sort-results.feature\#L32](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature#L32)

```gherkin
When the member searches for "dragons"
Then the results are ordered by relevance
```

#### Test: Results are ordered newest first

- **Covers:** [FUNC-008-02](#func-008)
- **Source:** [func-008-sort-results.feature\#L38](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature#L38)

```gherkin
Given the search for "dragons" shows "The Hobbit" from 1937 and "Temeraire" from 2006
When the member sorts by "Newest first"
Then "Temeraire" is listed before "The Hobbit"
```

#### Test: Relevance order continues on the next page

- **Covers:** [FUNC-008-03](#func-008) (relevance)
- **Source:** [func-008-sort-results.feature\#L45](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature#L45)

```gherkin
Given the search for "dragons" returns more than 20 results
When the member opens the second page of results
Then the second page continues the relevance order of the first
```

#### Test: Newest-first order continues on the next page

- **Covers:** [FUNC-008-03](#func-008) (newest-first)
- **Source:** [func-008-sort-results.feature\#L52](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature#L52)

```gherkin
Given the search for "dragons" returns more than 20 results
And the member sorts by "Newest first"
When the member opens the second page of results
Then the second page continues the newest-first order of the first
```

[Home](#ui-test-catalog)

---

### func-009-loan-list-states.feature

- **Entity:** [FUNC-009](#func-009)
- **Source:** [func-009-loan-list-states.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-009-loan-list-states.feature)

#### Test: Member with loans sees their loans

- **Covers:** [FUNC-009-01](#func-009)
- **Source:** [func-009-loan-list-states.feature\#L28](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-009-loan-list-states.feature#L28)

```gherkin
Given the member has borrowed "The Hobbit" and "Dune"
When the member opens the My Loans page
Then two loans are listed, each with its title and due date
```

#### Test: Member without loans sees the empty state

- **Covers:** [FUNC-009-02](#func-009)
- **Source:** [func-009-loan-list-states.feature\#L35](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-009-loan-list-states.feature#L35)

```gherkin
Given the member has no loans
When the member opens the My Loans page
Then "You have no books on loan" is shown with a link to the catalogue
```

#### Test: Member whose loans fail to load sees the error state

- **Status:** `SKIPPED`
- **Skipped, not counted:** [FUNC-009-03](#func-009)
- **Tags:** @skip
- **Source:** [func-009-loan-list-states.feature\#L43](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-009-loan-list-states.feature#L43)

```gherkin
Given the loans service is unavailable
When the member opens the My Loans page
Then "Loans could not be loaded" is shown with a "Try again" button
```

#### Test: Borrowed books are listed with their due dates (func-009-loan-list-states)

- **Covers:** [FUNC-009-01](#func-009)
- **Source:** [func-009-loan-list-states.feature\#L50](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-009-loan-list-states.feature#L50)

```gherkin
Given the member has borrowed these books:
  | title      | due date   |
  | The Hobbit | 2026-12-01 |
  | Dune       | 2026-12-08 |
When the member opens the My Loans page
Then each book is listed in its own row with its due date
```

#### Test: The empty state shows its message in full

- **Covers:** [FUNC-009-02](#func-009)
- **Source:** [func-009-loan-list-states.feature\#L60](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-009-loan-list-states.feature#L60)

```gherkin
Given the member has no loans
When the member opens the My Loans page
Then the empty state reads:
  """
  You have no books on loan.
  Browse the catalogue to borrow one.
  """
```

#### Test: The My Loans page opens from the menu

- **Source:** [func-009-loan-list-states.feature\#L69](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-009-loan-list-states.feature#L69)

```gherkin
Given the member is on the home page
When the member chooses "My Loans" in the menu
Then the My Loans page is shown
```

[Home](#ui-test-catalog)

---

### func-010-total-fines-owed.feature

- **Entity:** [FUNC-010](#func-010)
- **Source:** [func-010-total-fines-owed.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-010-total-fines-owed.feature)

#### Test: Total fines add up across loans

- **Covers:** [FUNC-010-01](#func-010)
- **Source:** [func-010-total-fines-owed.feature\#L28](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-010-total-fines-owed.feature#L28)

```gherkin
Given the member owes 0.40 on "The Hobbit" and 1.20 on "Dune"
When the member opens the My Loans page
Then the total fines owed is 1.60
```

#### Test: Small fines add up to the cent

- **Status:** `SKIPPED`
- **Skipped, not counted:** [FUNC-010-01](#func-010)
- **Tags:** @skip
- **Source:** [func-010-total-fines-owed.feature\#L36](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-010-total-fines-owed.feature#L36)

```gherkin
Given the member owes 0.10 on "The Hobbit", 0.10 on "Dune" and 0.10 on "Emma"
When the member opens the My Loans page
Then the total fines owed is 0.30
```

#### Test: A settled fine is left out of the total

- **Covers:** [FUNC-010-02](#func-010)
- **Outline:** 3 examples
- **Source:** [func-010-total-fines-owed.feature\#L43](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-010-total-fines-owed.feature#L43)

```gherkin
Given the member has a fine of 0.40 on "The Hobbit" and 1.20 on "Dune"
And the fine on "Dune" is <fine-state>
When the member opens the My Loans page
Then the total fines owed is 0.40
Examples:
  | fine-state  |
  | paid        |
  | waived      |
  | written-off |
```

#### Test: The total adds up for any number of loans

- **Covers:** [FUNC-010-01](#func-010)
- **Outline:** 3 examples
- **Source:** [func-010-total-fines-owed.feature\#L57](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-010-total-fines-owed.feature#L57)

```gherkin
Given the member owes <fine> on each of <loans> loans
When the member opens the My Loans page
Then the total fines owed is <total>
Examples: A few loans
  | loans | fine | total |
  | 1     | 0.40 | 0.40  |
  | 3     | 0.40 | 1.20  |
Examples: Many loans
  | loans | fine | total |
  | 50    | 0.10 | 5.00  |
```

[Home](#ui-test-catalog)

---

### func-011-redirect-existing-members.feature

- **Entity:** [FUNC-011](#func-011)
- **Source:** [func-011-redirect-existing-members.feature](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-011-redirect-existing-members.feature)

#### Test: Signed-in member is redirected to My Loans

- **Covers:** [FUNC-011-01](#func-011)
- **Source:** [func-011-redirect-existing-members.feature\#L22](https://github.com/AbsaOSS/living-doc-testbed/blob/6b9b3ec9262032518023a3cd6e9f86acf97d1f89/projects/core/tests/e2e/features/liv_doc_func/func-011-redirect-existing-members.feature#L22)

```gherkin
Given a member is signed in
When the member opens "/join"
Then the My Loans page is displayed
```

[Home](#ui-test-catalog)
