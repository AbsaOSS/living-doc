## Overview

`tools/examples_check.py::SURFACE_TYPES` listed six surface types (`UI`, `API`, `Service`, `Worker`,
`Module`, `Library`), but the canon only defines two: the glossary ("Feature") and the header-types
guide (§2 "Required fields") say a Feature's surface is either `UI` or `API`, and a PageObject header
— the test abstraction for a UI surface — is `UI` only. The checker's own rules accepted the extra
four values, so a PageObject with `surface_type: Service` or `API`, or a Feature issue body with
`## Surface Type` `Worker`, passed CI and taught collectors and `agentic-toolkit` a vocabulary the
canon rejects.

This change narrows `SURFACE_TYPES` to `["UI", "API"]`, makes the PageObject header check reject
anything other than the literal `UI` (an `API` surface has no PageObject header at all, so it isn't
just "not in the list" — it's a different rule), and adds the previously-missing validation of a
Feature issue body's `## Surface Type` value against `SURFACE_TYPES`.

## Release Notes

- `examples_check` now rejects a PageObject `surface_type` other than `UI` and a Feature issue-body
  `## Surface Type` outside `UI` / `API`, matching the glossary and header-types canon.

## Acceptance criteria

- [x] `SURFACE_TYPES` equals the glossary's list, `["UI", "API"]` — [tools/examples_check.py:71](tools/examples_check.py#L71)
- [x] A PageObject header with any `surface_type` other than `UI` fails, and the hint names the rule — [tools/examples_check.py:502-507](tools/examples_check.py#L502-L507), verified by `test_pageobject_surface_type_service_fails` / `test_pageobject_surface_type_api_fails` ([tools/test_examples_check.py:173,185](tools/test_examples_check.py#L173))
- [x] A Feature issue body with a `## Surface Type` outside `SURFACE_TYPES` fails — [tools/examples_check.py:586-589](tools/examples_check.py#L586-L589), verified by `test_feat_surface_type_worker_fails` ([tools/test_examples_check.py:234](tools/test_examples_check.py#L234))
- [x] The three new negative cases exist in `tools/test_examples_check.py`; `examples_check` over `docs/examples/` stays green — `python -m pytest tools/test_examples_check.py -q` → 29 passed; `python tools/examples_check.py` → OK

## Related

Closes #31
