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
"""Tests for tests/examples/check_utilities_pins.py — the living-doc-utilities pin report.

Run: ``python -m pytest tests/examples/test_check_utilities_pins.py`` (needs pytest only).
Every case reads synthetic requirements files from ``tmp_path``; the one fetch test replaces
the network call, so nothing here goes online.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from check_utilities_pins import main, utilities_spec

COLLECTOR_REQUIREMENTS = """\
# Runtime dependencies only.
living-doc-utilities==0.6.0
pydantic==2.13.5
tomli==2.4.1; python_version < "3.11"
"""

TOOLKIT_REQUIREMENTS = """\
# Runtime only: the packages, each installed by path.
living-doc-utilities==0.6.0
./packages/core
./apps/cli
"""


@pytest.fixture
def requirements(tmp_path: Path):
    """Write the three requirements files and return the ``--requirements`` arguments for them."""
    def write(collector: str, examples_check: str) -> list[str]:
        (tmp_path / "collector.txt").write_text(collector, encoding="utf-8")
        (tmp_path / "toolkit.txt").write_text(TOOLKIT_REQUIREMENTS, encoding="utf-8")
        (tmp_path / "examples.txt").write_text(examples_check, encoding="utf-8")
        return ["--requirements", f"collector-gh={tmp_path / 'collector.txt'}",
                "--requirements", f"toolkit={tmp_path / 'toolkit.txt'}",
                "--requirements", f"examples-check={tmp_path / 'examples.txt'}"]
    return write


@pytest.fixture(autouse=True)
def _no_annotations(monkeypatch: pytest.MonkeyPatch) -> None:
    # The report prints GitHub workflow annotations inside Actions; assert on the plain form.
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)


def test_matching_pins_pass(requirements, capsys: pytest.CaptureFixture[str]) -> None:
    args = requirements(COLLECTOR_REQUIREMENTS, "PyYAML==6.0.3\nliving-doc-utilities==0.6.0\n")

    assert main(["--strict", *args]) == 0
    out = capsys.readouterr().out
    assert "collector-gh" in out and "examples-check" in out and "0.6.0" in out
    assert "OK: every component pins living-doc-utilities 0.6." in out


def test_patch_difference_is_not_a_mismatch(requirements, capsys: pytest.CaptureFixture[str]) -> None:
    args = requirements(COLLECTOR_REQUIREMENTS, "living-doc-utilities==0.6.1\n")

    assert main(["--strict", *args]) == 0
    assert "warning" not in capsys.readouterr().out


def test_minor_mismatch_warns(requirements, capsys: pytest.CaptureFixture[str]) -> None:
    args = requirements(COLLECTOR_REQUIREMENTS, "living-doc-utilities==0.5.0\n")

    assert main(args) == 0
    out = capsys.readouterr().out
    assert ("warning: living-doc-utilities minor-version mismatch: collector-gh 0.6.0, "
            "toolkit 0.6.0, examples-check 0.5.0") in out


def test_minor_mismatch_fails_with_strict(requirements, capsys: pytest.CaptureFixture[str]) -> None:
    args = requirements(COLLECTOR_REQUIREMENTS, "living-doc-utilities==0.5.0\n")

    assert main(["--strict", *args]) == 1
    assert "error: living-doc-utilities minor-version mismatch" in capsys.readouterr().out


def test_missing_line_warns_and_fails_with_strict(requirements,
                                                  capsys: pytest.CaptureFixture[str]) -> None:
    args = requirements("pydantic==2.13.5\n", "living-doc-utilities==0.6.0\n")

    assert main(args) == 0
    out = capsys.readouterr().out
    assert "warning: collector-gh pins no living-doc-utilities" in out
    assert main(["--strict", *args]) == 1


def test_inexact_pin_warns(requirements, capsys: pytest.CaptureFixture[str]) -> None:
    args = requirements("living-doc-utilities>=0.6\n", "living-doc-utilities==0.6.0\n")

    assert main(args) == 0
    assert ("warning: collector-gh pins living-doc-utilities>=0.6, not one exact '==' version"
            in capsys.readouterr().out)


def test_ci_run_annotates_the_warning(requirements, capsys: pytest.CaptureFixture[str],
                                      monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    args = requirements(COLLECTOR_REQUIREMENTS, "living-doc-utilities==0.5.0\n")

    assert main(args) == 0
    assert "::warning::living-doc-utilities minor-version mismatch" in capsys.readouterr().out


@pytest.mark.parametrize(("line", "spec"), [
    ("living-doc-utilities==0.6.0", "==0.6.0"),
    ("Living_Doc.Utilities == 0.6.0  # runtime", "==0.6.0"),
    ('living-doc-utilities[github]==0.6.0; python_version >= "3.10"', "==0.6.0"),
    ("living-doc-utilities-extra==1.0.0", None),
    ("-r other.txt", None),
])
def test_requirement_line_parsing(line: str, spec: str | None) -> None:
    assert utilities_spec(f"PyYAML==6.0.3\n{line}\n") == spec


def test_requirements_with_local_package_lines() -> None:
    assert utilities_spec(TOOLKIT_REQUIREMENTS) == "==0.6.0"


def test_unreadable_requirements_file_exits_2(tmp_path: Path,
                                              capsys: pytest.CaptureFixture[str]) -> None:
    missing = tmp_path / "nope.txt"
    assert main(["--requirements", f"collector-gh={missing}",
                 "--requirements", f"examples-check={missing}"]) == 2
    assert "cannot read" in capsys.readouterr().err


def test_component_requirements_fetched_at_the_pinned_ref(tmp_path: Path,
                                                          capsys: pytest.CaptureFixture[str]) -> None:
    pins = tmp_path / "pins.env"
    pins.write_text("# comment\nCOLLECTOR_GH_REF=0123456789abcdef0123456789abcdef01234567\n"
                    "TOOLKIT_REF=89abcdef0123456789abcdef0123456789abcdef\n",
                    encoding="utf-8")
    examples = tmp_path / "examples.txt"
    examples.write_text("living-doc-utilities==0.6.0\n", encoding="utf-8")
    fetched: list[str] = []

    def fetcher(url: str) -> str:
        fetched.append(url)
        return COLLECTOR_REQUIREMENTS

    assert main(["--pins", str(pins), "--requirements", f"examples-check={examples}"],
                fetcher=fetcher) == 0
    assert fetched == ["https://raw.githubusercontent.com/AbsaOSS/living-doc-collector-gh/"
                       "0123456789abcdef0123456789abcdef01234567/requirements.txt",
                       "https://raw.githubusercontent.com/AbsaOSS/living-doc-toolkit/"
                       "89abcdef0123456789abcdef0123456789abcdef/requirements.txt"]
    assert "AbsaOSS/living-doc-collector-gh@0123456789ab requirements.txt" in capsys.readouterr().out


def test_pins_file_without_the_ref_exits_2(tmp_path: Path,
                                           capsys: pytest.CaptureFixture[str]) -> None:
    pins = tmp_path / "pins.env"
    pins.write_text("# no pins\n", encoding="utf-8")

    assert main(["--pins", str(pins)], fetcher=lambda url: "") == 2
    assert "sets no COLLECTOR_GH_REF" in capsys.readouterr().err
