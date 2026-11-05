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
"""Tests for tests/integration/local-integration.sh: the configurations it refuses before any clone, and the chain.

Run: ``python -m pytest tests/integration -q`` (needs pytest and bash). Each case copies the runner, the pins and the
pin report into ``tmp_path``, writes a configuration there, and runs the runner with a fake ``git`` first on ``PATH``.
For the refusals, that ``git`` answers every ``ls-remote`` with "no such tag" and fails any other command, so a clone
would show in its log. For the chain, its ``clone`` makes a folder holding a stand-in ``local-integration.sh``, which
records each call and its ``.env.local``, writes the files the real script writes, and fails where ``FAIL_AT`` says.
Nothing goes online.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
RUNNER = HERE / "local-integration.sh"
PINS = REPO_ROOT / "tests" / "collector" / "collector-pins.env"
PIN_REPORT = REPO_ROOT / "tests" / "examples" / "check_utilities_pins.py"
CHECKER_REQUIREMENTS = REPO_ROOT / "tests" / "examples" / "requirements-examples-check.txt"
TESTBED_STAGE = REPO_ROOT / "tests" / "testbed" / "run-testbed-stage.sh"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="needs bash")

# A complete TARGET=project configuration; each case drops or changes one line.
PROJECT = {
    "TARGET": "project",
    "PROJECT_ID": "absa-1",
    "TARGET_CHECKOUT": "../some-checkout",
    "ORGANIZATION_NAME": "some-org",
    "REPOSITORY_NAME": "some-repo",
    "DOC_SOURCE_US_PATHS": "features/us",
    "UI_TESTS_PATHS": "features",
}

FAKE_GIT = """#!/bin/sh
echo "$*" >> "{calls}"
case "$1" in
  ls-remote) exit 2 ;;
esac
echo "git $1: not available in this test" >&2
exit 1
"""

# The chain's `git`: a clone is a folder holding a stand-in component script, its origin kept in `.git/origin-url`;
# `ls-remote` knows one tag, `{tag}`; `status` lists a file named `untracked.feature` unless untracked files are off.
CHAIN_GIT = """#!/bin/sh
echo "$*" >> "{calls}"
dir=.
while :; do
  case "$1" in
    -C) dir="$2"; shift 2 ;;
    -c) shift 2 ;;
    *) break ;;
  esac
done
command="$1"
shift
url=""
previous=""
last=""
for last in "$@"; do url="$previous"; previous="$last"; done
case "$command" in
  ls-remote) [ "$last" = "refs/tags/{tag}" ] && exit 0; exit 2 ;;
  clone)
    mkdir -p "$last/.git"
    echo "$url" > "$last/.git/origin-url"
    cp "{stub}" "$last/local-integration.sh"
    chmod +x "$last/local-integration.sh"
    cp "{requirements}" "$last/requirements.txt"
    exit 0 ;;
  remote) cat "$dir/.git/origin-url"; exit 0 ;;
  status)
    case " $* " in *" --untracked-files=no "*) exit 0 ;; esac
    [ -f "$dir/untracked.feature" ] && echo "?? untracked.feature"
    exit 0 ;;
  fetch | checkout | clean) exit 0 ;;
  rev-parse) echo {sha}; exit 0 ;;
