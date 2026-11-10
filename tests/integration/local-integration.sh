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
# Run the GitHub source-code chain for one project on this machine, each component through its own
# `local-integration.sh`, unchanged: living-doc-collector-gh (`doc-source`, `ui-tests`) once, then per view (`inner`,
# `release`) living-doc-toolkit's three commands and living-doc-generator-markdown's three documents. Everything goes
# into one output root; then the living-doc-utilities pin report over the clones that ran. A testbed run then judges
# its own output with CI's testbed checks, and exits 0 only when the chain, the pin report and every check pass: the
# release go/no-go. The configuration is tests/integration/.env.local (copy .env.local.example). See
# docs/_integration/README.md § Run a milestone target and § Release go/no-go.
#
#   tests/integration/local-integration.sh            # check, clone, run the chain, report the pins
#   tests/integration/local-integration.sh --check    # check, clone, run the collector's own --check; nothing else
#
# The runner clones each component and the testbed itself, into out/components/<repository>/ and out/testbed/
# (git-ignored), reuses those clones across runs, and writes the `.env.local` of those clones only: a developer's own
# checkouts are never read or written. The output root:
#
#   <OUT_DIR>/local-integration.log                    this runner's own lines: the resolved refs, each step
#   <OUT_DIR>/collector-gh/local-integration.log       the collector's log
#   <OUT_DIR>/collector-gh/{doc-source,ui-tests}/…
#   <OUT_DIR>/<view>/toolkit/local-integration.log     the toolkit's log, per view
#   <OUT_DIR>/<view>/toolkit/{normalize-docs,normalize-tests,coverage-matrix}/…
#   <OUT_DIR>/<view>/local-integration.log             the generator's log, beside the folder it clears as a whole
#   <OUT_DIR>/<view>/generator-markdown/<document type>.md, .run-report.json
#   <OUT_DIR>/pin-report.txt                           tests/examples/check_utilities_pins.py --strict over the clones
#
# A run first clears the paths the chain writes in the root, so the root holds one run's files even when the run stops
# midway; anything else there, such as a milestone's env.local, stays. The root may not lie inside the target's checkout
# or the runner's clones.
#
# No token. Runs in bash 3.2 or later: Linux, macOS, or Git Bash on Windows.

set -euo pipefail

ME="tests/integration/local-integration.sh"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
ENV_FILE="tests/integration/.env.local"
PINS_FILE="tests/collector/collector-pins.env"
# The runner's own clones. Never under OUT_DIR, which a milestone run may commit.
WORK="out"
GITHUB="https://github.com/AbsaOSS"
VIEWS="inner release"

# Every setting the configuration may hold; a line with any other key stops the run, reported by its number only.
KEYS="TARGET TESTBED_REF COLLECTOR_GH_REF TOOLKIT_REF GENERATOR_MARKDOWN_REF PROJECT_ID TARGET_CHECKOUT
ORGANIZATION_NAME REPOSITORY_NAME DOC_SOURCE_US_PATHS DOC_SOURCE_FUNC_PATHS DOC_SOURCE_PAGES_PATHS UI_TESTS_PATHS
GITHUB_SERVER_URL OUT_DIR PYTHON"
# The collector's target keys: TARGET=project takes them from the configuration, TARGET=testbed sets them itself.
PROJECT_KEYS="PROJECT_ID TARGET_CHECKOUT ORGANIZATION_NAME REPOSITORY_NAME DOC_SOURCE_US_PATHS DOC_SOURCE_FUNC_PATHS
DOC_SOURCE_PAGES_PATHS UI_TESTS_PATHS GITHUB_SERVER_URL"
PROJECT_REQUIRED="PROJECT_ID TARGET_CHECKOUT ORGANIZATION_NAME REPOSITORY_NAME DOC_SOURCE_US_PATHS UI_TESTS_PATHS"

# A run's failure also ends the output root's own log (LOG, set once the run starts writing), so the log says why.
die() {
  printf '%s: %s\n' "$ME" "$*" >&2
  [ -z "${LOG:-}" ] || printf '%s: %s\n' "$ME" "$*" >> "$LOG"
  exit 1
}
is_key() { local key; for key in $KEYS; do [ "$key" = "$1" ] && return 0; done; return 1; }

usage() {
  cat <<EOF
usage: $ME [--check]

Runs living-doc-collector-gh, then living-doc-toolkit and living-doc-generator-markdown in the inner and the release
view, over the target configured in $ENV_FILE (copy .env.local.example), into one output root, then reports the
living-doc-utilities pins of the clones that ran.

  --check   check Python, git, the configuration, the refs and the target, clone or update the components, then run
            the collector's own --check; build no venv, run nothing else
EOF
}

