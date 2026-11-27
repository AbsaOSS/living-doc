# Tutorial: GitHub Source Code → Markdown

## Purpose

This page is one complete workflow: GitHub source code to the technical project, the test catalog and the coverage
matrix in Markdown, refreshed on every push or attached to each release. A pull-request check fails a header the
collector would drop or misread, before the merge.

Use this when living documentation is authored [directly in code](../reference/authoring-formats.md) — today's
documentation source; issues are planned ([Choosing a documentation source](../guides/choosing-a-documentation-source.md)).

Read before: [Build a pipeline](../guides/build-a-pipeline.md) · Next: [Document types](../guides/living-doc-document-types.md)

## Contents

- [1. Prepare the inputs](#1-prepare-the-inputs)
- [2. Add the workflow](#2-add-the-workflow)
- [3. What happens on each run](#3-what-happens-on-each-run)
- [4. Verify](#4-verify)
- [5. Attach the documents to a release](#5-attach-the-documents-to-a-release)
- [6. Check a pull request before the merge](#6-check-a-pull-request-before-the-merge)
- [Related](#related)

## 1. Prepare the inputs

| Document type you want | What must be in the repo |
|---|---|
| [Technical project](../guides/living-doc-document-types.md#technical-project) | User Story headers in `.feature` files under `features/liv_doc_us/`, Functionality headers under `features/liv_doc_func/`, and Feature headers in PageObjects under `pages/`, in the [documented format](../reference/authoring-formats.md) |
| [Test catalog](../guides/living-doc-document-types.md#test-catalog) | Gherkin scenarios in the `.feature` files under `features/`, with `@AC:` tags |
| [Coverage matrix](../guides/living-doc-document-types.md#coverage-matrix) | Both of the above, with the scenarios tagging the headers' acceptance-criterion IDs |

Other folders work too: change the paths in the collect step. `func-paths` and `pages-paths` are optional; drop
either if the folder does not exist, since every configured folder must
([repository entry](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/doc_source/README.md#repository-entry)).

## 2. Add the workflow

`.github/workflows/living-doc.yml`:

```yaml
name: Living Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

# A newer push replaces a refresh still running, so two runs never push over each other.
concurrency:
  group: living-doc
  cancel-in-progress: true

jobs:
  living-doc:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v7

      # toolkit and generator-markdown need Python 3.10 or later on the runner
      - uses: actions/setup-python@v7
        with:
          python-version: '3.14'

      # 1. COLLECT the headers (doc-source) and the scenarios (ui-tests) into output/collector-gh/
      - name: Collect from source
        uses: AbsaOSS/living-doc-collector-gh@v0.3.0
        with:
          project-id: your-project
          doc-source: true
          doc-source-repositories: |
            [{"organization-name": "${{ github.repository_owner }}",
              "repository-name": "${{ github.event.repository.name }}",
              "us-paths": ["${{ github.workspace }}/features/liv_doc_us"],
              "func-paths": ["${{ github.workspace }}/features/liv_doc_func"],
              "pages-paths": ["${{ github.workspace }}/pages"]}]
          ui-tests: true
          ui-tests-repositories: |
            [{"organization-name": "${{ github.repository_owner }}",
              "repository-name": "${{ github.event.repository.name }}",
              "paths": ["${{ github.workspace }}/features"]}]

      # 2. NORMALIZE: one toolkit step per document, in the inner view, into output/toolkit/
      - name: Normalize the documentation
        uses: AbsaOSS/living-doc-toolkit@v0.2.0
        with:
          command: normalize-docs
          input: output/collector-gh/doc-source/doc-source.json
          output: output/toolkit/generator-ready.json
          view: inner
      - name: Normalize the tests
        uses: AbsaOSS/living-doc-toolkit@v0.2.0
        with:
          command: normalize-tests
          input: output/collector-gh/doc-source/doc-source.json
          tests-input: output/collector-gh/ui-tests/ui-tests.json
          output: output/toolkit/ui-test-catalog.json
          view: inner
      - name: Join them into a coverage matrix
        uses: AbsaOSS/living-doc-toolkit@v0.2.0
        with:
          command: coverage-matrix
          input: output/collector-gh/doc-source/doc-source.json
          tests-input: output/collector-gh/ui-tests/ui-tests.json
          output: output/toolkit/coverage-matrix.json
          view: inner

      # 3. GENERATE one Markdown document per step, each with its run report, into docs/living-doc/
      - name: Render the technical project
        uses: AbsaOSS/living-doc-generator-markdown@v0.2.0
        with:
          document-type: technical-project
          source-path: output/toolkit/generator-ready.json
          output-path: docs/living-doc
      - name: Render the test catalog
        uses: AbsaOSS/living-doc-generator-markdown@v0.2.0
        with:
          document-type: ui-test-catalog
          source-path: output/toolkit/ui-test-catalog.json
          output-path: docs/living-doc
      - name: Render the coverage matrix
        uses: AbsaOSS/living-doc-generator-markdown@v0.2.0
        with:
          document-type: coverage-matrix
          source-path: output/toolkit/coverage-matrix.json
          output-path: docs/living-doc

      # 4. COMMIT each document together with its run report
      - name: Commit the documents
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add docs/living-doc
          git commit -m "docs: refresh living documentation" || echo "no changes"
          git push
```

Change `your-project` to your project's id
([Project id](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#project-id)).
To refresh nightly as well, add `schedule: [{cron: '0 4 * * *'}]` under `on:`.
This workflow renders the inner view, which keeps everything; § 5 renders the release view for each release
([Rendering rules — Views](../reference/rendering-rules.md#views)). `normalize-tests` reads both files, so each link
in the test catalog carries its criterion's state
([Rendering rules — Test catalog](../reference/rendering-rules.md#test-catalog)).
Every input of each step: [`collector-gh`](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md#inputs),
[`toolkit`](https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/action.md#inputs),
[`generator-markdown`](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/docs/action.md#inputs).

## 3. What happens on each run

1. `collector-gh` parses the header blocks into `output/collector-gh/doc-source/doc-source.json` and the scenarios
   into `output/collector-gh/ui-tests/ui-tests.json`.
2. `toolkit` writes one file per document under `output/toolkit/`: `generator-ready.json`, `ui-test-catalog.json`
   and `coverage-matrix.json` ([Data flows — Commands](../reference/data-flows.md#commands)).
3. `generator-markdown` renders `technical-project-inner.md`, `ui-test-catalog-inner.md` and
   `coverage-matrix-inner.md` into `docs/living-doc/`, each beside its run report, `.run-report.json` in place of
   `.md`
   ([`generator-markdown` files](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/docs/action.md#files)).
4. The workflow commits `docs/living-doc/`: each document with its run report, which lists what the document shows,
   so the report's diff shows what changed. `output/` is not committed. A commit pushed with the job's token starts
   no new run.

## 4. Verify

After the first run, `docs/living-doc/` holds six files: three documents and their run reports. The technical project
lists your User Stories, the test catalog your scenarios, and the coverage matrix each criterion's verdict. A run
that warns or fails names a code: [Error codes](../reference/errors.md). The six documents these tags rendered over
the testbed, in both views, are in [`docs/_integration/go-no-go/testbed-core/`](../_integration/go-no-go/testbed-core/release/generator-markdown/technical-project-release-v0.1.0.md).

## 5. Attach the documents to a release

A second workflow, `.github/workflows/living-doc-release.yml`, is § 2's with a new `name:` and `on:`, no
`concurrency:` block, the release view in steps 2 and 3, and step 4 replaced.

```yaml
name: Living Documentation release

on:
  release:
    types: [published]

jobs:
  living-doc:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      # The checkout, the Python setup and step 1 (COLLECT) exactly as in § 2

      # 2. NORMALIZE: § 2's three toolkit steps, each in the release view
      - name: Normalize the documentation
        uses: AbsaOSS/living-doc-toolkit@v0.2.0
        with:
          command: normalize-docs
          input: output/collector-gh/doc-source/doc-source.json
          output: output/toolkit/generator-ready.json
          view: release
      - name: Normalize the tests
        uses: AbsaOSS/living-doc-toolkit@v0.2.0
        with:
          command: normalize-tests
          input: output/collector-gh/doc-source/doc-source.json
          tests-input: output/collector-gh/ui-tests/ui-tests.json
          output: output/toolkit/ui-test-catalog.json
          view: release
      - name: Join them into a coverage matrix
        uses: AbsaOSS/living-doc-toolkit@v0.2.0
        with:
          command: coverage-matrix
          input: output/collector-gh/doc-source/doc-source.json
          tests-input: output/collector-gh/ui-tests/ui-tests.json
          output: output/toolkit/coverage-matrix.json
          view: release

      # 3. GENERATE the release's documents, named by its tag, into output/living-doc-release/
      - name: Render the technical project
        uses: AbsaOSS/living-doc-generator-markdown@v0.2.0
        with:
          document-type: technical-project
          source-path: output/toolkit/generator-ready.json
          output-path: output/living-doc-release
          release-version: ${{ github.event.release.tag_name }}
      - name: Render the test catalog
        uses: AbsaOSS/living-doc-generator-markdown@v0.2.0
        with:
          document-type: ui-test-catalog
          source-path: output/toolkit/ui-test-catalog.json
          output-path: output/living-doc-release
          release-version: ${{ github.event.release.tag_name }}
      - name: Render the coverage matrix
        uses: AbsaOSS/living-doc-generator-markdown@v0.2.0
        with:
          document-type: coverage-matrix
          source-path: output/toolkit/coverage-matrix.json
          output-path: output/living-doc-release
          release-version: ${{ github.event.release.tag_name }}

      # 4. ATTACH each document and its run report to the release
      - name: Attach the documents to the release
        env:
          GH_TOKEN: ${{ github.token }}
          TAG: ${{ github.event.release.tag_name }}
        run: gh release upload "$TAG" output/living-doc-release/* --repo "$GITHUB_REPOSITORY" --clobber
```

On each published release:

- The checkout is the release's tag, so the documents show the code as released.
- Steps 2 and 3 render the release view, and the release's tag names each file: a release `v1.2.0` gets
  `technical-project-release-v1.2.0.md`, `ui-test-catalog-release-v1.2.0.md` and `coverage-matrix-release-v1.2.0.md`
  ([`generator-markdown` files](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/docs/action.md#files)).
- They go to `output/living-doc-release/`, not `docs/living-doc/`: the tag's checkout holds the inner documents § 2
  committed, which the release does not attach.
- Step 4 attaches the six files to the release as assets; `--clobber` replaces them when the run is re-run.
- Nothing is committed: the checkout is a tag, not a branch, so there is no branch to push to.
- The workflow has no `concurrency:` block: in § 2's `living-doc` group, a push would cancel a release run.
- `published` also fires for a pre-release; `types: [released]` leaves pre-releases out.
- A release published with the job's token starts no run; publish it by hand or with another token.
- The workflow must be in the tagged commit: a release of an older commit starts no run.
- An immutable release takes no assets once published, so step 4 fails where immutable releases are on.
- To name the release in a title, set a render step's `document-title`, for example
  `Technical project ${{ github.event.release.tag_name }}`
  ([`generator-markdown` inputs](https://github.com/AbsaOSS/living-doc-generator-markdown/blob/master/docs/action.md#inputs)).

## 6. Check a pull request before the merge

A third workflow, `.github/workflows/living-doc-check.yml`, checks the living-doc files a pull request changes. It
runs `collector-gh`'s `doc-check` mode, which reports each finding on its line and fails on the policy's codes
([Documentation Check mode](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/doc_check/README.md)).

```yaml
name: Living Documentation check

on:
  pull_request:
    # the folders the collect step of § 2 reads
    paths:
      - features/liv_doc_us/**
      - features/liv_doc_func/**
      - pages/**

jobs:
  living-doc-check:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0                   # the base commit, for the diff

      # 1. LIST the paths the pull request changes, one per line
      - name: List the changed paths
        id: changed
        env:
          BASE: ${{ github.event.pull_request.base.sha }}
        run: |
          { echo 'paths<<EOF'; git -c core.quotePath=false diff --name-only "$BASE...HEAD"; echo 'EOF'; } >> "$GITHUB_OUTPUT"

      # 2. CHECK the changed living-doc files, with the doc-source-repositories of § 2
      - name: Check the changed living-doc files
        uses: AbsaOSS/living-doc-collector-gh@v0.3.0
        with:
          project-id: your-project
          doc-check: true
          doc-source-repositories: |
            [{"organization-name": "${{ github.repository_owner }}",
              "repository-name": "${{ github.event.repository.name }}",
              "us-paths": ["${{ github.workspace }}/features/liv_doc_us"],
              "func-paths": ["${{ github.workspace }}/features/liv_doc_func"],
              "pages-paths": ["${{ github.workspace }}/pages"]}]
          doc-check-changed-paths: ${{ steps.changed.outputs.paths }}
```

On each pull request:

- `paths:` holds § 2's folders, so a pull request that changes none of them starts no run. Change both together.
- The checkout is the pull request merged into its base; `fetch-depth: 0` brings the base commit for the diff.
- `core.quotePath=false` prints a non-ASCII path as it is; quoted, it would match no file and go unchecked.
- The mode skips each changed path outside those folders, and each deleted file; with none left, it passes
  ([Changed paths](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/doc_check/README.md#changed-paths)).
- So a pull request that only deletes a file passes, even when other files relate to it.
- Otherwise it reports the changed files' own findings, and every broken relation among all the files it reads.
- Each finding is a log line and a row in the job summary, and an annotation on its line while GitHub's limit
  lasts ([Report](https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/doc_check/README.md#report)).
- It runs alone and writes nothing: § 2 and § 5 still build the documents.
- A required check that `paths:` skips stays pending and blocks the merge; drop `paths:` to make it required.

### The policy file

`living-doc-policy.yaml`, at the repository root, names the codes that only warn. Without it, every code of the
default fail list fails ([Policy file](https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/check.md#policy-file)).

```yaml
check:
  warn:            # these codes still print, but no longer fail
    - LEGACY_AC_STATE
```

- Here a criterion in a retired state only warns, while the project moves to the four states
  ([`LEGACY_AC_STATE`](../reference/errors.md#codes)).
- A code under `warn:` still shows in the log and the summary, and the step passes on it.
- To relax another code, add it to the list; to make a code fail again, remove it.
- A code outside the default fail list, or another key under `check:`, fails the step with `INVALID_CONFIGURATION`.
- The check reads the policy only when a header changes, so a pull request that changes only the policy passes.

### Example: a broken criterion header

In the testbed's
[FUNC-008](https://github.com/AbsaOSS/living-doc-testbed/blob/master/projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature),
a pull request drops the hyphen from one criterion's header line:

```diff
-#   AC:FUNC-008-02 (v1.0.0 - active)
+#   AC:FUNC-008-02 (v1.0.0 active)
```

The check fails, and the step's log reads:

```text
projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature:16: MALFORMED_AC Acceptance criterion failed validation: state: Input should be 'planned', 'in_review', 'active' or 'deprecated'. Fix: Write 'AC:<id> (v<major.minor.patch> - <state>)', or 'AC:<id> (planned)' for a backlog criterion.
projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature:17: AUTHORING_WARNING Line of a dropped acceptance criterion is not read. Fix: Put the line under the field it belongs to, or remove it: nothing reads it.
projects/core/tests/e2e/features/liv_doc_func/func-008-sort-results.feature:18: AUTHORING_WARNING Line of a dropped acceptance criterion is not read. Fix: Put the line under the field it belongs to, or remove it: nothing reads it.
```

- The testbed's folders sit under `projects/core/tests/e2e/`, so its `paths:` and `*-paths` start with that prefix.
- Each path in the log starts at the repository root.
- Line 16 is no criterion any more, so lines 17 and 18, its description, belong to no field.
- All three fail under the default policy; fixing line 16 clears them all.
- Without the check, § 2's run passes: it warns `MALFORMED_AC` and drops the criterion from the documents.

## Related

- [GitHub Issues → Markdown](gh-issues-to-markdown.md) — the same output from issues instead of code *(planned)*
- [GitHub Source → PDF](gh-source-to-pdf.md) — same inputs, PDF output *(planned)*
- [Authoring formats](../reference/authoring-formats.md) — the source-code format being mined
- [Living Documentation Document Types](../guides/living-doc-document-types.md)