esac
echo "git $command: not available in this test" >&2
exit 1
"""

# A component's `local-integration.sh`, standing in: records the call and its `.env.local` under `{record}`, writes
# the files the real one writes under its OUT_DIR, and fails its run where FAIL_AT names `<clone>:<OUT_DIR's name>`.
STUB_COMPONENT = """#!/bin/sh
component=$(basename "$(pwd)")
out=$(sed -n 's/^OUT_DIR=//p' .env.local)
step="$component:$(basename "$out")"
echo "$component ${{1:-run}} $(basename "$out")" >> "{record}/calls.txt"
cp .env.local "{record}/$component.$(basename "$out").env"
[ "${{1:-}}" = --check ] && exit 0
if [ "${{FAIL_AT:-}}" = "$step" ]; then echo "stub: $step fails"; exit 3; fi
case "$component" in
  living-doc-collector-gh)
    mkdir -p "$out/collector-gh/doc-source" "$out/collector-gh/ui-tests"
    echo "{{}}" > "$out/collector-gh/doc-source/doc-source.json"
    echo "{{}}" > "$out/collector-gh/ui-tests/ui-tests.json" ;;
  living-doc-toolkit)
    for file in normalize-docs/generator-ready normalize-tests/ui-test-catalog coverage-matrix/coverage-matrix; do
      mkdir -p "$out/toolkit/${{file%/*}}"
      echo "{{}}" > "$out/toolkit/$file.json"
    done ;;
  living-doc-generator-markdown)
    rm -rf "$out/generator-markdown"
    mkdir -p "$out/generator-markdown"
    for document in technical-project ui-test-catalog coverage-matrix; do
      echo "# $document" > "$out/generator-markdown/$document.md"
    done ;;
esac
echo "stub: $step done"
"""

SHA = "0123456789abcdef0123456789abcdef01234567"
TAG = "v9.9.9"
COMPONENTS = ("living-doc-collector-gh", "living-doc-toolkit", "living-doc-generator-markdown")
DOCUMENTS = ("technical-project", "ui-test-catalog", "coverage-matrix")


def python_setting() -> str:
    """This interpreter, in the form bash runs on every platform."""
    return Path(sys.executable).as_posix()


def install(tmp_path: Path, config: str, fake_git: str) -> None:
    """A copy of the runner, the pins and the pin report in ``tmp_path``, with ``config`` and ``fake_git``."""
    for source, folder in ((RUNNER, "integration"), (PINS, "collector"), (PIN_REPORT, "examples"),
                           (CHECKER_REQUIREMENTS, "examples")):
        (tmp_path / "tests" / folder).mkdir(parents=True, exist_ok=True)
        shutil.copy(source, tmp_path / "tests" / folder / source.name)
    (tmp_path / "tests" / "integration" / ".env.local").write_text(config, encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "git").write_text(fake_git, encoding="utf-8", newline="\n")
    (bin_dir / "git").chmod(0o755)


def invoke(tmp_path: Path, **env: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    """Run the installed runner with ``env`` added; its result, and every git command it started."""
    calls = tmp_path / "git-calls.txt"
    calls.unlink(missing_ok=True)
    path = f"{tmp_path / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}"
    result = subprocess.run([BASH, str(tmp_path / "tests" / "integration" / RUNNER.name)], cwd=tmp_path,
                            env={**os.environ, "PATH": path, **env}, capture_output=True, text=True, timeout=120,
                            check=False)
    return result, calls.read_text(encoding="utf-8").splitlines() if calls.exists() else []


def run(tmp_path: Path, config: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    """Run a copy of the runner over ``config`` with the refusing ``git``."""
    install(tmp_path, config, FAKE_GIT.format(calls=(tmp_path / "git-calls.txt").as_posix()))
    return invoke(tmp_path)


def install_chain(tmp_path: Path, config: str) -> Path:
    """The runner over ``config`` with the chain's ``git`` and stand-ins; the folder the stand-ins record in."""
    record = tmp_path / "record"
    record.mkdir()
    stub = tmp_path / "stub-local-integration.sh"
    stub.write_text(STUB_COMPONENT.format(record=record.as_posix()), encoding="utf-8", newline="\n")
    install(tmp_path, config, CHAIN_GIT.format(calls=(tmp_path / "git-calls.txt").as_posix(), tag=TAG,
                                               stub=stub.as_posix(), requirements=CHECKER_REQUIREMENTS.as_posix(),
                                               sha=SHA))
    return record


def settings(path: Path) -> dict[str, str]:
    """The KEY=value lines of an `.env.local` the runner wrote."""
    return dict(line.split("=", 1) for line in path.read_text(encoding="utf-8").splitlines()
                if line and not line.startswith("#"))


