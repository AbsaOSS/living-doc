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
"""Tests for tests/integration/local-integration.sh: the configurations it refuses before any clone.

Run: ``python -m pytest tests/integration -q`` (needs pytest and bash). Each case copies the runner and the pins into
``tmp_path``, writes a configuration there, and runs the runner with a ``git`` first on ``PATH`` that answers every
``ls-remote`` with "no such tag" and fails any other command. Nothing goes online, and a clone would show in its log.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
RUNNER = HERE / "local-integration.sh"
PINS = REPO_ROOT / "tests" / "collector" / "collector-pins.env"
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


def python_setting() -> str:
    """This interpreter, in the form bash runs on every platform."""
    return Path(sys.executable).as_posix()


def run(tmp_path: Path, config: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    """Run a copy of the runner over ``config``; its result, and every git command it started."""
    runner = tmp_path / "tests" / "integration" / RUNNER.name
    runner.parent.mkdir(parents=True)
    shutil.copy(RUNNER, runner)
    (tmp_path / "tests" / "collector").mkdir(parents=True)
    shutil.copy(PINS, tmp_path / "tests" / "collector" / PINS.name)
    (runner.parent / ".env.local").write_text(config, encoding="utf-8")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    calls = tmp_path / "git-calls.txt"
    fake_git = bin_dir / "git"
    fake_git.write_text(FAKE_GIT.format(calls=calls.as_posix()), encoding="utf-8", newline="\n")
    fake_git.chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

    result = subprocess.run([BASH, str(runner)], cwd=tmp_path, env=env, capture_output=True, text=True,
                            timeout=60, check=False)
    git_calls = calls.read_text(encoding="utf-8").splitlines() if calls.exists() else []
    return result, git_calls


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
