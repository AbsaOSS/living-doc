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
"""Tests for tests/docs/retired_names_check.py — the retired-names check.

Run: ``python -m pytest tests/docs -q`` (needs pytest and git). Each case builds small git checkouts
in ``tmp_path`` with an ``origin`` naming their repository; the first reads this repository's own
checkout with its allow-list. Nothing goes online.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from retired_names_check import RETIRED_NAMES, main

PLANTED = "Run normalize-issues before the generator.\n"


def checkout(root: Path, repository: str, tracked: dict[str, str],
             untracked: dict[str, str] | None = None) -> Path:
    """A git work tree named after ``repository``, ``tracked`` added to its index."""
    path = root / repository.rsplit("/", 1)[-1]
    for name, text in {**tracked, **(untracked or {})}.items():
        (path / name).parent.mkdir(parents=True, exist_ok=True)
        (path / name).write_text(text, encoding="utf-8")
    path.mkdir(exist_ok=True)
    git = ["git", "-C", str(path)]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "remote", "add", "origin", f"https://github.com/{repository}.git"], check=True)
    if tracked:
        subprocess.run([*git, "add", "--", *tracked], check=True)
    return path


@pytest.fixture
def living_doc(tmp_path: Path) -> Path:
    return checkout(tmp_path, "AbsaOSS/living-doc", {"README.md": "Living Documentation.\n"})


def run(tmp_path: Path, *checkouts: Path, allow: str = "", strict: bool = True) -> int:
    allow_list = tmp_path / "allow.txt"
    allow_list.write_text(allow, encoding="utf-8")
    return main([*(["--strict"] if strict else []), "--allow-list", str(allow_list),
                 *map(str, checkouts)])


def test_this_repository_and_a_clean_component_pass(tmp_path: Path,
                                                    capsys: pytest.CaptureFixture[str]) -> None:
    toolkit = checkout(tmp_path, "AbsaOSS/living-doc-toolkit", {"README.md": "Toolkit.\n"})

    assert main(["--strict", str(toolkit)]) == 0, capsys.readouterr().out
    header = capsys.readouterr().out.splitlines()[0]
    assert "/living-doc," in header and "AbsaOSS/living-doc-toolkit" in header, header


def test_planted_name_fails_with_strict(tmp_path: Path, living_doc: Path,
                                        capsys: pytest.CaptureFixture[str]) -> None:
    toolkit = checkout(tmp_path, "AbsaOSS/living-doc-toolkit", {"docs/usage.md": "Usage.\n" + PLANTED})

    assert run(tmp_path, living_doc, toolkit) == 1
    assert "AbsaOSS/living-doc-toolkit  docs/usage.md:2  normalize-issues" in capsys.readouterr().out


def test_without_strict_reports_and_exits_0(tmp_path: Path, living_doc: Path,
                                            capsys: pytest.CaptureFixture[str]) -> None:
    toolkit = checkout(tmp_path, "AbsaOSS/living-doc-toolkit", {"docs/usage.md": PLANTED})

    assert run(tmp_path, living_doc, toolkit, strict=False) == 0
    out = capsys.readouterr().out
    assert "AbsaOSS/living-doc-toolkit  docs/usage.md:1  normalize-issues" in out
    assert "warning: 1 finding(s)" in out


@pytest.mark.parametrize("name", RETIRED_NAMES)
def test_each_name_is_matched_as_written(tmp_path: Path, living_doc: Path, name: str,
                                         capsys: pytest.CaptureFixture[str]) -> None:
    generator = checkout(tmp_path, "AbsaOSS/living-doc-generator-markdown",
                         {"src/render.py": f"value = data[{name!r}]  # {name}\n"})

    assert run(tmp_path, living_doc, generator) == 1
    assert f"src/render.py:1  {name}" in capsys.readouterr().out


def test_tests_changelogs_and_collector_gh_doc_issues_are_skipped(tmp_path: Path,
                                                                 living_doc: Path) -> None:
    collector = checkout(tmp_path, "AbsaOSS/living-doc-collector-gh", {
        "tests/test_reader.py": PLANTED, "src/tests/fixture.md": PLANTED,
        "CHANGELOG.md": PLANTED, "doc_issues/model.py": PLANTED, "README.md": "Collector.\n"})

    assert run(tmp_path, living_doc, collector) == 0


def test_doc_issues_is_skipped_in_collector_gh_only(tmp_path: Path, living_doc: Path,
                                                    capsys: pytest.CaptureFixture[str]) -> None:
    toolkit = checkout(tmp_path, "AbsaOSS/living-doc-toolkit", {"doc_issues/model.py": PLANTED})

    assert run(tmp_path, living_doc, toolkit) == 1
    assert "doc_issues/model.py:1" in capsys.readouterr().out


def test_untracked_file_is_not_read(tmp_path: Path, living_doc: Path) -> None:
    toolkit = checkout(tmp_path, "AbsaOSS/living-doc-toolkit", {"README.md": "Toolkit.\n"},
                       untracked={"notes.md": PLANTED, ".venv/lib/site.py": PLANTED})

    assert run(tmp_path, living_doc, toolkit) == 0


def test_allow_list_entry_skips_its_file_in_living_doc(tmp_path: Path) -> None:
    living_doc = checkout(tmp_path, "AbsaOSS/living-doc",
                          {"agentic/schema.json": '{"type": "array", "items": {}}\n'})

    assert run(tmp_path, living_doc,
               allow="# path  reason\nagentic/schema.json\tthe JSON Schema keyword\n") == 0


def test_allow_list_entry_that_skips_no_hit_fails(tmp_path: Path, living_doc: Path,
                                                  capsys: pytest.CaptureFixture[str]) -> None:
    assert run(tmp_path, living_doc, allow="\nagentic/gone.md  quoted to forbid it\n") == 1
    assert "allow.txt:2  agentic/gone.md skips no hit in AbsaOSS/living-doc" in capsys.readouterr().out


def test_allow_list_entry_without_a_reason_fails(tmp_path: Path,
                                                 capsys: pytest.CaptureFixture[str]) -> None:
    living_doc = checkout(tmp_path, "AbsaOSS/living-doc", {"agentic/schema.json": '"items"\n'})

    assert run(tmp_path, living_doc, allow="agentic/schema.json\n") == 1
    assert "allow.txt:1  agentic/schema.json gives no reason" in capsys.readouterr().out


def test_a_directory_that_is_no_checkout_exits_2(tmp_path: Path, living_doc: Path,
                                                 capsys: pytest.CaptureFixture[str]) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()

    assert run(tmp_path, living_doc, plain) == 2
    assert "error:" in capsys.readouterr().err