def settings_of_the_testbed_stage() -> dict[str, str]:
    """The collector settings tests/testbed/run-testbed-stage.sh gives the testbed's `core`."""
    found = dict(re.findall(r'^([A-Z_]+)="([^"]*)"$', TESTBED_STAGE.read_text(encoding="utf-8"), re.MULTILINE))
    core = found["CORE"]
    return {
        "PROJECT_ID": found["PROJECT_ID"],
        "ORGANIZATION_NAME": found["TESTBED_ORG"],
        "REPOSITORY_NAME": found["TESTBED_REPO"],
        "DOC_SOURCE_US_PATHS": found["US_PATHS"].replace("$CORE", core),
        "DOC_SOURCE_FUNC_PATHS": found["FUNC_PATHS"].replace("$CORE", core),
        "DOC_SOURCE_PAGES_PATHS": found["PAGES_PATHS"].replace("$CORE", core),
        "UI_TESTS_PATHS": found["SCENARIO_PATHS"].replace("$CORE", core),
    }


# The stand-ins' calls of a whole run, `<clone> <--check or run> <OUT_DIR's name>`: each step's --check, then its run.
FULL_CHAIN = [f"{clone} {mode} {folder}"
              for clone, folder in (("living-doc-collector-gh", "run"),
                                    ("living-doc-toolkit", "inner"), ("living-doc-generator-markdown", "inner"),
                                    ("living-doc-toolkit", "release"), ("living-doc-generator-markdown", "release"))
              for mode in ("--check", "run")]


def assert_refused(tmp_path: Path, result: subprocess.CompletedProcess[str], git_calls: list[str],
                   *expected: str) -> None:
    """Non-zero, one line naming the problem, and nothing cloned or written."""
    assert result.returncode != 0
    assert result.stdout == ""
    lines = result.stderr.splitlines()
    assert len(lines) == 1, result.stderr
    for text in expected:
        assert text in lines[0], lines[0]
    assert all(call.startswith("ls-remote ") for call in git_calls), git_calls
    assert not (tmp_path / "out").exists()


def lines(settings: dict[str, str]) -> str:
    return "".join(f"{key}={value}\n" for key, value in settings.items())


def test_an_unknown_key_is_refused_by_its_line_number(tmp_path: Path) -> None:
    result, git_calls = run(tmp_path, "# a comment\nTARGET=testbed\nCOLLECTOR_REF=v1.0.0\n")

    assert_refused(tmp_path, result, git_calls, "tests/integration/.env.local:3:", "not a setting of this runner")
    assert "COLLECTOR_REF" not in result.stderr
    assert git_calls == []


@pytest.mark.parametrize("key, ref", [
    ("COLLECTOR_GH_REF", "93faed7"),
    ("TOOLKIT_REF", "master"),
    ("GENERATOR_MARKDOWN_REF", "e6b1c2d6525fe5fb9ee8418f29672c902831134"),
    ("TESTBED_REF", "master"),
])
def test_a_ref_that_is_neither_a_full_sha_nor_a_tag_is_refused(tmp_path: Path, key: str, ref: str) -> None:
    result, git_calls = run(tmp_path, f"TARGET=testbed\n{key}={ref}\nPYTHON={python_setting()}\n")

    assert_refused(tmp_path, result, git_calls, f"{key} '{ref}'", "neither a full 40-hex commit SHA nor a tag")
    assert any(f"refs/tags/{ref}" in call for call in git_calls), git_calls


def test_a_missing_target_is_refused(tmp_path: Path) -> None:
    result, git_calls = run(tmp_path, "COLLECTOR_GH_REF=\nOUT_DIR=\n")

    assert_refused(tmp_path, result, git_calls, "TARGET is not set")
    assert git_calls == []


