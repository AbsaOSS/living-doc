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
# (tools/check_collector_stage.py), then write the normalized JSON in the collector's own output layout:
# <out>/collector-gh/<mode>/<artifact>.json.
#
#   tools/regen-collector-snapshots.sh                # -> docs/examples/_expected/ (regen & commit)
#   tools/regen-collector-snapshots.sh /tmp/actual    # -> /tmp/actual/ (CI: diff against _expected)
#
# The pinned collector (tools/collector-snapshot-pins.env), the venv it runs in and the run itself come from
# tools/collector-gh.sh, which tools/run-testbed-stage.sh shares. No token: neither mode reads a credential.
#
# Environment (both optional):
#   PYTHON      the interpreter the venv is built from (default: python3, else python - the first that runs)
#   CORPUS_DIR  the corpus to mine (default: docs/examples) - e.g. a modified copy, to see an assertion fail
#
# Runs in bash 3.2 or later: Linux, macOS, or Git Bash on Windows.

set -euo pipefail

# shellcheck source=tools/collector-gh.sh
source "$(dirname "${BASH_SOURCE[0]}")/collector-gh.sh"

REPO_ROOT="$(native_dir "$(dirname "${BASH_SOURCE[0]}")/..")"
OUT_DIR="${1:-$REPO_ROOT/docs/examples/_expected}"
CORPUS_DIR="$(native_dir "${CORPUS_DIR:-$REPO_ROOT/docs/examples}")"
PROJECT_ID="living-doc-examples"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
WORK_DIR="$(native_dir "$WORK_DIR")"

collector_gh_setup

OUTPUT_ROOT="$WORK_DIR/output"
echo "==> mining $CORPUS_DIR (project-id $PROJECT_ID)"
collector_gh_run "$PROJECT_ID" "$OUTPUT_ROOT" \
  "$(collector_gh_repositories AbsaOSS living-doc \
    "us-paths=$CORPUS_DIR/gherkin/liv_doc_us" \
    "func-paths=$CORPUS_DIR/gherkin/liv_doc_func" \
    "pages-paths=$CORPUS_DIR/pageobject")" \
  "$(collector_gh_repositories AbsaOSS living-doc "paths=$CORPUS_DIR/gherkin")"

echo "==> validating and asserting the collector stage"
"$VPY" -E -X utf8 "$REPO_ROOT/tools/check_collector_stage.py" "$OUTPUT_ROOT"

rm -rf "$OUT_DIR/collector-gh"
for mode in doc-source ui-tests; do
  mkdir -p "$OUT_DIR/collector-gh/$mode"
  "$VPY" -E -X utf8 "$REPO_ROOT/tools/normalize_snapshot.py" \
    < "$OUTPUT_ROOT/$mode/$mode.json" > "$OUT_DIR/collector-gh/$mode/$mode.json"
done

echo "==> wrote normalized snapshots to $OUT_DIR/collector-gh/"
