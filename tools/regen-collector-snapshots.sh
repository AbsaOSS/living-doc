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
# The pinned ref comes from tools/collector-snapshot-pins.env (the one place to bump it). No token: neither mode
# reads a credential. The venv is built from the collector's runtime requirements.txt at that ref and nothing else,
# so living-doc-utilities arrives only through that file: a skew between what the collector ships and what this
# job assumes fails here, as it would in a real pipeline.
#
# Environment (both optional):
#   PYTHON      the interpreter the venv is built from (default: python3, else python - the first that runs)
#   CORPUS_DIR  the corpus to mine (default: docs/examples) - e.g. a modified copy, to see an assertion fail
#
# Runs in bash 3.2 or later: Linux, macOS, or Git Bash on Windows.

set -euo pipefail

# `pwd -W` (a Git-for-Windows builtin) yields a native C:/... path the venv's Python can read;
# it errors on Linux, where plain `pwd` is already correct.
native_dir() { (cd "$1" && { pwd -W 2>/dev/null || pwd; }); }

REPO_ROOT="$(native_dir "$(dirname "${BASH_SOURCE[0]}")/..")"
OUT_DIR="${1:-$REPO_ROOT/docs/examples/_expected}"
CORPUS_DIR="$(native_dir "${CORPUS_DIR:-$REPO_ROOT/docs/examples}")"
PROJECT_ID="living-doc-examples"
# The collector's venv, reused only when the interpreter now resolved built it from the requirements.txt now pinned.
VENV="$REPO_ROOT/.snapshot-venvs/collector-gh"

# No mode reads a credential. Drop the token names a shell may still carry from collector versions that needed one,
# and every inherited action input, so the run sees exactly the inputs set below.
unset GITHUB_TOKEN GH_TOKEN GH_ENTERPRISE_TOKEN GITHUB_ENTERPRISE_TOKEN
for name in $(compgen -e); do
  case "$name" in INPUT_*) unset "$name" ;; esac
done

# shellcheck source=tools/collector-snapshot-pins.env
source "$REPO_ROOT/tools/collector-snapshot-pins.env"

# The pin MUST be an immutable ref: a full 40-hex commit SHA, or a tag that exists on the remote.
# Anything else (a branch name, a short SHA, a typo) is rejected so the snapshot stays reproducible.
COLLECTOR_GH_URL="https://github.com/AbsaOSS/living-doc-collector-gh"
if ! [[ "${COLLECTOR_GH_REF:-}" =~ ^[0-9a-f]{40}$ ]] \
   && ! { [[ -n "${COLLECTOR_GH_REF:-}" ]] && git ls-remote --tags --exit-code "$COLLECTOR_GH_URL" \
          "refs/tags/$COLLECTOR_GH_REF" >/dev/null 2>&1; }; then
  echo "ERROR: COLLECTOR_GH_REF='${COLLECTOR_GH_REF:-}' must be a full 40-hex commit SHA or an existing tag of $COLLECTOR_GH_URL." >&2
  exit 2
fi

# --- Python, as the collector's action.yml resolves it -----------------------------------------------------------
# `PYTHON` when set, else the first of python3 and python that runs: on Windows `python3` can be the Store stub.
PY=""
for candidate in ${PYTHON:+"$PYTHON"} python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 \
     && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$candidate"
    break
  fi
done
if [[ -z "$PY" ]]; then
  echo "ERROR: needs Python >= 3.10 on PATH (python3 or python), or PYTHON set to one." >&2
  exit 2
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
WORK_DIR="$(native_dir "$WORK_DIR")"

echo "==> collector-gh @ $COLLECTOR_GH_REF"
git clone --quiet --filter=blob:none "$COLLECTOR_GH_URL" "$WORK_DIR/collector-gh"
git -C "$WORK_DIR/collector-gh" checkout --quiet "$COLLECTOR_GH_REF"
REQUIREMENTS="$WORK_DIR/collector-gh/requirements.txt"

# --- The venv, shaped like the collector's action.yml -------------------------------------------------------------
# The install must land in the venv and nowhere else: these redirect pip's target or prepend to `sys.path`.
# Unset, not set empty: pip reads its own variables as configuration values.
unset PIP_TARGET PIP_PREFIX PIP_USER PYTHONPATH