def test_an_unknown_target_is_refused(tmp_path: Path) -> None:
    result, git_calls = run(tmp_path, "TARGET=staging\n")

    assert_refused(tmp_path, result, git_calls, "TARGET 'staging'", "not testbed or project")
    assert git_calls == []


@pytest.mark.parametrize("missing", ["PROJECT_ID", "TARGET_CHECKOUT", "ORGANIZATION_NAME", "REPOSITORY_NAME",
                                     "DOC_SOURCE_US_PATHS", "UI_TESTS_PATHS"])
def test_a_project_without_a_required_collector_key_is_refused(tmp_path: Path, missing: str) -> None:
    settings = {key: value for key, value in PROJECT.items() if key != missing}

    result, git_calls = run(tmp_path, lines(settings))

    assert_refused(tmp_path, result, git_calls, f"{missing} is not set", "TARGET=project needs it")
    assert git_calls == []


def test_the_testbed_refuses_a_project_key(tmp_path: Path) -> None:
    result, git_calls = run(tmp_path, "TARGET=testbed\nPROJECT_ID=absa-1\n")

    assert_refused(tmp_path, result, git_calls, "PROJECT_ID is set", "TARGET=testbed")
    assert git_calls == []


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_a_testbed_run_chains_the_components_in_both_views_into_one_root(tmp_path: Path) -> None:
    record = install_chain(tmp_path, f"TARGET=testbed\nOUT_DIR=run\nPYTHON={python_setting()}\n")

    result, git_calls = invoke(tmp_path)

    assert result.returncode == 0, result.stderr
    assert read(record / "calls.txt").splitlines() == FULL_CHAIN
    header = result.stdout.split("\n== collector-gh", 1)[0]
    for label in ("run id:", "living-doc:", "collector-gh:", "toolkit:", "generator-markdown:", "target:"):
        assert f"\n{label}" in header, header
    assert f"testbed-core: AbsaOSS/living-doc-testbed {SHA} (master)" in header
    for repository in (*COMPONENTS, "living-doc-testbed"):
        assert any(call.startswith(f"clone --quiet --filter=blob:none https://github.com/AbsaOSS/{repository} ")
                   for call in git_calls), git_calls

    collector = settings(record / "living-doc-collector-gh.run.env")
    assert {key: collector[key] for key in settings_of_the_testbed_stage()} == settings_of_the_testbed_stage()
    assert collector["TARGET_CHECKOUT"].endswith("/out/testbed")
    assert collector["OUT_DIR"].endswith("/run")
    root = tmp_path / "run"
    for view in ("inner", "release"):
        toolkit = settings(record / f"living-doc-toolkit.{view}.env")
        assert toolkit["DOC_INPUT"].endswith("/run/collector-gh/doc-source/doc-source.json")
        assert toolkit["TESTS_INPUT"].endswith("/run/collector-gh/ui-tests/ui-tests.json")
        assert toolkit["VIEW"] == view
        assert toolkit["OUT_DIR"].endswith(f"/run/{view}")
        generator = settings(record / f"living-doc-generator-markdown.{view}.env")
        toolkit_out = f"/run/{view}/toolkit"
        assert generator["TECHNICAL_PROJECT_INPUT"].endswith(f"{toolkit_out}/normalize-docs/generator-ready.json")
        assert generator["UI_TEST_CATALOG_INPUT"].endswith(f"{toolkit_out}/normalize-tests/ui-test-catalog.json")
        assert generator["COVERAGE_MATRIX_INPUT"].endswith(f"{toolkit_out}/coverage-matrix/coverage-matrix.json")
        assert generator["OUT_DIR"].endswith(f"/run/{view}")
        for document in DOCUMENTS:
            assert (root / view / "generator-markdown" / f"{document}.md").is_file()
        assert f"stub: living-doc-toolkit:{view} done" in read(root / view / "toolkit" / "local-integration.log")
        assert f"stub: living-doc-generator-markdown:{view} done" in read(root / view / "local-integration.log")
    assert "stub: living-doc-collector-gh:run done" in read(root / "collector-gh" / "local-integration.log")
    assert "OK: every component pins living-doc-utilities" in read(root / "pin-report.txt")
    assert read(root / "local-integration.log").startswith("== tests/integration/local-integration.sh\nrun id:")


