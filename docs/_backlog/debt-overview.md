# Debt overview

## Purpose

This page is a fast way to find the open technical debt and epics of the ecosystem's seven repositories by the strings
a search would use: a path, a symbol, a code. A row only points to its issue, which holds every fact.

## Contents

- [Rules](#rules)
- [Topics](#topics)
- [Wakes on](#wakes-on)
- [Open debt](#open-debt)

## Rules

- One row per open issue labelled tech debt or epic, a sub-issue included, in the seven repositories:
  `living-doc`, `living-doc-utilities`, `living-doc-collector-gh`, `living-doc-collector-ad`, `living-doc-toolkit`,
  `living-doc-generator-markdown` and `living-doc-generator-pdf`.
- The labels are `type:tech-debt` and `type:epic` in `living-doc` and `living-doc-generator-markdown`, and
  `tech debt` and `epic` in the other five.
- A row has four cells: the issue link `<repository>#<n>`, its topics, its anchors and its wake tag, `—` for an epic.
- A row has nothing else: no title, description, priority, status, estimate or date.
- Anchors are strings exactly as they appear in code or pages: file paths, `module.py::symbol`, CLI options, action
  inputs, error codes, workflow files.
- Topics and wake tags come from the two lists below; a new one joins its list in the same PR.
- A row is added once its issue is created, and removed once the issue is closed, implemented or dropped.
- Rows are sorted by repository, then by issue number.
- `tests/docs/debt_overview_check.py` compares this page with the open issues, on a PR that changes it, by hand and
  weekly; a weekly run that finds drift opens one Documentation Task issue, or comments on the open one.

## Topics

- `contract`: the six contracts, their models and their rules.
- `parser`: the authoring parsers and normalisation.
- `rendering`: what a generator renders, and how.
- `diagnostics`: warning and error codes and their messages.
- `action`: a composite action's `action.yml` and its venv step.
- `ci`: workflows, `Makefile` targets and repository settings.
- `docs`: pages and the canon.
- `testing`: tests, fixtures and integration runs.
- `dependencies`: package dependencies and install extras.
- `agentic`: the skills, the agent and their scripts in `agentic/`.
- `eval`: the agentic layer's evals.
- `security`: sanitising, the URL policy and security scans.
- `performance`: time and memory at real volume.
- `release`: versions and releases.
- `epic`: planned work across repositories.
- `pdf`: PDF output, `living-doc-generator-pdf`.
- `ado`: Azure DevOps as a documentation source, `living-doc-collector-ad`.
- `gh-issues`: GitHub Issues as a documentation source.
- `tutorial-capture`: tutorials captured from `@tutorial` scenarios.
- `api-endpoint`: API Features documented from an endpoint header.
- `input-checks`: authored input checked before merge and while typing.
- `agentic-scripts`: the agentic layer's repeatable steps as scripts.

## Wakes on

- `when:next-pr`: ready; the next PR that touches its anchors fixes it.
- `when:release`: at the next ecosystem release.
- `when:v1`: when the ecosystem moves to `1.0.0`.
- `when:pilot`: when a pilot deployment in a target project needs it.
- `when:reported`: when someone reports the problem it describes.
- `when:owner-decision`: when the owner decides between its options.
- `when:new-repo`: when a new `living-doc-*` repository is planned.
- `when:security-review`: at the security review.
- `when:allow-partial`: at the first run with `allow-partial`.
- `when:windows-runner`: when an action runs on a Windows runner.
- `when:container-job`: when an action runs in a `container:` job.
- `when:contract-minor`: with the next contract change, a `living-doc-utilities` minor.
- `when:utilities-release`: with the next `living-doc-utilities` release.
- `when:canon-change`: with the next change to the canon in `docs/reference/`.
- `when:eval-run`: at the next eval run of the agentic layer.
- `when:issues-source`: when GitHub Issues as a documentation source is built.
- `when:input-checks`: when the authored-input checks are built.

## Open debt

| Issue | Topics | Anchors | Wakes on |
|---|---|---|---|
| [living-doc#110](https://github.com/AbsaOSS/living-doc/issues/110) | `epic` `api-endpoint` | `feature_dependencies` `UNRESOLVED_RELATION` `PageRef` `surface_type` `doc-source` | — |
| [living-doc#111](https://github.com/AbsaOSS/living-doc/issues/111) | `epic` `input-checks` | `living-doc-check` `normalize()` `REQUIRED_FEATURE_KEYS` `MALFORMED_AC` `MISSING_ENTITY_ID` `tests/examples/examples_check.py` | — |
| [living-doc#112](https://github.com/AbsaOSS/living-doc/issues/112) | `epic` `agentic-scripts` | `compute_gaps.py` `trace_impact.py` `summarize_snapshot.py` `find_unused_steps.py` `step_matcher.py` `living-doc-shared/lib/` | — |
| [living-doc#113](https://github.com/AbsaOSS/living-doc/issues/113) | `epic` `ado` | `living-doc-collector-ad` `work_items/` `html_to_markdown` `extraction_mode` `doc-entities` `tools/make_ado_fixtures.py` | — |
| [living-doc#114](https://github.com/AbsaOSS/living-doc/issues/114) | `epic` `gh-issues` | `doc_issues/` `doc-issues` `authoring.issue_body` `github-token` `github/rate_limiter.py` `docs/examples/gh-issues/` | — |
| [living-doc#115](https://github.com/AbsaOSS/living-doc/issues/115) | `epic` `pdf` | `living-doc-generator-pdf` `generator/schemas/` `Draft7Validator` `generator_markdown/presentation.py` `docs/tutorials/gh-source-to-pdf.md` | — |
| [living-doc#116](https://github.com/AbsaOSS/living-doc/issues/116) | `epic` `tutorial-capture` | `@tutorial` `tutorials/` `tutorial_<group>/` `_is_under_tutorial_dir` | — |
| [living-doc#117](https://github.com/AbsaOSS/living-doc/issues/117) | `agentic` `gh-issues` | `validate_entity.py` `catalog.json` `## Parent Feature` `feature_dependencies` | `when:issues-source` |
| [living-doc#118](https://github.com/AbsaOSS/living-doc/issues/118) | `agentic` `input-checks` | `migrate_pageobject_headers.py` `header_bounds()` `FEAT-UNKNOWN` `stub-reason:` | `when:input-checks` |
| [living-doc#119](https://github.com/AbsaOSS/living-doc/issues/119) | `agentic` | `bdd-maintain/SKILL.md` `find_unused_steps.py` `test_skill_doc_consistency.py` | `when:next-pr` |
| [living-doc#120](https://github.com/AbsaOSS/living-doc/issues/120) | `agentic` `eval` `testing` | `gen_runner_prompts.py` `compare_baseline.py` `fix_benchmark.py` `eval-protocol.md` | `when:eval-run` |
| [living-doc#121](https://github.com/AbsaOSS/living-doc/issues/121) | `agentic` `eval` | `gherkin-living-doc-sync/SKILL.md` `living-doc-pageobject-scan/SKILL.md` `living-doc-update/SKILL.md` `living-doc-create-feature/SKILL.md` | `when:eval-run` |
| [living-doc#122](https://github.com/AbsaOSS/living-doc/issues/122) | `agentic` `eval` | `living-doc-impact-analysis/SKILL.md` `living-doc-scenario-creator/SKILL.md` `living-doc-create-feature/SKILL.md` `surface_type` `coverage_report.py` | `when:next-pr` |
| [living-doc#123](https://github.com/AbsaOSS/living-doc/issues/123) | `agentic` | `compute_gaps.py` `PYTHONHASHSEED` `UNDOCUMENTED_FUNCTIONALITY` `UNTESTED_AC` `catalog-snapshot.json` | `when:next-pr` |
| [living-doc#124](https://github.com/AbsaOSS/living-doc/issues/124) | `agentic` `parser` | `living-doc-bdd-schemas.md` `notes:` `normalize()` | `when:next-pr` |
| [living-doc#125](https://github.com/AbsaOSS/living-doc/issues/125) | `agentic` `eval` | `gherkin-living-doc-sync/SKILL.md` `living-doc-update/SKILL.md` `@AC:STANDALONE` `evals.json` | `when:eval-run` |
| [living-doc#126](https://github.com/AbsaOSS/living-doc/issues/126) | `agentic` | `validate_artifacts.py` `suggested_test_id` `next_id.py` `living-doc-bdd-copilot.agent.md` `test_skill_doc_commands.py` `scan_ac_links.py` | `when:next-pr` |
| [living-doc#127](https://github.com/AbsaOSS/living-doc/issues/127) | `agentic` `eval` | `description:` `skill-testing.md` `--num-workers` | `when:owner-decision` |
| [living-doc#128](https://github.com/AbsaOSS/living-doc/issues/128) | `agentic` `eval` | `living-doc-create-functionality/SKILL.md` `living-doc-create-user-story/SKILL.md` `Aspect:` `FEATURE_WITHOUT_USER_STORY` `ORPHAN_FEATURE` | `when:canon-change` |
| [living-doc#129](https://github.com/AbsaOSS/living-doc/issues/129) | `docs` `agentic` | `docs/reference/glossary.md` `superseded_by` `sync-canon-copies.sh` `test_entity_ids_never_change` | `when:canon-change` |
| [living-doc#130](https://github.com/AbsaOSS/living-doc/issues/130) | `ci` | `.github/workflows/link-check.yml` `workflow_dispatch` `docs_changed` | `when:next-pr` |
| [living-doc#131](https://github.com/AbsaOSS/living-doc/issues/131) | `performance` | `docs/_integration/` `local-integration.sh` | `when:pilot` |
| [living-doc#132](https://github.com/AbsaOSS/living-doc/issues/132) | `release` `testing` | `docs/_integration/README.md` `report.md` | `when:release` |
| [living-doc#133](https://github.com/AbsaOSS/living-doc/issues/133) | `ci` | `.github/workflows/tutorial-by-tag.yml` | `when:next-pr` |
| [living-doc#134](https://github.com/AbsaOSS/living-doc/issues/134) | `security` `ci` | `aquasec-night-scan.yml` `AQUA_GROUP_ID` `AQUA_REPOSITORY_ID` `url_policy` | `when:security-review` |
| [living-doc#135](https://github.com/AbsaOSS/living-doc/issues/135) | `ci` | `check-pr-requirements.yml` `test.yml` `dependabot.yml` `Makefile` | `when:new-repo` |
| [living-doc#136](https://github.com/AbsaOSS/living-doc/issues/136) | `release` | `docs/CONTEXT.md` `collector-pins.env` `-v1.0.0` | `when:release` |
| [living-doc-collector-gh#162](https://github.com/AbsaOSS/living-doc-collector-gh/issues/162) | `gh-issues` | `SUPPORTED_ISSUE_LABELS` `doc_issues/collector.py` `DocumentedUserStory` | `when:issues-source` |
| [living-doc-collector-gh#163](https://github.com/AbsaOSS/living-doc-collector-gh/issues/163) | `ci` `action` | `.github/workflows/link-check.yml` `github.action_path` `GITHUB_ACTION_PATH` `check-pr-requirements` `CONTRIBUTING.md` | `when:next-pr` |
| [living-doc-collector-gh#164](https://github.com/AbsaOSS/living-doc-collector-gh/issues/164) | `diagnostics` | `SOURCE_UNAVAILABLE` `EMPTY_SOURCE` `utils/artifact.py` `source_context` `allow-partial` | `when:allow-partial` |
| [living-doc-collector-gh#165](https://github.com/AbsaOSS/living-doc-collector-gh/issues/165) | `action` | `action.yml` `bin/python` `Scripts/` `SPEC.md` `integration_test.yml` | `when:windows-runner` |
| [living-doc-collector-gh#166](https://github.com/AbsaOSS/living-doc-collector-gh/issues/166) | `docs` `release` | `DEVELOPER.md` `MAJOR` `v1.0.1` | `when:next-pr` |
| [living-doc-generator-markdown#39](https://github.com/AbsaOSS/living-doc-generator-markdown/issues/39) | `action` | `action.yml` `github.action_path` `GITHUB_ACTION_PATH` | `when:container-job` |
| [living-doc-generator-markdown#40](https://github.com/AbsaOSS/living-doc-generator-markdown/issues/40) | `rendering` | `sources_failed` `source_inputs` `rendering.md` `allow-partial` | `when:allow-partial` |
| [living-doc-generator-markdown#41](https://github.com/AbsaOSS/living-doc-generator-markdown/issues/41) | `rendering` `security` | `presentation.py::_outline` `_NESTED_ITEM_RE` | `when:security-review` |
| [living-doc-toolkit#114](https://github.com/AbsaOSS/living-doc-toolkit/issues/114) | `docs` `testing` | `tests/docs/test_anchors.py` `## Code map` `CONTEXT.md` | `when:reported` |
| [living-doc-toolkit#115](https://github.com/AbsaOSS/living-doc-toolkit/issues/115) | `action` | `--document-version` `document.version` `action.yml` | `when:pilot` |
| [living-doc-toolkit#116](https://github.com/AbsaOSS/living-doc-toolkit/issues/116) | `ci` `docs` | `Makefile` `.github/dependabot.yml` `.gitignore` `py-qa` | `when:next-pr` |
| [living-doc-toolkit#117](https://github.com/AbsaOSS/living-doc-toolkit/issues/117) | `contract` | `MULTIPLE_DOCUMENTATION_SOURCES` `MIXED_DOCUMENTATION_SOURCES` `pipeline-rules.md` | `when:pilot` |
| [living-doc-toolkit#118](https://github.com/AbsaOSS/living-doc-toolkit/issues/118) | `diagnostics` | `normalize-docs` `--input` `MULTIPLE_DOCUMENTATION_SOURCES` `validate_inputs` `normalize_docs.py` | `when:next-pr` |
| [living-doc-toolkit#119](https://github.com/AbsaOSS/living-doc-toolkit/issues/119) | `docs` `testing` | `tests/docs/pages.py` `_CODE_SPAN` `_LINE_NUMBER_RE` | `when:reported` |
| [living-doc-toolkit#120](https://github.com/AbsaOSS/living-doc-toolkit/issues/120) | `docs` `release` | `SPEC.md` `.github/copilot-review-rules.md` `major bump` | `when:next-pr` |
| [living-doc-utilities#222](https://github.com/AbsaOSS/living-doc-utilities/issues/222) | `parser` `gh-issues` | `issue_body.py::_read_bullets` `MISINDENTED_LINE` `AUTHORING_WARNING` `authoring-formats.md` | `when:issues-source` |
| [living-doc-utilities#223](https://github.com/AbsaOSS/living-doc-utilities/issues/223) | `parser` `gh-issues` | `parse_issue_body` `framing.py::frame_issue_body` `accounting.py::unplaced_lines` `MALFORMED_AC` `html_to_markdown` | `when:issues-source` |
| [living-doc-utilities#224](https://github.com/AbsaOSS/living-doc-utilities/issues/224) | `parser` `input-checks` | `living-doc-check` `[project.scripts]` `AUTHORING_ERROR` `REQUIRED_FEATURE_KEYS` | `when:input-checks` |
| [living-doc-utilities#225](https://github.com/AbsaOSS/living-doc-utilities/issues/225) | `contract` | `NEVER_CARRIED_PATHS` `producer.build` `full_sample` `doc_entities.py` | `when:contract-minor` |
| [living-doc-utilities#226](https://github.com/AbsaOSS/living-doc-utilities/issues/226) | `contract` | `-v1.0.0` `schema_version` `read_artifact` | `when:v1` |
| [living-doc-utilities#227](https://github.com/AbsaOSS/living-doc-utilities/issues/227) | `dependencies` | `pyproject.toml` `optional-dependencies` `github/rate_limiter.py` `github/decorators.py` `nh3` | `when:utilities-release` |
| [living-doc-utilities#228](https://github.com/AbsaOSS/living-doc-utilities/issues/228) | `contract` | `EntityCoverage` `coverage_matrix.py` `coverage-matrix` | `when:reported` |
| [living-doc-utilities#229](https://github.com/AbsaOSS/living-doc-utilities/issues/229) | `contract` `parser` | `AcLink` `STALE_AC_REF` `ui-tests.json` `coverage-matrix` | `when:contract-minor` |
| [living-doc-utilities#230](https://github.com/AbsaOSS/living-doc-utilities/issues/230) | `ci` | `.github/workflows/link-check.yml` `workflow_dispatch` `docs_changed` | `when:next-pr` |
| [living-doc-utilities#231](https://github.com/AbsaOSS/living-doc-utilities/issues/231) | `parser` | `authoring/normalize.py` `_rewrite_scenario_file` `inline_ac_description` `_report_rewrites` | `when:utilities-release` |
| [living-doc-utilities#232](https://github.com/AbsaOSS/living-doc-utilities/issues/232) | `contract` `testing` | `component-checks.md` `metadata.stats` `source_inputs` `sources_failed` `FIELD_LOSS` | `when:pilot` |
| [living-doc-utilities#233](https://github.com/AbsaOSS/living-doc-utilities/issues/233) | `contract` `docs` | `artifact-rules.md` `component-checks.md` `LineageEntry` `check_field_loss` `selected_stats` `FIELD_LOSS` | `when:contract-minor` |
| [living-doc-utilities#234](https://github.com/AbsaOSS/living-doc-utilities/issues/234) | `contract` | `SourceRef` `scenario_id` `native_id` `normalize-tests` `ui_tests/collector.py` | `when:contract-minor` |
