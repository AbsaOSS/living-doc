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
# Sourced, never run: the ONE definition of the pinned living-doc-toolkit, the venv it runs in and how it is run.
# tests/examples/regen-collector-snapshots.sh (over docs/examples/) and tests/testbed/run-testbed-stage.sh (over
# the testbed's `core`) both source it, after tests/collector/collector-gh.sh, whose `native_dir` and
# `_collector_gh_venv_python` it uses.
#
# The caller sets `set -euo pipefail`, REPO_ROOT and WORK_DIR (native paths, see `native_dir`), then calls:
#   toolkit_setup                                         clone the pinned toolkit into $WORK_DIR/toolkit and build or
#                                                         reuse its venv; sets TOOLKIT_PY, the venv's interpreter
#   toolkit_run <command> <output> <INPUT_NAME=value>...  one command, as the toolkit's action runs it
#   toolkit_chain <doc-source> <ui-tests> <output-root>   every command over one collector run's two artifacts:
#                                                         <output-root>/gh-headers/{generator-ready.inner,
#                                                         generator-ready.release,coverage-matrix}.json and
#                                                         <output-root>/tests/ui-test-catalog.json
#
# The pinned ref comes from tests/collector/collector-pins.env (the one place to bump it). The venv is built from the
# toolkit's runtime requirements.txt at that ref and nothing else, so living-doc-utilities arrives only through that
# file: a skew between what the toolkit ships and what a stage assumes fails there, as it would in a real pipeline.
#
# Environment (optional):
#   PYTHON      the interpreter the venv is built from (default: python3, else python - the first that runs)
#
# Runs in bash 3.2 or later: Linux, macOS, or Git Bash on Windows.

TOOLKIT_URL="https://github.com/AbsaOSS/living-doc-toolkit"

toolkit_setup() {
  # Drop every inherited action input, so a run sees exactly the inputs `toolkit_run` is given.
  local name
  for name in $(compgen -e); do
    case "$name" in INPUT_*) unset "$name" ;; esac
  done

  # shellcheck source=tests/collector/collector-pins.env
  source "$REPO_ROOT/tests/collector/collector-pins.env"

  # The pin MUST be an immutable ref: a full 40-hex commit SHA, or a tag that exists on the remote.
  # Anything else (a branch name, a short SHA, a typo) is rejected so every run stays reproducible.
  if ! [[ "${TOOLKIT_REF:-}" =~ ^[0-9a-f]{40}$ ]] \
     && ! { [[ -n "${TOOLKIT_REF:-}" ]] && git ls-remote --tags --exit-code "$TOOLKIT_URL" \
            "refs/tags/$TOOLKIT_REF" >/dev/null 2>&1; }; then
    echo "ERROR: TOOLKIT_REF='${TOOLKIT_REF:-}' must be a full 40-hex commit SHA or an existing tag of $TOOLKIT_URL." >&2
    exit 2
  fi

  # --- Python, as the toolkit's action.yml resolves it -------------------------------------------------------------
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

  echo "==> toolkit @ $TOOLKIT_REF"
  git clone --quiet --filter=blob:none "$TOOLKIT_URL" "$WORK_DIR/toolkit"
  git -C "$WORK_DIR/toolkit" checkout --quiet "$TOOLKIT_REF"

  # --- The venv, shaped like the toolkit's action.yml --------------------------------------------------------------
  # The toolkit's venv, reused only when the interpreter now resolved built it at the ref now pinned. Its
  # requirements.txt cannot be the key: the packages are installed by path, each at one version, so a new ref with the
  # same file would keep the old code.
  local venv="$REPO_ROOT/.snapshot-venvs/toolkit"
  local ref_file="$venv/toolkit-ref.txt"
  # The install must land in the venv and nowhere else: these redirect pip's target or prepend to `sys.path`.
  # Unset, not set empty: pip reads its own variables as configuration values.
  unset PIP_TARGET PIP_PREFIX PIP_USER PIP_ROOT PIP_PYTHON PYTHONPATH

  # `base_prefix` identifies the interpreter a venv was created from.
  local identity='import sys; print(sys.base_prefix, sys.version_info[:3])'
  local want have=""
  want="$("$py" -c "$identity")"
  if TOOLKIT_PY="$(_collector_gh_venv_python "$venv")" && [[ "$(cat "$ref_file" 2>/dev/null)" == "$TOOLKIT_REF" ]]; then
    have="$("$TOOLKIT_PY" -c "$identity" 2>/dev/null || true)"
  fi
  if [[ "$have" != "$want" ]]; then
    echo "==> building the toolkit venv ($("$py" -c 'import platform; print(platform.python_version())'))"
    rm -rf "$venv"
    "$py" -m venv "$venv"
    TOOLKIT_PY="$(_collector_gh_venv_python "$venv")"
    # From the checkout's root: the file's `./packages/...` and `./apps/cli` lines are relative to it.
    ( cd "$WORK_DIR/toolkit" && "$TOOLKIT_PY" -m pip install --quiet --disable-pip-version-check -r requirements.txt )
    # pip's own config files can still redirect the install while pip exits 0; one import through the venv's own
    # interpreter reports it here, where it happened.
    "$TOOLKIT_PY" -E -c 'import living_doc_cli.main' || {
      echo "ERROR: the toolkit's requirements did not land in $venv; check pip's configuration for a 'target' or 'prefix' setting." >&2
      exit 1
    }
    echo "$TOOLKIT_REF" > "$ref_file"
  else
    echo "==> reusing the toolkit venv at $venv"
  fi
  echo "    living-doc-utilities $("$TOOLKIT_PY" -E -c 'from importlib.metadata import version; print(version("living-doc-utilities"))' | tr -d '\r')"
}

toolkit_run() {
  local command="$1" output="$2"
  shift 2
  # `-E`, as action.yml runs it: the interpreter ignores the whole `PYTHON*` set. `GITHUB_OUTPUT` is where `main.py`
  # writes its `output-path` output; a file of this run's own, so a CI step's output is never touched.
  ( cd "$WORK_DIR" && env \
      GITHUB_OUTPUT="$WORK_DIR/toolkit-github-output.txt" \
      INPUT_COMMAND="$command" \
      INPUT_OUTPUT="$output" \
      "$@" \
      "$TOOLKIT_PY" -E -X utf8 "$WORK_DIR/toolkit/main.py" )
}

# `&&`, not one line each: a caller may test this function's status, and `set -e` does not apply inside such a call.
toolkit_chain() {
  local doc_source="$1" ui_tests="$2" output_root="$3"
  toolkit_run normalize-docs "$output_root/gh-headers/generator-ready.inner.json" \
      INPUT_INPUT="$doc_source" INPUT_VIEW=inner \
    && toolkit_run normalize-docs "$output_root/gh-headers/generator-ready.release.json" \
      INPUT_INPUT="$doc_source" INPUT_VIEW=release \
    && toolkit_run coverage-matrix "$output_root/gh-headers/coverage-matrix.json" \
      INPUT_INPUT="$doc_source" INPUT_TESTS_INPUT="$ui_tests" \
    && toolkit_run normalize-tests "$output_root/tests/ui-test-catalog.json" \
      INPUT_INPUT="$ui_tests"
}
