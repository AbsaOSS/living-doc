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
"""Tests for tests/docs/debt_overview_check.py — the debt overview's drift check.

Run: ``python -m pytest tests/docs -q``. GitHub is replaced by a set of open issues and a map of the other issues'
states, so nothing goes online.
"""

from __future__ import annotations

import pytest

import debt_overview_check
from debt_overview_check import PAGE, findings, main, next_link, parse_page

LISTS = """# Debt overview

## Topics

- `ci`: workflows.
- `epic`: planned work.

## Wakes on

- `when:next-pr`: ready.

## Open debt

| Issue | Topics | Anchors | Wakes on |
|---|---|---|---|
"""
EPIC = "| [living-doc#110](https://github.com/AbsaOSS/living-doc/issues/110) | `epic` | `doc-source` | — |\n"
DEBT = (
    "| [living-doc-toolkit#118](https://github.com/AbsaOSS/living-doc-toolkit/issues/118) | `ci` "
    "| `normalize-docs` `--input` | `when:next-pr` |\n"
)
OPEN = {("living-doc", 110), ("living-doc-toolkit", 118)}


def check(text: str, open_issues: set[tuple[str, int]] = OPEN, states: dict | None = None) -> list[str]:
    return findings(parse_page(text), open_issues, lambda repository, number: (states or {})[(repository, number)])


def test_a_page_matching_the_open_issues_has_no_finding():
    assert check(LISTS + EPIC + DEBT) == []


def test_an_open_issue_without_a_row_is_a_finding():
    assert check(LISTS + EPIC) == ["living-doc-toolkit#118: open tech-debt or epic issue without a row"]


def test_a_row_whose_issue_is_closed_is_a_finding():
    found = check(LISTS + EPIC + DEBT, {("living-doc", 110)}, {("living-doc-toolkit", 118): "closed"})
    assert found == ["living-doc-toolkit#118: row whose issue is closed"]


def test_a_row_whose_issue_lost_its_label_is_a_finding():
    found = check(LISTS + EPIC + DEBT, {("living-doc", 110)}, {("living-doc-toolkit", 118): "open"})
    assert found == ["living-doc-toolkit#118: row whose issue is no longer labelled tech debt or epic"]


def test_a_row_whose_issue_does_not_exist_is_a_finding():
    found = check(LISTS + EPIC + DEBT, {("living-doc", 110)}, {("living-doc-toolkit", 118): "missing"})
    assert found == ["living-doc-toolkit#118: row whose issue does not exist"]


def test_a_tag_on_neither_list_is_a_finding():
    row = DEBT.replace("`ci`", "`ci` `docs`").replace("`when:next-pr`", "`when:later`")
    assert check(LISTS + EPIC + row) == [
        "living-doc-toolkit#118: topic `docs` is not on the Topics list",
        "living-doc-toolkit#118: wake tag `when:later` is not on the Wakes on list",
    ]


def test_a_duplicate_row_is_a_finding():
    assert check(LISTS + EPIC + DEBT + DEBT) == ["living-doc-toolkit#118: duplicate row"]


def test_a_malformed_row_is_a_finding_naming_its_line():
    row = "| [living-doc#111](https://github.com/AbsaOSS/living-doc/issues/112) | `epic` | `x` | — |\n"
    found = check(LISTS + EPIC + DEBT + row)
    assert found == [f"line 18: not a row of four cells with its issue's link: {row.strip()!r}"]


def test_a_row_outside_the_seven_repositories_is_a_finding():
    row = "| [agentic-toolkit#45](https://github.com/AbsaOSS/agentic-toolkit/issues/45) | `ci` | `x` | `when:next-pr` |\n"
    assert check(LISTS + row + EPIC + DEBT) == ["agentic-toolkit#45: not one of the seven repositories"]


def test_a_row_out_of_order_is_a_finding():
    assert check(LISTS + DEBT + EPIC) == ["living-doc#110: row out of order; rows are sorted by repository, then number"]


