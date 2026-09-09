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
# Run the pinned living-doc-collector-gh (doc-source + ui-tests) and the pinned
# living-doc-toolkit (coverage-matrix) over docs/examples/gherkin/ and write the
# normalized JSON to a target directory.
#
#   tools/regen-collector-snapshots.sh                       # -> docs/examples/_expected/ (regen & commit)
#   tools/regen-collector-snapshots.sh /tmp/actual           # -> /tmp/actual/ (CI: diff against _expected)
#
# Pinned refs come from tools/collector-snapshot-pins.env (the one place to bump them).
# A GitHub token is required only for the collector's start-up connectivity check:
# GITHUB_TOKEN in CI, or `gh auth token` locally.

set -euo pipefail

# `pwd -W` (a Git-for-Windows builtin) yields a native C:/... path the bundled Python can read;
# it errors on Linux, where plain `pwd` is already correct.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && { pwd -W 2>/dev/null || pwd; })"
OUT_DIR="${1:-$REPO_ROOT/docs/examples/_expected}"
CORPUS_DIR="$REPO_ROOT/docs/examples/gherkin"

# shellcheck source=tools/collector-snapshot-pins.env
source "$REPO_ROOT/tools/collector-snapshot-pins.env"

for ref_name in COLLECTOR_GH_REF TOOLKIT_REF; do
  ref_value="${!ref_name}"
  if [[ "$ref_value" =~ ^(master|main|HEAD|develop)$ || -z "$ref_value" ]]; then
    echo "ERROR: $ref_name='$ref_value' must be a tag or a full commit SHA, not a floating branch." >&2
    exit 2
  fi
done

GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || true)}"
if [[ -z "$GITHUB_TOKEN" ]]; then
  echo "ERROR: set GITHUB_TOKEN (or run 'gh auth login') - the collector needs it for its start-up check." >&2
  exit 2
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

echo "==> collector-gh @ $COLLECTOR_GH_REF"
git clone --quiet --filter=blob:none https://github.com/AbsaOSS/living-doc-collector-gh "$WORK_DIR/collector-gh"
git -C "$WORK_DIR/collector-gh" checkout --quiet "$COLLECTOR_GH_REF"
pip install --quiet -r "$WORK_DIR/collector-gh/requirements.txt"

echo "==> toolkit @ $TOOLKIT_REF"
git clone --quiet --filter=blob:none https://github.com/AbsaOSS/living-doc-toolkit "$WORK_DIR/toolkit"
git -C "$WORK_DIR/toolkit" checkout --quiet "$TOOLKIT_REF"
# requirements.txt uses editable paths relative to the repo root, so install from there.
( cd "$WORK_DIR/toolkit" && pip install --quiet -r requirements.txt )

RUN_DIR="$WORK_DIR/run"
mkdir -p "$RUN_DIR"

echo "==> mining docs/examples/gherkin/"
cd "$RUN_DIR"
export INPUT_GITHUB_TOKEN="$GITHUB_TOKEN"
export INPUT_DOC_ISSUES="false"
export INPUT_DOC_SOURCE="true"
export INPUT_UI_TESTS="true"
export INPUT_DOC_SOURCE_REPOSITORIES="[{\"organization-name\":\"AbsaOSS\",\"repository-name\":\"living-doc\",\"us-paths\":[\"$CORPUS_DIR/liv_doc_us\"],\"func-paths\":[\"$CORPUS_DIR/liv_doc_func\"]}]"
export INPUT_UI_TESTS_REPOSITORIES="[{\"organization-name\":\"AbsaOSS\",\"repository-name\":\"living-doc\",\"paths\":[\"$CORPUS_DIR\"]}]"
python "$WORK_DIR/collector-gh/main.py"

echo "==> coverage-matrix"
living-doc coverage-matrix \
  --doc-input "$RUN_DIR/output/doc-source/doc-source.json" \
  --tests-input "$RUN_DIR/output/ui-tests/ui-tests.json" \
  --output "$RUN_DIR/coverage-matrix.json"

mkdir -p "$OUT_DIR"
norm() { python "$REPO_ROOT/tools/normalize_snapshot.py" < "$1" > "$2"; }
norm "$RUN_DIR/output/doc-source/doc-source.json" "$OUT_DIR/doc-source.json"
norm "$RUN_DIR/output/ui-tests/ui-tests.json"     "$OUT_DIR/ui-tests.json"
norm "$RUN_DIR/coverage-matrix.json"              "$OUT_DIR/coverage-matrix.json"

echo "==> wrote normalized snapshots to $OUT_DIR"
