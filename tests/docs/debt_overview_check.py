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
"""Compare docs/_backlog/debt-overview.md with the open tech-debt and epic issues of the seven repositories.

Reads the page, then through the GitHub REST API the open issues carrying any of the four labels in each repository
(both spellings: ``type:tech-debt``/``type:epic`` and ``tech debt``/``epic``), and each issue a row names that is not
among them. Prints one line per finding:

- an open tech-debt or epic issue without a row;
- a row whose issue is closed, is open but no longer labelled tech debt or epic, or does not exist;
- a topic or wake tag on neither of the page's lists;
- a duplicate row, or a row out of order (rows are sorted by repository, then number);
- a row that is not four cells with its issue's link, or names a repository outside the seven.

Usage:
    python tests/docs/debt_overview_check.py [--page PATH]

Reads ``GITHUB_TOKEN``, else ``GH_TOKEN``, when set; without one GitHub allows 60 requests an hour. Exit codes: 0 no
finding, 1 a finding, 2 the page or GitHub cannot be read.
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from pages import section

PAGE = Path(__file__).resolve().parents[2] / "docs" / "_backlog" / "debt-overview.md"
OWNER = "AbsaOSS"
REPOSITORIES = (
    "living-doc",
    "living-doc-utilities",
    "living-doc-collector-gh",
    "living-doc-collector-ad",
    "living-doc-toolkit",
    "living-doc-generator-markdown",
    "living-doc-generator-pdf",
)
LABELS = ("type:tech-debt", "type:epic", "tech debt", "epic")
API = "https://api.github.com"

_LIST_TAG_RE = re.compile(r"^- `(?P<tag>[^`]+)`:")
_CODE_SPAN_RE = re.compile(r"`([^`]+)`")
_LINK_CELL_RE = re.compile(
    rf"^\[(?P<repository>[\w.-]+)#(?P<number>\d+)\]\(https://github\.com/{OWNER}/(?P=repository)/issues/(?P=number)\)$"
)
_NEXT_RE = re.compile(r'<(?P<url>[^>]+)>;\s*rel="next"')
_CELL_SEPARATOR_RE = re.compile(r"(?<!\\)\|")
NO_WAKE = "—"


class CheckError(Exception):
    """The page or GitHub cannot be read."""


class NotFound(CheckError):
    """GitHub knows no such issue."""


@dataclass(frozen=True)
class Row:
    repository: str
    number: int
    topics: tuple[str, ...]
    wake: str | None

    @property
    def ref(self) -> str:
        return f"{self.repository}#{self.number}"


@dataclass
class Page:
    topics: set[str] = field(default_factory=set)
    wakes: set[str] = field(default_factory=set)
    rows: list[Row] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


def _tags(text: str, title: str) -> set[str]:
    """The tags the `## <title>` list defines, one `- `tag`: meaning` line each."""
    return {m.group("tag") for line in section(text, title) if (m := _LIST_TAG_RE.match(line))}


def parse_page(text: str) -> Page:
    """The page's two lists and its table rows; a line of the table that is not a well-formed row is a problem."""
    page = Page(topics=_tags(text, "Topics"), wakes=_tags(text, "Wakes on"))
    in_table = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            in_table = line == "## Open debt"
            continue
        if not in_table or not line.startswith("|") or line.startswith(("| Issue |", "|---")):
            continue
        cells = [cell.strip() for cell in _CELL_SEPARATOR_RE.split(line.strip().strip("|"))]
        link_m = _LINK_CELL_RE.match(cells[0]) if len(cells) == 4 else None
        wake_tags = _CODE_SPAN_RE.findall(cells[3]) if link_m else []
        if not link_m or not (cells[3] == NO_WAKE or (len(wake_tags) == 1 and cells[3] == f"`{wake_tags[0]}`")):
            page.problems.append(f"line {line_no}: not a row of four cells with its issue's link: {line.strip()!r}")
            continue
        page.rows.append(
            Row(
                link_m.group("repository"),
                int(link_m.group("number")),
                tuple(_CODE_SPAN_RE.findall(cells[1])),
                wake_tags[0] if wake_tags else None,
            )
        )
    return page


