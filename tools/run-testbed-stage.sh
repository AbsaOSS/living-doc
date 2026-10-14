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
# Run the pinned living-doc-collector-gh (`doc-source` + `ui-tests`) over the `core` project of
# AbsaOSS/living-doc-testbed, read at its current master, and assert invariants on what it produces
# (tools/check_testbed_stage.py): `core` follows the canon 100 %, so any warning is a defect. Every count comes from
# the checkout at run time; nothing about `core`'s content is written down here. Then run each derived problem case
# (integration/testbed_cases.py) over a copy of `core` and assert the one warning it must raise.
#
#   tools/run-testbed-stage.sh                      # shallow-clones the testbed's master
#   tools/run-testbed-stage.sh <testbed-checkout>   # reads a checkout already made (CI: actions/checkout)
#
# The testbed is only read: never pinned, never written to - the stage fails if it leaves the checkout changed. Its
# collector paths, project-id and cases live in living-doc, never in the testbed. The collector, its venv and the run
# come from tools/collector-gh.sh, shared with tools/regen-collector-snapshots.sh. No token.
#
# Environment (both optional):
#   PYTHON                the interpreter the collector's venv is built from (see tools/collector-gh.sh)
#   GITHUB_STEP_SUMMARY   set in CI: the testbed SHA and the checks' output are appended to it
#
# Runs in bash 3.2 or later: Linux, macOS, or Git Bash on Windows.

set -euo pipefail

# shellcheck source=tools/collector-gh.sh
source "$(dirname "${BASH_SOURCE[0]}")/collector-gh.sh"

REPO_ROOT="$(native_dir "$(dirname "${BASH_SOURCE[0]}")/..")"

# --- The stage's configuration: the consumer owns it, the testbed holds content only ------------------------------
TESTBED_URL="https://github.com/AbsaOSS/living-doc-testbed"
TESTBED_ORG="AbsaOSS"
TESTBED_REPO="living-doc-testbed"
PROJECT_ID="testbed-core"
CORE="projects/core"
US_PATHS="$CORE/tests/e2e/features/liv_doc_us"
FUNC_PATHS="$CORE/tests/e2e/features/liv_doc_func"
PAGES_PATHS="$CORE/tests/e2e/pages"
# `ui-tests` reads the whole test tree, not only the living-doc folders: a folder outside living doc (`smoke/`) is read
# the way a team pointing the collector at its tests would have it read, so "no AC link" tests something. "No entity"
# holds by configuration: no `doc-source` path above names `smoke/`.
SCENARIO_PATHS="$CORE/tests/e2e/features"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
WORK_DIR="$(native_dir "$WORK_DIR")"

collector_gh_setup

