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
# Sourced, never run: the ONE definition of the pinned living-doc-collector-gh, the venv it runs in and how it is
# run. tools/regen-collector-snapshots.sh (over docs/examples/) and tools/run-testbed-stage.sh (over the testbed's
# `core`) both source it, so the two stages always run the same collector in the same venv.
#
# The caller sets `set -euo pipefail`, REPO_ROOT and WORK_DIR (native paths, see `native_dir`), then calls:
#   collector_gh_setup                                    clone the pinned collector into $WORK_DIR/collector-gh and
#                                                         build or reuse its venv; sets VPY, the venv's interpreter
#   collector_gh_repositories <org> <repo> <key>=<dir>... one mode's repository list, as the collector reads it
#   collector_gh_run <project-id> <output-root> <doc-source-repositories> [<ui-tests-repositories>]
#                                                         one run; a mode with no repository list is disabled
#
# The pinned ref comes from tools/collector-snapshot-pins.env (the one place to bump it). No token: neither mode
# reads a credential. The venv is built from the collector's runtime requirements.txt at that ref and nothing else,
# so living-doc-utilities arrives only through that file: a skew between what the collector ships and what a stage
# assumes fails there, as it would in a real pipeline.
#
# Environment (optional):
#   PYTHON      the interpreter the venv is built from (default: python3, else python - the first that runs)
#
# Runs in bash 3.2 or later: Linux, macOS, or Git Bash on Windows.

# `pwd -W` (a Git-for-Windows builtin) yields a native C:/... path the venv's Python can read;
# it errors on Linux, where plain `pwd` is already correct.
native_dir() { (cd "$1" && { pwd -W 2>/dev/null || pwd; }); }

COLLECTOR_GH_URL="https://github.com/AbsaOSS/living-doc-collector-gh"

collector_gh_setup() {
  # No mode reads a credential. Drop the token names a shell may still carry from collector versions that needed
  # one, and every inherited action input, so a run sees exactly the inputs `collector_gh_run` sets.
  unset GITHUB_TOKEN GH_TOKEN GH_ENTERPRISE_TOKEN GITHUB_ENTERPRISE_TOKEN
  local name
  for name in $(compgen -e); do
    case "$name" in INPUT_*) unset "$name" ;; esac
  done

  # shellcheck source=tools/collector-snapshot-pins.env
  source "$REPO_ROOT/tools/collector-snapshot-pins.env"

  # The pin MUST be an immutable ref: a full 40-hex commit SHA, or a tag that exists on the remote.
  # Anything else (a branch name, a short SHA, a typo) is rejected so every run stays reproducible.
  if ! [[ "${COLLECTOR_GH_REF:-}" =~ ^[0-9a-f]{40}$ ]] \
     && ! { [[ -n "${COLLECTOR_GH_REF:-}" ]] && git ls-remote --tags --exit-code "$COLLECTOR_GH_URL" \
            "refs/tags/$COLLECTOR_GH_REF" >/dev/null 2>&1; }; then
    echo "ERROR: COLLECTOR_GH_REF='${COLLECTOR_GH_REF:-}' must be a full 40-hex commit SHA or an existing tag of $COLLECTOR_GH_URL." >&2
    exit 2
  fi

  # --- Python, as the collector's action.yml resolves it ---------------------------------------------------------
  # `PYTHON` when set, else the first of python3 and python that runs: on Windows `python3` can be the Store stub.
  local py="" candidate
  for candidate in ${PYTHON:+"$PYTHON"} python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 \
       && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      py="$candidate"
      break
    fi
  done
  if [[ -z "$py" ]]; then
    echo "ERROR: needs Python >= 3.10 on PATH (python3 or python), or PYTHON set to one." >&2
    exit 2
  fi

  echo "==> collector-gh @ $COLLECTOR_GH_REF"
  git clone --quiet --filter=blob:none "$COLLECTOR_GH_URL" "$WORK_DIR/collector-gh"
  git -C "$WORK_DIR/collector-gh" checkout --quiet "$COLLECTOR_GH_REF"
  local requirements="$WORK_DIR/collector-gh/requirements.txt"

  # --- The venv, shaped like the collector's action.yml -----------------------------------------------------------
  # The collector's venv, reused only when the interpreter now resolved built it from the requirements.txt now pinned.
  local venv="$REPO_ROOT/.snapshot-venvs/collector-gh"
  # The install must land in the venv and nowhere else: these redirect pip's target or prepend to `sys.path`.
  # Unset, not set empty: pip reads its own variables as configuration values.
  unset PIP_TARGET PIP_PREFIX PIP_USER PYTHONPATH

  # `base_prefix` identifies the interpreter a venv was created from; a requirement dropped from the pinned file
  # would otherwise stay installed in a reused venv, and the run would hide the skew it should show.
  local identity='import sys; print(sys.base_prefix, sys.version_info[:3])'
  local want have=""
  want="$("$py" -c "$identity")"
  if VPY="$(_collector_gh_venv_python "$venv")" && cmp -s "$requirements" "$venv/requirements.txt"; then
    have="$("$VPY" -c "$identity" 2>/dev/null || true)"
  fi
  if [[ "$have" != "$want" ]]; then
    echo "==> building the collector-gh venv ($("$py" -c 'import platform; print(platform.python_version())'))"
    rm -rf "$venv"
    "$py" -m venv "$venv"
    VPY="$(_collector_gh_venv_python "$venv")"
    "$VPY" -m pip install --quiet --disable-pip-version-check -r "$requirements"
    # pip's own config files can still redirect the install while pip exits 0; one import through the venv's own
    # interpreter reports it here, where it happened.
    "$VPY" -E -c 'import living_doc_utilities, pydantic' || {
      echo "ERROR: the collector's requirements did not land in $venv; check pip's configuration for a 'target' or 'prefix' setting." >&2
      exit 1
    }
    cp "$requirements" "$venv/requirements.txt"
  else
    echo "==> reusing the collector-gh venv at $venv"
  fi
  echo "    living-doc-utilities $("$VPY" -E -c 'from importlib.metadata import version; print(version("living-doc-utilities"))' | tr -d '\r')"
}