venv_python() {
  if [[ -x "$VENV/bin/python" ]]; then
    echo "$VENV/bin/python"
  elif [[ -x "$VENV/Scripts/python.exe" ]]; then
    echo "$VENV/Scripts/python.exe"
  else
    return 1
  fi
}

# `base_prefix` identifies the interpreter a venv was created from; a requirement dropped from the pinned file
# would otherwise stay installed in a reused venv, and the run would hide the skew it should show.
IDENTITY='import sys; print(sys.base_prefix, sys.version_info[:3])'
WANT="$("$PY" -c "$IDENTITY")"
HAVE=""
if VPY="$(venv_python)" && cmp -s "$REQUIREMENTS" "$VENV/requirements.txt"; then
  HAVE="$("$VPY" -c "$IDENTITY" 2>/dev/null || true)"
fi
if [[ "$HAVE" != "$WANT" ]]; then
  echo "==> building the collector-gh venv ($("$PY" -c 'import platform; print(platform.python_version())'))"
  rm -rf "$VENV"
  "$PY" -m venv "$VENV"
  VPY="$(venv_python)"
  "$VPY" -m pip install --quiet --disable-pip-version-check -r "$REQUIREMENTS"
  # pip's own config files can still redirect the install while pip exits 0; one import through the venv's own
  # interpreter reports it here, where it happened.
  "$VPY" -E -c 'import living_doc_utilities, pydantic' || {
    echo "ERROR: the collector's requirements did not land in $VENV; check pip's configuration for a 'target' or 'prefix' setting." >&2
    exit 1
  }
  cp "$REQUIREMENTS" "$VENV/requirements.txt"
else
  echo "==> reusing the collector-gh venv at $VENV"
fi
echo "    living-doc-utilities $("$VPY" -E -c 'from importlib.metadata import version; print(version("living-doc-utilities"))' | tr -d '\r')"

# --- The run ------------------------------------------------------------------------------------------------------
# One mode's repository list for this checkout, from `<key>=<directory>` pairs.
repositories() {
  "$VPY" -E -c '
import json, sys
entry = {"organization-name": "AbsaOSS", "repository-name": "living-doc"}
for pair in sys.argv[1:]:
    key, _, directory = pair.partition("=")
    entry.setdefault(key, []).append(directory)
print(json.dumps([entry]))' "$@" | tr -d '\r'
}

OUTPUT_ROOT="$WORK_DIR/output"
echo "==> mining $CORPUS_DIR (project-id $PROJECT_ID)"
# `-E`, as action.yml runs it: the interpreter ignores the whole `PYTHON*` set. `GITHUB_OUTPUT` is where `main.py`
# writes its `output-path` output; a file of this run's own, so a CI step's output is never touched.
( cd "$WORK_DIR" && env \
    GITHUB_OUTPUT="$WORK_DIR/github-output.txt" \
    INPUT_PROJECT_ID="$PROJECT_ID" \
    INPUT_OUTPUT_PATH="$OUTPUT_ROOT" \
    INPUT_DOC_ISSUES="false" \
    INPUT_DOC_SOURCE="true" \
    INPUT_UI_TESTS="true" \
    INPUT_DOC_SOURCE_REPOSITORIES="$(repositories \
      "us-paths=$CORPUS_DIR/gherkin/liv_doc_us" \
      "func-paths=$CORPUS_DIR/gherkin/liv_doc_func" \
      "pages-paths=$CORPUS_DIR/pageobject")" \
    INPUT_UI_TESTS_REPOSITORIES="$(repositories "paths=$CORPUS_DIR/gherkin")" \
    "$VPY" -E -X utf8 "$WORK_DIR/collector-gh/main.py" )

echo "==> validating and asserting the collector stage"
"$VPY" -E -X utf8 "$REPO_ROOT/tools/check_collector_stage.py" "$OUTPUT_ROOT"

rm -rf "$OUT_DIR/collector-gh"
for mode in doc-source ui-tests; do
  mkdir -p "$OUT_DIR/collector-gh/$mode"
  "$VPY" -E -X utf8 "$REPO_ROOT/tools/normalize_snapshot.py" \
    < "$OUTPUT_ROOT/$mode/$mode.json" > "$OUT_DIR/collector-gh/$mode/$mode.json"
done

echo "==> wrote normalized snapshots to $OUT_DIR/collector-gh/"