def test_an_existing_tag_is_accepted_as_a_ref(tmp_path: Path) -> None:
    install_chain(tmp_path, f"TARGET=testbed\nCOLLECTOR_GH_REF={TAG}\nOUT_DIR=run\nPYTHON={python_setting()}\n")

    result, git_calls = invoke(tmp_path)

    assert result.returncode == 0, result.stderr
    assert f"(COLLECTOR_GH_REF={TAG})" in result.stdout
    assert any(call.endswith(f"checkout --quiet --force --detach {TAG}") for call in git_calls), git_calls


def test_a_failing_step_stops_the_chain_and_the_runners_log_names_it(tmp_path: Path) -> None:
    record = install_chain(tmp_path, f"TARGET=testbed\nOUT_DIR=run\nPYTHON={python_setting()}\n")

    result, _ = invoke(tmp_path, FAIL_AT="living-doc-toolkit:release")

    assert result.returncode != 0
    assert read(record / "calls.txt").splitlines() == FULL_CHAIN[:FULL_CHAIN.index("living-doc-toolkit run release") + 1]
    assert not (tmp_path / "run" / "pin-report.txt").exists()
    assert "toolkit, release view failed" in result.stderr
    assert "toolkit, release view failed" in read(tmp_path / "run" / "local-integration.log").splitlines()[-1]


def test_a_rerun_into_the_same_root_leaves_nothing_of_the_earlier_run(tmp_path: Path) -> None:
    install_chain(tmp_path, f"TARGET=testbed\nOUT_DIR=run\nPYTHON={python_setting()}\n")
    first, _ = invoke(tmp_path)
    assert first.returncode == 0, first.stderr
    (tmp_path / "run" / "env.local").write_text("TARGET=testbed\n", encoding="utf-8")

    second, _ = invoke(tmp_path, FAIL_AT="living-doc-toolkit:release")

    assert second.returncode != 0
    assert not (tmp_path / "run" / "pin-report.txt").exists()
    assert not (tmp_path / "run" / "release" / "generator-markdown").exists()
    assert not (tmp_path / "run" / "release" / "toolkit" / "normalize-docs").exists()
    assert (tmp_path / "run" / "inner" / "generator-markdown" / "technical-project.md").is_file()
    assert read(tmp_path / "run" / "env.local") == "TARGET=testbed\n"


def test_a_run_clears_only_the_paths_the_chain_writes(tmp_path: Path) -> None:
    install_chain(tmp_path, f"TARGET=testbed\nOUT_DIR=run\nPYTHON={python_setting()}\n")
    kept = [tmp_path / "run" / folder / "notes.txt"
            for folder in ("collector-gh", "inner", "release", "inner/toolkit", "release/toolkit")]
    for path in kept:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not the runner's\n", encoding="utf-8")

    result, _ = invoke(tmp_path)

    assert result.returncode == 0, result.stderr
    assert [path for path in kept if not path.exists()] == []


def test_a_project_run_forwards_its_checkout_and_every_collector_setting(tmp_path: Path) -> None:
    project = {**PROJECT, "TARGET_CHECKOUT": "project-checkout", "DOC_SOURCE_FUNC_PATHS": "features/func",
               "DOC_SOURCE_PAGES_PATHS": "pages", "GITHUB_SERVER_URL": "https://ghe.example.com"}
    record = install_chain(tmp_path, lines({**project, "OUT_DIR": "run", "PYTHON": python_setting()}))
    (tmp_path / "project-checkout" / ".git").mkdir(parents=True)

    result, git_calls = invoke(tmp_path)

    assert result.returncode == 0, result.stderr
    assert read(record / "calls.txt").splitlines() == FULL_CHAIN
    collector = settings(record / "living-doc-collector-gh.run.env")
    assert collector.pop("TARGET_CHECKOUT").endswith("/project-checkout")
    assert collector.pop("OUT_DIR").endswith("/run")
    collector.pop("PYTHON")
    assert collector == {key: value for key, value in project.items() if key not in ("TARGET", "TARGET_CHECKOUT")}
    assert f"\ntarget:              absa-1: {SHA} (" in result.stdout
    assert not any("living-doc-testbed" in call for call in git_calls), git_calls


