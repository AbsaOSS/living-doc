# tests/examples

Parent: [../CONTEXT.md](../CONTEXT.md)

## Purpose

The corpus checker `examples_check.py` (its rules: the module docstring), the snapshot pipeline over `docs/examples/`, and their pytest suites.

## Test conventions

- Suites: `test_examples_check.py`, `test_check_utilities_pins.py`, `test_normalize_snapshot.py`. Run: `python -m pytest tests/examples -q`.
- The mock surface is the real corpus, not a fake: the `corpus_dir` fixture copies `docs/examples/` into `tmp_path`; a test mutates exactly one thing and asserts that `check_corpus()` returns the `Finding` naming the file and rule. Never hand-write a synthetic mini-corpus; it drifts from the real one.
- Never write to the real `docs/examples/`.
- Reuse `corpus_dir`; don't add a second corpus fixture.
- Assert on returned `Finding` objects, never on output text.
- `test_pristine_corpus_passes` asserts `check_corpus(REAL_EXAMPLES) == []` on the unmodified corpus. Every mutation test depends on it; keep it first.
- A new rule in `examples_check.py` gets a mutation test that breaks exactly that rule, plus a passing case when the rule has an allowed variant.

## Mutation patterns

| Need | Pattern | Example |
|---|---|---|
| a rule must fire | strip, replace or insert one line, assert the finding names the file and the offending field, tag or id | `test_missing_required_header_field_fails`, `test_undeclared_ac_tag_fails`, `test_pageobject_status_field_fails` |
| an allowed variant must pass | apply the variant, assert no finding names the file | `test_pageobject_stub_reason_is_optional`, `test_backlog_ac_without_version_is_accepted` |
| a required file | delete it, assert the finding names its path | `test_missing_project_profile_fails` |
| a cross-file rule | change one or more files so they disagree, assert the rule's finding | `test_coverage_pair_broken_when_every_ac_covered`, `test_pair_with_different_ac_sets_fails` |

## Gotchas

- Nothing here invokes the real collector or toolkit. Mining over `docs/examples/` belongs in `regen-collector-snapshots.sh`, over the testbed in `tests/testbed/`.