if [[ $# -ge 1 ]]; then
  TESTBED="$(native_dir "$1")"
else
  git clone --quiet --depth 1 "$TESTBED_URL" "$WORK_DIR/testbed"
  TESTBED="$WORK_DIR/testbed"
fi
TESTBED_SHA="$(git -C "$TESTBED" rev-parse HEAD)"
echo "==> living-doc-testbed @ $TESTBED_SHA"
# Every file in the checkout, tracked or not, ignored or not, as it is before the stage: it must be the same after.
testbed_status() { git -C "$TESTBED" status --porcelain --ignored --untracked-files=all; }
TESTBED_STATUS="$(testbed_status)"

summary() {
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then printf '%s\n' "$@" >> "$GITHUB_STEP_SUMMARY"; fi
}
summary "### Collector stage over the testbed's \`$CORE\`" "" \
  "- living-doc-testbed \`master\` at [\`$TESTBED_SHA\`]($TESTBED_URL/commit/$TESTBED_SHA)" \
  "- collector-gh at \`$COLLECTOR_GH_REF\`" ""

# One run over a testbed root (the checkout, or a case's copy): `doc-source`, and `ui-tests` unless told otherwise.
mine() {
  local root="$1" output="$2" ui_tests=""
  if [[ "${3:-}" != "doc-source-only" ]]; then
    ui_tests="$(collector_gh_repositories "$TESTBED_ORG" "$TESTBED_REPO" "paths=$root/$SCENARIO_PATHS")"
  fi
  collector_gh_run "$PROJECT_ID" "$output" \
    "$(collector_gh_repositories "$TESTBED_ORG" "$TESTBED_REPO" \
      "us-paths=$root/$US_PATHS" \
      "func-paths=$root/$FUNC_PATHS" \
      "pages-paths=$root/$PAGES_PATHS")" \
    "$ui_tests"
}

# Runs one check, prints its output and appends it to the job summary under a title; the check's status is returned.
check() {
  local title="$1" status=0
  shift
  "$VPY" -E -X utf8 "$@" > "$WORK_DIR/check.txt" || status=$?
  tr -d '\r' < "$WORK_DIR/check.txt"
  summary "$title" '```' "$(tr -d '\r' < "$WORK_DIR/check.txt")" '```' ""
  return "$status"
}

failed=0

# A run or a case that cannot finish fails the stage and moves on, so the testbed write check below still runs.
echo "==> mining $CORE (project-id $PROJECT_ID)"
if mine "$TESTBED" "$WORK_DIR/core"; then
  echo "==> asserting the invariants over $CORE"
  check "**Invariants over \`$CORE\`**" "$REPO_ROOT/tools/check_testbed_stage.py" core "$WORK_DIR/core" "$TESTBED" \
    --us "$US_PATHS" --func "$FUNC_PATHS" --pages "$PAGES_PATHS" --scenarios "$SCENARIO_PATHS" || failed=1
else
  echo "ERROR: the collector failed over $CORE" >&2
  failed=1
fi

cases="$("$VPY" -E -X utf8 "$REPO_ROOT/integration/testbed_cases.py" --list | tr -d '\r')"
for case in $cases; do
  copy="$WORK_DIR/cases/$case"
  mkdir -p "$copy/$(dirname "$CORE")"
  cp -R "$TESTBED/$CORE" "$copy/$CORE"
  "$VPY" -E -X utf8 "$REPO_ROOT/integration/testbed_cases.py" "$case" "$copy/$CORE" | tr -d '\r' > "$copy.expected" \
    || { echo "ERROR: case $case could not be applied" >&2; failed=1; continue; }
  IFS=$'\t' read -r code line changed change < "$copy.expected"
  echo "==> case $case: ${changed#"$copy/"}, $change; expecting $code at line $line"
  # A git checkout, as a team's repository is: a file outside one has no source URL and is reported NO_SOURCE_URL.
  git -C "$copy" -c init.defaultBranch=master init --quiet
  git -C "$copy" remote add origin "$TESTBED_URL"
  git -C "$copy" -c core.autocrlf=false add --all
  # A throwaway commit in a temp dir: no identity of the runner's own, and never signed.
  git -C "$copy" -c user.name="testbed stage" -c user.email="testbed-stage@invalid" -c commit.gpgsign=false \
    commit --quiet --message "testbed case: $case"
  mine "$copy" "$WORK_DIR/cases/$case-output" doc-source-only \
    || { echo "ERROR: the collector failed over case $case" >&2; failed=1; continue; }
  check "**Case \`$case\`**: ${changed#"$copy/"}, $change; expecting $code at line $line" \
    "$REPO_ROOT/tools/check_testbed_stage.py" case "$WORK_DIR/cases/$case-output" "$code" "$line" "$changed" \
    || failed=1
done

# The stage reads the testbed and writes nothing into it: the collector's output and every case's copy live in the
# work dir. An ignored or untracked file counts too.
if [[ "$(testbed_status)" != "$TESTBED_STATUS" ]]; then
  echo "ERROR: the stage changed the testbed checkout at $TESTBED; its status now:" >&2
  testbed_status >&2
  failed=1
fi

if [[ "$failed" -ne 0 ]]; then
  echo "==> the testbed stage FAILED over living-doc-testbed @ $TESTBED_SHA" >&2
  exit 1
fi
echo "==> the testbed stage passed over living-doc-testbed @ $TESTBED_SHA"