def test_a_reused_clone_of_another_repository_is_cloned_again(tmp_path: Path) -> None:
    install_chain(tmp_path, f"TARGET=testbed\nOUT_DIR=run\nPYTHON={python_setting()}\n")
    first, _ = invoke(tmp_path)
    assert first.returncode == 0, first.stderr
    toolkit = tmp_path / "out" / "components" / "living-doc-toolkit"
    (toolkit / ".git" / "origin-url").write_text("https://github.com/someone/living-doc-toolkit\n", encoding="utf-8")
    (toolkit / "planted.txt").write_text("not the toolkit's\n", encoding="utf-8")

    second, git_calls = invoke(tmp_path)

    assert second.returncode == 0, second.stderr
    assert not (toolkit / "planted.txt").exists()
    assert any(call.startswith("clone --quiet --filter=blob:none https://github.com/AbsaOSS/living-doc-toolkit ")
               for call in git_calls), git_calls
    assert not any(call.startswith("clone ") and "living-doc-collector-gh" in call for call in git_calls), git_calls


def test_every_clone_is_cleaned_after_checkout_and_the_testbed_of_ignored_files_too(tmp_path: Path) -> None:
    install_chain(tmp_path, f"TARGET=testbed\nOUT_DIR=run\nPYTHON={python_setting()}\n")

    result, git_calls = invoke(tmp_path)

    assert result.returncode == 0, result.stderr
    for clone, flags in (("testbed", "-ffdx"), *((f"components/{c}", "-ffd") for c in COMPONENTS)):
        checkout = next(i for i, call in enumerate(git_calls) if f"/out/{clone} -c " in call and " checkout " in call)
        assert git_calls[checkout + 1].endswith(f"/out/{clone} clean -q {flags}"), git_calls[checkout:checkout + 2]


@pytest.mark.parametrize("target, out_dir, inside", [
    ("TARGET=testbed\n", "out/testbed", "the runner's testbed clone"),
    ("TARGET=testbed\n", "out/components/living-doc-toolkit/output", "the runner's component clones"),
    (lines(PROJECT), "../some-checkout", "TARGET_CHECKOUT"),
    (lines(PROJECT), "../some-checkout/docs", "TARGET_CHECKOUT"),
])
def test_an_output_root_inside_a_checkout_the_run_reads_or_a_clone_is_refused(
        tmp_path: Path, target: str, out_dir: str, inside: str) -> None:
    result, git_calls = run(tmp_path, f"{target}OUT_DIR={out_dir}\nPYTHON={python_setting()}\n")

    assert_refused(tmp_path, result, git_calls, "OUT_DIR", f"is inside {inside}")


def test_an_untracked_file_in_the_target_marks_its_commit(tmp_path: Path) -> None:
    install_chain(tmp_path, lines({**PROJECT, "TARGET_CHECKOUT": "project-checkout", "OUT_DIR": "run",
                                   "PYTHON": python_setting()}))
    (tmp_path / "project-checkout" / ".git").mkdir(parents=True)
    (tmp_path / "project-checkout" / "untracked.feature").write_text("Feature: not committed\n", encoding="utf-8")

    result, _ = invoke(tmp_path)

    assert result.returncode == 0, result.stderr
    assert f"\ntarget:              absa-1: {SHA} (uncommitted changes) (" in result.stdout
    assert f"\nliving-doc:          {SHA}\n" in result.stdout