CHECK_ONLY=false
case "${1-}" in
  "") ;;
  --check) CHECK_ONLY=true ;;
  -h | --help) usage; exit 0 ;;
  *) die "unknown argument '$1'; usage: $ME [--check]" ;;
esac
[ $# -le 1 ] || die "too many arguments; usage: $ME [--check]"

cd "$REPO_ROOT"

# --- Configuration -------------------------------------------------------------------------------------------
# Read as data, never sourced, by the component scripts' rules: one KEY=value per line, `#` comments, no expansion.
for key in $KEYS; do printf -v "CFG_$key" '%s' ""; done
[ -f "$ENV_FILE" ] || die "$ENV_FILE not found; copy tests/integration/.env.local.example to it and set TARGET"
line_no=0
while IFS= read -r line || [ -n "$line" ]; do
  line_no=$((line_no + 1))
  line="${line%$'\r'}"
  line="${line#"${line%%[![:space:]]*}"}"
  case "$line" in "" | "#"*) continue ;; esac
  line="${line#export }"
  key="${line%%=*}"
  # A line is reported by its number only, never by its text: it may be a pasted secret.
  [[ "$line" == *=* && "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || die "$ENV_FILE:$line_no: not a KEY=value line"
  # Unlike a component script, the runner stops on an unknown key: a misspelt ref key would run the pin unnoticed.
  is_key "$key" || die "$ENV_FILE:$line_no: not a setting of this runner; see tests/integration/.env.local.example"
  value="${line#*=}"
  value="${value%"${value##*[![:space:]]}"}"
  case "$value" in
    \"*\") value="${value#\"}"; value="${value%\"}" ;;
    \'*\') value="${value#\'}"; value="${value%\'}" ;;
  esac
  printf -v "CFG_$key" '%s' "$value"
done < "$ENV_FILE"

case "$CFG_TARGET" in
  "") die "TARGET is not set in $ENV_FILE; set it to testbed or project" ;;
  testbed)
    for key in $PROJECT_KEYS; do
      var="CFG_$key"
      [ -z "${!var}" ] || die "$key is set in $ENV_FILE, but TARGET=testbed configures the testbed's core itself; empty it, or set TARGET=project"
    done
    ;;
  project)
    for key in $PROJECT_REQUIRED; do
      var="CFG_$key"
      [ -n "${!var}" ] || die "$key is not set in $ENV_FILE; TARGET=project needs it"
    done
    [ -z "$CFG_TESTBED_REF" ] || die "TESTBED_REF is set in $ENV_FILE, but TARGET=project reads TARGET_CHECKOUT; empty it"
    ;;
  *) die "TARGET '$CFG_TARGET' in $ENV_FILE is not testbed or project" ;;
esac

# A configured path: `~/` is the home directory, and a relative one resolves against this repository's root.
resolve() {
  case "$1" in
    "~/"*) printf '%s\n' "$HOME/${1#"~/"}" ;;
    /* | [A-Za-z]:[/\\]*) printf '%s\n' "$1" ;;
    *) printf '%s\n' "$REPO_ROOT/${1#./}" ;;
  esac
}

# --- Tools ---------------------------------------------------------------------------------------------------
# The interpreter: `PYTHON` when set, else `python3`, else `python` - the order each component resolves it in. The one
# found is passed to every component, so all three build their venvs from the same interpreter.
case "$CFG_PYTHON" in
  */*) PY="$(resolve "$CFG_PYTHON")" ;;
  ?*) PY="$CFG_PYTHON" ;;
  *) PY="$(command -v python3 || command -v python || true)" ;;
esac
[ -n "$PY" ] || die "needs Python >= 3.10, and neither python3 nor python is on PATH; set PYTHON in $ENV_FILE"
PY_VERSION="$("$PY" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null | tr -d '\r')" \
  || die "needs Python >= 3.10, and '$PY' does not run; set PYTHON in $ENV_FILE"
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
  || die "needs Python >= 3.10, and '$PY' is $PY_VERSION; set PYTHON in $ENV_FILE"
command -v git >/dev/null 2>&1 || die "git is not on PATH"

# --- Refs ----------------------------------------------------------------------------------------------------
pin_of() {  # pin_of KEY: its value in the pins file, read as data
  sed -n "s/^$1=//p" "$PINS_FILE" | tr -d '\r' | tail -n 1
}