def findings(page: Page, open_issues: set[tuple[str, int]], state_of: Callable[[str, int], str]) -> list[str]:
    """One line per finding. `open_issues` holds every open tech-debt or epic issue; `state_of` gives `closed`, `open`
    or `missing` for an issue outside it."""
    found = list(page.problems)
    seen: set[tuple[str, int]] = set()
    previous: tuple[str, int] | None = None
    for row in page.rows:
        key = (row.repository, row.number)
        if previous is not None and key < previous:
            found.append(f"{row.ref}: row out of order; rows are sorted by repository, then number")
        previous = key
        if row.repository not in REPOSITORIES:
            found.append(f"{row.ref}: not one of the seven repositories")
            continue
        if key in seen:
            found.append(f"{row.ref}: duplicate row")
            continue
        seen.add(key)
        found += [f"{row.ref}: topic `{tag}` is not on the Topics list" for tag in row.topics if tag not in page.topics]
        if row.wake is not None and row.wake not in page.wakes:
            found.append(f"{row.ref}: wake tag `{row.wake}` is not on the Wakes on list")
        if key not in open_issues:
            state = state_of(*key)
            found.append(
                f"{row.ref}: row whose issue "
                + {"closed": "is closed", "open": "is no longer labelled tech debt or epic"}.get(state, "does not exist")
            )
    found += [
        f"{repository}#{number}: open tech-debt or epic issue without a row"
        for repository, number in sorted(open_issues - seen)
    ]
    return found


def next_link(header: str | None) -> str | None:
    """The `rel="next"` URL of a `Link` header, or `None` on the last page."""
    next_m = _NEXT_RE.search(header or "")
    return next_m.group("url") if next_m else None


def _get(url: str, token: str | None) -> tuple[object, str | None]:
    """The decoded JSON at `url` and its `Link` header; NotFound for a 404 or 410, CheckError for any other failure."""
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
            return json.load(response), response.headers.get("Link")
    except urllib.error.HTTPError as error:
        raise (NotFound if error.code in (404, 410) else CheckError)(f"{url}: HTTP {error.code}") from error
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, ValueError) as error:
        raise CheckError(f"{url}: {error}") from error


def fetch_open_issues(token: str | None) -> set[tuple[str, int]]:
    """Every open issue, not a pull request, carrying one of LABELS in one of REPOSITORIES."""
    issues: set[tuple[str, int]] = set()
    for repository in REPOSITORIES:
        for label in LABELS:
            query = urllib.parse.urlencode({"state": "open", "labels": label, "per_page": 100})
            url: str | None = f"{API}/repos/{OWNER}/{repository}/issues?{query}"
            while url:
                items, link = _get(url, token)
                if not isinstance(items, list):
                    raise CheckError(f"{url}: expected a list of issues, got {items!r}")
                issues |= {(repository, item["number"]) for item in items if "pull_request" not in item}
                url = next_link(link)
    return issues


def fetch_state(repository: str, number: int, token: str | None) -> str:
    """`closed`, `open` or `missing` (no such issue, or a pull request) for one issue."""
    url = f"{API}/repos/{OWNER}/{repository}/issues/{number}"
    try:
        item, _ = _get(url, token)
    except NotFound:
        return "missing"
    if not isinstance(item, dict) or item.get("state") not in ("open", "closed"):
        raise CheckError(f"{url}: expected an issue, got {item!r}")
    return "missing" if "pull_request" in item else item["state"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--page", type=Path, default=PAGE, help="the overview page (default: %(default)s)")
    args = parser.parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    try:
        page = parse_page(args.page.read_text(encoding="utf-8"))
        open_issues = fetch_open_issues(token)
        found = findings(page, open_issues, lambda repository, number: fetch_state(repository, number, token))
    except (OSError, CheckError) as error:
        print(f"debt_overview_check: {error}", file=sys.stderr)
        return 2
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