def test_an_escaped_pipe_in_a_cell_stays_in_its_cell():
    row = DEBT.replace("`--input`", r"`--format md\|pdf`")
    page = parse_page(LISTS + EPIC + row)
    assert page.problems == [] and len(page.rows) == 2


def test_open_issues_are_read_page_by_page_without_pull_requests(monkeypatch):
    pages = {
        "first": ([{"number": 1}, {"number": 2, "pull_request": {}}], '<second>; rel="next"'),
        "second": ([{"number": 3}], None),
    }

    def get(url, token):
        if url.startswith(f"{debt_overview_check.API}/repos/AbsaOSS/living-doc/issues?") and "type%3Atech-debt" in url:
            return pages["first"]
        return pages["second"] if url == "second" else ([], None)

    monkeypatch.setattr(debt_overview_check, "_get", get)
    assert debt_overview_check.fetch_open_issues(None) == {("living-doc", 1), ("living-doc", 3)}


def test_a_list_answer_that_is_not_a_list_cannot_be_read(monkeypatch):
    monkeypatch.setattr(debt_overview_check, "_get", lambda url, token: ({"message": "Bad credentials"}, None))
    with pytest.raises(debt_overview_check.CheckError):
        debt_overview_check.fetch_open_issues(None)


@pytest.mark.parametrize(
    ("answer", "state"),
    [({"state": "closed"}, "closed"), ({"state": "open"}, "open"), ({"state": "open", "pull_request": {}}, "missing")],
)
def test_an_issue_outside_the_open_set_has_its_state(monkeypatch, answer, state):
    monkeypatch.setattr(debt_overview_check, "_get", lambda url, token: (answer, None))
    assert debt_overview_check.fetch_state("living-doc", 7, None) == state


def test_an_issue_github_does_not_know_is_missing(monkeypatch):
    def not_found(url, token):
        raise debt_overview_check.NotFound(f"{url}: HTTP 404")

    monkeypatch.setattr(debt_overview_check, "_get", not_found)
    assert debt_overview_check.fetch_state("living-doc", 7, None) == "missing"


def test_the_link_header_names_the_next_page():
    header = (
        '<https://api.github.com/repositories/1/issues?page=2>; rel="next", '
        '<https://api.github.com/repositories/1/issues?page=5>; rel="last"'
    )
    assert next_link(header) == "https://api.github.com/repositories/1/issues?page=2"
    assert next_link('<https://api.github.com/repositories/1/issues?page=1>; rel="prev"') is None
    assert next_link(None) is None


def test_the_page_parses_and_uses_only_listed_tags():
    page = parse_page(PAGE.read_text(encoding="utf-8"))
    assert page.rows
    assert findings(page, {(row.repository, row.number) for row in page.rows}, lambda *_: "open") == []


@pytest.mark.parametrize(("open_issues", "expected"), [(OPEN, 0), (set(), 1)])
def test_main_prints_one_line_per_finding_and_exits_by_them(tmp_path, monkeypatch, capsys, open_issues, expected):
    page = tmp_path / "debt-overview.md"
    page.write_text(LISTS + EPIC + DEBT, encoding="utf-8")
    monkeypatch.setattr(debt_overview_check, "fetch_open_issues", lambda token: open_issues)
    monkeypatch.setattr(debt_overview_check, "fetch_state", lambda repository, number, token: "closed")
    assert main(["--page", str(page)]) == expected
    assert capsys.readouterr().out.count("\n") == (0 if expected == 0 else 2)


def test_main_exits_2_when_github_cannot_be_read(tmp_path, monkeypatch, capsys):
    page = tmp_path / "debt-overview.md"
    page.write_text(LISTS + EPIC, encoding="utf-8")

    def unreachable(token):
        raise debt_overview_check.CheckError("GitHub answered 503")

    monkeypatch.setattr(debt_overview_check, "fetch_open_issues", unreachable)
    assert main(["--page", str(page)]) == 2
    assert "503" in capsys.readouterr().err