# A ref MUST be immutable, as .github/workflows/retired-names.yml requires of a pin: a full 40-hex commit SHA, or a
# tag that exists on the remote. A branch name or a short SHA is refused.
check_ref() {  # check_ref KEY REF REPOSITORY
  local url="$GITHUB/$3"
  [[ "$2" =~ ^[0-9a-f]{40}$ ]] && return 0
  [ -n "$2" ] && git ls-remote --tags --exit-code "$url" "refs/tags/$2" >/dev/null 2>&1 && return 0
  die "$1 '$2' is neither a full 40-hex commit SHA nor a tag of $url"
}

ref_for() {  # ref_for KEY: the configured ref, else the pin
  local var="CFG_$1"
  if [ -n "${!var}" ]; then printf '%s\n' "${!var}"; else pin_of "$1"; fi
}
source_of() {  # source_of KEY: "pin" or "KEY=<ref>", for the header
  local var="CFG_$1"
  if [ -n "${!var}" ]; then printf '%s=%s\n' "$1" "${!var}"; else echo "pin"; fi
}
COLLECTOR_GH_REF="$(ref_for COLLECTOR_GH_REF)"
TOOLKIT_REF="$(ref_for TOOLKIT_REF)"
GENERATOR_MARKDOWN_REF="$(ref_for GENERATOR_MARKDOWN_REF)"
check_ref COLLECTOR_GH_REF "$COLLECTOR_GH_REF" living-doc-collector-gh
check_ref TOOLKIT_REF "$TOOLKIT_REF" living-doc-toolkit
check_ref GENERATOR_MARKDOWN_REF "$GENERATOR_MARKDOWN_REF" living-doc-generator-markdown
# The testbed is read at `master` unless TESTBED_REF names a tag or a full SHA.
[ -z "$CFG_TESTBED_REF" ] || [ "$CFG_TARGET" != testbed ] || check_ref TESTBED_REF "$CFG_TESTBED_REF" living-doc-testbed

# --- The output root -----------------------------------------------------------------------------------------
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$(resolve "${CFG_OUT_DIR:-$WORK/$RUN_ID}")"
[ ! -e "$OUT" ] || [ -d "$OUT" ] || die "OUT_DIR is not a directory: $OUT"