_collector_gh_venv_python() {
  if [[ -x "$1/bin/python" ]]; then
    echo "$1/bin/python"
  elif [[ -x "$1/Scripts/python.exe" ]]; then
    echo "$1/Scripts/python.exe"
  else
    return 1
  fi
}

# One mode's repository list for one repository, from `<key>=<directory>` pairs.
collector_gh_repositories() {
  "$VPY" -E -c '
import json, sys
entry = {"organization-name": sys.argv[1], "repository-name": sys.argv[2]}
for pair in sys.argv[3:]:
    key, _, directory = pair.partition("=")
    entry.setdefault(key, []).append(directory)
print(json.dumps([entry]))' "$@" | tr -d '\r'
}

collector_gh_run() {
  local project_id="$1" output_root="$2" doc_source="$3" ui_tests="${4:-}"
  # `-E`, as action.yml runs it: the interpreter ignores the whole `PYTHON*` set. `GITHUB_OUTPUT` is where `main.py`
  # writes its `output-path` output; a file of this run's own, so a CI step's output is never touched.
  ( cd "$WORK_DIR" && env \
      GITHUB_OUTPUT="$WORK_DIR/github-output.txt" \
      INPUT_PROJECT_ID="$project_id" \
      INPUT_OUTPUT_PATH="$output_root" \
      INPUT_DOC_ISSUES="false" \
      INPUT_DOC_SOURCE="$([[ -n "$doc_source" ]] && echo true || echo false)" \
      INPUT_UI_TESTS="$([[ -n "$ui_tests" ]] && echo true || echo false)" \
      INPUT_DOC_SOURCE_REPOSITORIES="$doc_source" \
      INPUT_UI_TESTS_REPOSITORIES="$ui_tests" \
      "$VPY" -E -X utf8 "$WORK_DIR/collector-gh/main.py" )
}
