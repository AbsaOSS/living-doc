#!/usr/bin/env bash
#
# Copyright 2026 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Run the pinned living-doc-collector-gh (`doc-source` + `ui-tests`) over docs/examples/ in a venv of its own,
# validate each artifact against its contract and assert the collector stage's first-stage content
# (tests/examples/check_collector_stage.py). Then run the pinned living-doc-toolkit over the collector's raw output
# in a venv of its own, validate and assert each of its artifacts the same way (tests/examples/check_toolkit_stage.py).
# Only when every check passed, write the normalized JSON: <out>/collector-gh/<mode>/<artifact>.json, in the
# collector's own output layout, and <out>/toolkit/gh-headers/{generator-ready.inner,generator-ready.release,
# coverage-matrix}.json and <out>/toolkit/tests/ui-test-catalog.json.
#
#   tests/examples/regen-collector-snapshots.sh                # -> docs/examples/_expected/ (regen & commit)
#   tests/examples/regen-collector-snapshots.sh /tmp/actual    # -> /tmp/actual/ (CI: diff against _expected)
#
# The pinned collector and toolkit (tests/collector/collector-pins.env), the venvs they run in and the runs themselves
# come from tests/collector/collector-gh.sh and tests/collector/toolkit.sh, which tests/testbed/run-testbed-stage.sh
# shares. No token: neither mode reads a credential.
#
# Environment (both optional):
#   PYTHON      the interpreter the venvs are built from (default: python3, else python - the first that runs)
#   CORPUS_DIR  the corpus to mine (default: docs/examples) - e.g. a modified copy, to see an assertion fail
#
# Runs in bash 3.2 or later: Linux, macOS, or Git Bash on Windows.

set -euo pipefail

# shellcheck source=tests/collector/collector-gh.sh
source "$(dirname "${BASH_SOURCE[0]}")/../collector/collector-gh.sh"
# shellcheck source=tests/collector/toolkit.sh
source "$(dirname "${BASH_SOURCE[0]}")/../collector/toolkit.sh"

REPO_ROOT="$(native_dir "$(dirname "${BASH_SOURCE[0]}")/../..")"
OUT_DIR="${1:-$REPO_ROOT/docs/examples/_expected}"
CORPUS_DIR="$(native_dir "${CORPUS_DIR:-$REPO_ROOT/docs/examples}")"
PROJECT_ID="living-doc-examples"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
WORK_DIR="$(native_dir "$WORK_DIR")"

collector_gh_setup
toolkit_setup

OUTPUT_ROOT="$WORK_DIR/output"
echo "==> mining $CORPUS_DIR (project-id $PROJECT_ID)"
collector_gh_run "$PROJECT_ID" "$OUTPUT_ROOT" \
  "$(collector_gh_repositories AbsaOSS living-doc \
    "us-paths=$CORPUS_DIR/gherkin/liv_doc_us" \
    "func-paths=$CORPUS_DIR/gherkin/liv_doc_func" \
    "pages-paths=$CORPUS_DIR/pageobject")" \
  "$(collector_gh_repositories AbsaOSS living-doc "paths=$CORPUS_DIR/gherkin")"

echo "==> validating and asserting the collector stage"
"$VPY" -E -X utf8 "$REPO_ROOT/tests/examples/check_collector_stage.py" "$OUTPUT_ROOT"

TOOLKIT_OUTPUT="$WORK_DIR/toolkit-output"
DOC_SOURCE="$OUTPUT_ROOT/doc-source/doc-source.json"
UI_TESTS="$OUTPUT_ROOT/ui-tests/ui-tests.json"
echo "==> running the toolkit over the collector's output"
toolkit_chain "$DOC_SOURCE" "$UI_TESTS" "$TOOLKIT_OUTPUT"

echo "==> validating and asserting the toolkit stage"
"$TOOLKIT_PY" -E -X utf8 "$REPO_ROOT/tests/examples/check_toolkit_stage.py" "$TOOLKIT_OUTPUT" "$DOC_SOURCE" "$UI_TESTS"

rm -rf "$OUT_DIR/collector-gh" "$OUT_DIR/toolkit"
for mode in doc-source ui-tests; do
  mkdir -p "$OUT_DIR/collector-gh/$mode"
  "$VPY" -E -X utf8 "$REPO_ROOT/tests/examples/normalize_snapshot.py" \
    < "$OUTPUT_ROOT/$mode/$mode.json" > "$OUT_DIR/collector-gh/$mode/$mode.json"
done
for artifact in gh-headers/generator-ready.inner gh-headers/generator-ready.release gh-headers/coverage-matrix \
                tests/ui-test-catalog; do
  mkdir -p "$OUT_DIR/toolkit/$(dirname "$artifact")"
  "$TOOLKIT_PY" -E -X utf8 "$REPO_ROOT/tests/examples/normalize_snapshot.py" \
    < "$TOOLKIT_OUTPUT/$artifact.json" > "$OUT_DIR/toolkit/$artifact.json"
done

echo "==> wrote normalized snapshots to $OUT_DIR/collector-gh/ and $OUT_DIR/toolkit/"