# A path's physical form, for comparing paths: symlinks resolved for the part that exists, the rest as written.
physical() {  # physical PATH
  local path="$1" rest=""
  while [ ! -d "$path" ]; do
    rest="/$(basename "$path")$rest"
    path="$(dirname "$path")"
  done
  printf '%s%s\n' "$(cd "$path" && pwd -P)" "$rest"
}
# The output root lies outside every tree the run reads or the runner owns: inside one, the chain would write into the
# checkout it mines, or the next `git clean` of a clone would delete the output.
outside() {  # outside TREE NAME
  case "$(physical "$OUT")/" in
    "$(physical "$1")"/*) die "OUT_DIR $OUT is inside $2 ($1); set an output root outside it" ;;
  esac
}
outside "$REPO_ROOT/$WORK/testbed" "the runner's testbed clone"
outside "$REPO_ROOT/$WORK/components" "the runner's component clones"
[ "$CFG_TARGET" != project ] || outside "$(resolve "$CFG_TARGET_CHECKOUT")" "TARGET_CHECKOUT"

# --- Clones --------------------------------------------------------------------------------------------------
# A blob-less clone of AbsaOSS/<repository> in DIR, made once and fetched on every later run, then checked out at the
# ref (a tag, a full SHA, or the testbed's default, origin/master). The clone is the runner's own folder under out/,
# never another checkout: a link at DIR or at its `.git` is removed (the link, not what it points to) and a folder whose
# origin is another repository deleted, and either is cloned again; a link below out/ above DIR, such as out/components/
# pointing at a folder of checkouts, stops the run. After the checkout, a change made in the clone is discarded and an
# untracked file removed, so a run reads the ref's files only. CLEAN is `git clean`'s flags: `-ffd` keeps the files the
# clone's `.gitignore` ignores (a component's `.env.local` and `.venv-local-integration/`); `-ffdx` (the testbed)
# removes those too.
checkout_at() {  # checkout_at REPOSITORY REF DIR CLEAN
  local url="$GITHUB/$1" ref="$2" dir="$3" clean="$4"
  if [ -L "$dir" ] || [ -L "$dir/.git" ]; then
    rm -rf "$dir"
  fi
  [ "$(physical "$dir")" = "$(physical "$REPO_ROOT/$WORK")/${dir#"$REPO_ROOT/$WORK/"}" ] \
    || die "$dir is reached through a link to $(physical "$dir"); the runner keeps its own clones under $WORK/, so remove the link"
  if [ -d "$dir/.git" ] && [ "$(git -C "$dir" remote get-url origin 2>/dev/null | tr -d '\r')" != "$url" ]; then
    rm -rf "$dir"
  fi
  if [ -d "$dir/.git" ]; then
    git -C "$dir" fetch --quiet --force --tags origin || die "could not fetch $url into $dir"
  else
    rm -rf "$dir"
    mkdir -p "$(dirname "$dir")"
    git clone --quiet --filter=blob:none "$url" "$dir" || die "could not clone $url into $dir"
  fi
  git -C "$dir" -c advice.detachedHead=false checkout --quiet --force --detach "$ref" \
    || die "$1: '$ref' is not a commit of $url"
  git -C "$dir" clean -q "$clean" || die "could not clean $dir"
}

# commit_of DIR [UNTRACKED]: its HEAD, marked when its files differ from it. UNTRACKED is git status's
# --untracked-files: `no` (the default, as the component scripts check) for living-doc and the clones; `normal` for the
# target, whose untracked files the collector mines like any other.
commit_of() {
  local sha
  sha="$(git -C "$1" rev-parse HEAD 2>/dev/null)" || { echo "unknown (not a git checkout)"; return 0; }
  if [ -n "$(git -C "$1" status --porcelain --untracked-files="${2:-no}" 2>/dev/null)" ]; then
    sha="$sha (uncommitted changes)"
  fi
  printf '%s\n' "$sha"
}

COLLECTOR="$REPO_ROOT/$WORK/components/living-doc-collector-gh"
TOOLKIT="$REPO_ROOT/$WORK/components/living-doc-toolkit"
GENERATOR="$REPO_ROOT/$WORK/components/living-doc-generator-markdown"

# The target, as the collector's settings. The testbed's are tests/testbed/run-testbed-stage.sh's (`core`, its User
# Story, Functionality and PageObject folders, and the whole test tree for `ui-tests`); change both together.
if [ "$CFG_TARGET" = testbed ]; then
  TESTBED="$REPO_ROOT/$WORK/testbed"
  checkout_at living-doc-testbed "${CFG_TESTBED_REF:-origin/master}" "$TESTBED" -ffdx
  CFG_PROJECT_ID="testbed-core"
  CFG_TARGET_CHECKOUT="$TESTBED"
  CFG_ORGANIZATION_NAME="AbsaOSS"
  CFG_REPOSITORY_NAME="living-doc-testbed"
  CFG_DOC_SOURCE_US_PATHS="projects/core/tests/e2e/features/liv_doc_us"
  CFG_DOC_SOURCE_FUNC_PATHS="projects/core/tests/e2e/features/liv_doc_func"
  CFG_DOC_SOURCE_PAGES_PATHS="projects/core/tests/e2e/pages"
  CFG_UI_TESTS_PATHS="projects/core/tests/e2e/features"
  TARGET_LINE="testbed-core: AbsaOSS/living-doc-testbed $(commit_of "$TESTBED" normal) (${CFG_TESTBED_REF:-master})"
else
  CFG_TARGET_CHECKOUT="$(resolve "$CFG_TARGET_CHECKOUT")"
  [ -d "$CFG_TARGET_CHECKOUT" ] || die "TARGET_CHECKOUT not found: $CFG_TARGET_CHECKOUT"
  git -C "$CFG_TARGET_CHECKOUT" rev-parse --verify --quiet HEAD >/dev/null \
    || die "TARGET_CHECKOUT is not a git checkout: $CFG_TARGET_CHECKOUT"
  TARGET_LINE="$CFG_PROJECT_ID: $(commit_of "$CFG_TARGET_CHECKOUT" normal) ($CFG_TARGET_CHECKOUT)"
fi

checkout_at living-doc-collector-gh "$COLLECTOR_GH_REF" "$COLLECTOR" -ffd
checkout_at living-doc-toolkit "$TOOLKIT_REF" "$TOOLKIT" -ffd
checkout_at living-doc-generator-markdown "$GENERATOR_MARKDOWN_REF" "$GENERATOR" -ffd

# --- Every resolved ref, before the first component runs ----------------------------------------------------------
# Printed, and in a run also written to the output root's own log, which `docs/_integration/.gitignore` ignores by
# name: it holds this machine's paths.
LOG=""
say() {
  printf '%s\n' "$@"
  [ -z "$LOG" ] || printf '%s\n' "$@" >> "$LOG"
}
if [ "$CHECK_ONLY" = false ]; then
  mkdir -p "$OUT"
  # The root holds this run's files and nothing older: a run that stops midway would otherwise leave an earlier run's
  # later outputs beside its own. Only the paths the chain writes are cleared; anything else there, such as a
  # milestone's committed env.local, stays.
  rm -rf "$OUT/collector-gh/doc-source" "$OUT/collector-gh/ui-tests" "$OUT/collector-gh/local-integration.log" \
    "$OUT/pin-report.txt"
  for view in $VIEWS; do
    rm -rf "$OUT/$view/toolkit/normalize-docs" "$OUT/$view/toolkit/normalize-tests" \
      "$OUT/$view/toolkit/coverage-matrix" "$OUT/$view/toolkit/local-integration.log" \
      "$OUT/$view/generator-markdown" "$OUT/$view/local-integration.log"
  done
  LOG="$OUT/local-integration.log"
  : > "$LOG"
fi
say "== $ME" \
  "run id:              $RUN_ID" \
  "living-doc:          $(commit_of "$REPO_ROOT")" \
  "collector-gh:        $(commit_of "$COLLECTOR") ($(source_of COLLECTOR_GH_REF))" \
  "toolkit:             $(commit_of "$TOOLKIT") ($(source_of TOOLKIT_REF))" \
  "generator-markdown:  $(commit_of "$GENERATOR") ($(source_of GENERATOR_MARKDOWN_REF))" \
  "target:              $TARGET_LINE" \
  "python:              $PY_VERSION ($PY)" \
  "output:              $OUT"

# --- The components' configurations ------------------------------------------------------------------------------
# Each is written into the runner's clone only, as data the component reads; every path is absolute.
write_env() {  # write_env CLONE KEY=value...
  local clone="$1"
  shift
  {
    echo "# Written by living-doc $ME, run $RUN_ID; rewritten by every run."
    printf '%s\n' "$@"
  } > "$clone/.env.local"
}

write_env "$COLLECTOR" \
  "PROJECT_ID=$CFG_PROJECT_ID" \
  "TARGET_CHECKOUT=$CFG_TARGET_CHECKOUT" \
  "ORGANIZATION_NAME=$CFG_ORGANIZATION_NAME" \
  "REPOSITORY_NAME=$CFG_REPOSITORY_NAME" \
  "DOC_SOURCE_US_PATHS=$CFG_DOC_SOURCE_US_PATHS" \
  "DOC_SOURCE_FUNC_PATHS=$CFG_DOC_SOURCE_FUNC_PATHS" \
  "DOC_SOURCE_PAGES_PATHS=$CFG_DOC_SOURCE_PAGES_PATHS" \
  "UI_TESTS_PATHS=$CFG_UI_TESTS_PATHS" \
  "GITHUB_SERVER_URL=$CFG_GITHUB_SERVER_URL" \
  "OUT_DIR=$OUT" \
  "PYTHON=$PY"

if [ "$CHECK_ONLY" = true ]; then
  # The toolkit's and the generator's own --check need their input files, which only a run writes: each runs right
  # before its component's run in the chain.
  say "" "== collector-gh --check"
  (cd "$COLLECTOR" && ./local-integration.sh --check) || die "the collector's --check failed; its output is above"
  say "" "$ME: check passed; the toolkit's and the generator's own --check run in the chain, once their inputs exist"
  exit 0
fi

# --- The chain -----------------------------------------------------------------------------------------------
# One component's --check, then its run, in its clone, teed into LOG. The first that fails stops the chain.
component() {  # component STEP CLONE LOG
  say "" "== $1"
  mkdir -p "$(dirname "$3")"
  (cd "$2" && ./local-integration.sh --check && ./local-integration.sh) 2>&1 | tee "$3" \
    || die "$1 failed; its log: $3"
}

component "collector-gh: doc-source, ui-tests" "$COLLECTOR" "$OUT/collector-gh/local-integration.log"
for view in $VIEWS; do
  write_env "$TOOLKIT" \
    "DOC_INPUT=$OUT/collector-gh/doc-source/doc-source.json" \
    "TESTS_INPUT=$OUT/collector-gh/ui-tests/ui-tests.json" \
    "VIEW=$view" \
    "OUT_DIR=$OUT/$view" \
    "PYTHON=$PY"
  component "toolkit, $view view" "$TOOLKIT" "$OUT/$view/toolkit/local-integration.log"
  write_env "$GENERATOR" \
    "TECHNICAL_PROJECT_INPUT=$OUT/$view/toolkit/normalize-docs/generator-ready.json" \
    "UI_TEST_CATALOG_INPUT=$OUT/$view/toolkit/normalize-tests/ui-test-catalog.json" \
    "COVERAGE_MATRIX_INPUT=$OUT/$view/toolkit/coverage-matrix/coverage-matrix.json" \
    "OUT_DIR=$OUT/$view" \
    "PYTHON=$PY"
  # generator-markdown clears `<view>/generator-markdown/` as a whole, so its log goes beside that folder.
  component "generator-markdown, $view view" "$GENERATOR" "$OUT/$view/local-integration.log"
done

# --- The living-doc-utilities pins of the clones that ran ----------------------------------------------------------
# Paths relative to this repository's root, so the report names no machine path.
say "" "== living-doc-utilities pins"
"$PY" tests/examples/check_utilities_pins.py --strict \
  --requirements "collector-gh=$WORK/components/living-doc-collector-gh/requirements.txt" \
  --requirements "toolkit=$WORK/components/living-doc-toolkit/requirements.txt" \
  --requirements "generator-markdown=$WORK/components/living-doc-generator-markdown/requirements.txt" \
  2>&1 | tr -d '\r' | tee "$OUT/pin-report.txt" || die "the pin report failed; see $OUT/pin-report.txt"

# A project's warnings belong to its authors: a project run is not judged.
if [ "$CFG_TARGET" = project ]; then
  say "" "$ME: the chain passed: the six documents are under $OUT/{inner,release}/generator-markdown"
  exit 0
fi

# --- The verdict over the testbed's output -------------------------------------------------------------------------
# `core` follows the canon 100 %, so any warning or broken invariant over it is a defect. The run checks its own output
# with CI's testbed checks in tests/testbed/, each in the venv its component's script built, as the testbed stage runs
# each in its component's venv. The first check that fails stops the run; its last line names it.
venv_python() {  # venv_python CLONE: the interpreter of the venv the clone's local-integration.sh built
  if [ -x "$1/.venv-local-integration/bin/python" ]; then
    printf '%s\n' "$1/.venv-local-integration/bin/python"
  elif [ -x "$1/.venv-local-integration/Scripts/python.exe" ]; then
    printf '%s\n' "$1/.venv-local-integration/Scripts/python.exe"
  else
    die "$1 has no .venv-local-integration/, which its local-integration.sh builds on a run"
  fi
}
check() {  # check STEP PYTHON SCRIPT ARG...: one check, its output printed and in LOG
  local step="$1" python="$2"
  shift 2
  say "" "== check: $step"
  "$python" -E -X utf8 "$@" 2>&1 | tr -d '\r' | tee -a "$LOG" || die "$step failed; its output is above"
}
COLLECTOR_PY="$(venv_python "$COLLECTOR")" || exit 1
TOOLKIT_PY="$(venv_python "$TOOLKIT")" || exit 1

check "the collector's invariants over core" "$COLLECTOR_PY" tests/testbed/check_testbed_stage.py core \
  "$OUT/collector-gh" "$TESTBED" --us "$CFG_DOC_SOURCE_US_PATHS" --func "$CFG_DOC_SOURCE_FUNC_PATHS" \
  --pages "$CFG_DOC_SOURCE_PAGES_PATHS" --scenarios "$CFG_UI_TESTS_PATHS"
check "the toolkit's invariants over both views" "$TOOLKIT_PY" tests/testbed/check_testbed_toolkit_stage.py --runner \
  "$OUT" "$OUT/collector-gh/doc-source/doc-source.json" "$OUT/collector-gh/ui-tests/ui-tests.json"

say "" "== check: the six documents and their run reports"
missing=""
for view in $VIEWS; do
  for document in technical-project ui-test-catalog coverage-matrix; do
    for file in "$document.md" "$document.run-report.json"; do
      [ -f "$OUT/$view/generator-markdown/$file" ] || missing="$missing $view/generator-markdown/$file"
    done
  done
done
[ -z "$missing" ] || die "the six documents and their run reports failed; missing under $OUT:$missing"
say "  OK: each view's technical-project, ui-test-catalog and coverage-matrix, each with its run report"

say "" "$ME: the chain and the testbed's invariants passed: the six documents are under $OUT/{inner,release}/generator-markdown"
