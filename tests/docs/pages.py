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
"""
The pages of this repository and the checks the page rules need (CONTRIBUTING.md § Writing documentation).
Each check takes page text and returns one message per problem, each naming the page, so a test can also plant
a violation in a synthetic page and see it reported.

The parser is living-doc-generator-markdown's tests/docs/pages.py, hand-written, with no Markdown library.
"""

from __future__ import annotations

import re
import subprocess
from collections import deque
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parents[2]

# Every page with `## Purpose` then `## Contents`; a new page is added here and linked within three links of
# README.md.
PAGES: tuple[str, ...] = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/introduction/what-is-living-documentation.md",
    "docs/introduction/architecture.md",
    "docs/introduction/quickstart.md",
    "docs/introduction/principles.md",
    "docs/guides/build-a-pipeline.md",
    "docs/guides/choosing-a-documentation-source.md",
    "docs/guides/authoring-documentation.md",
    "docs/guides/github-collection.md",
    "docs/guides/azure-devops-collection.md",
    "docs/guides/living-doc-document-types.md",
    "docs/tutorials/gh-source-to-markdown.md",
    "docs/tutorials/gh-issues-to-markdown.md",
    "docs/tutorials/technical-project-to-pdf.md",
    "docs/tutorials/ado-workitems-to-markdown.md",
    "docs/tutorials/gh-source-to-pdf.md",
    "docs/reference/glossary.md",
    "docs/reference/authoring-formats.md",
    "docs/reference/rendering-rules.md",
    "docs/reference/data-flows.md",
    "docs/reference/contracts.md",
    "docs/reference/errors.md",
    "docs/examples/README.md",
    "docs/_integration/README.md",
    "docs/_archive/decisions.md",
    "docs/_backlog/debt-overview.md",
)

# The pages whose anchors are search keys, not a description of code, so they may carry `path::symbol`.
ANCHOR_PAGES: tuple[str, ...] = ("docs/_backlog/debt-overview.md",)

# The project cards: `## Purpose`, no `## Contents`, at most CARD_MAX_LINES lines.
CARDS: tuple[str, ...] = (
    "docs/projects/agentic.md",
    "docs/projects/collector-gh.md",
    "docs/projects/collector-ad.md",
    "docs/projects/toolkit.md",
    "docs/projects/utilities.md",
    "docs/projects/generator-markdown.md",
    "docs/projects/generator-pdf.md",
)
CARD_MAX_LINES = 25

# Each moved or merged page and the page it now points to: `# Title`, a blank line, one `Moved to` line.
REDIRECTS: dict[str, str] = {
    "docs/guides/living-doc-glossary.md": "docs/reference/glossary.md",
    "docs/guides/living-doc-header-types.md": "docs/reference/authoring-formats.md",
    "docs/guides/getting-started.md": "docs/guides/build-a-pipeline.md",
    "docs/guides/choosing-a-generator.md": "docs/guides/build-a-pipeline.md",
    "docs/projects/agentic-toolkit.md": "docs/projects/agentic.md",
}

# The pages that stay conceptual (levels L0 and L1): no YAML block.
CONCEPT_PAGES: tuple[str, ...] = tuple(
    page for page in PAGES if page == "README.md" or page.startswith("docs/introduction/")
)

# Every page lies within this many links of README.md; a redirect is exempt.
MAX_LINKS_FROM_README = 3

# Tracked Markdown that is not a page: the agentic setup and layer, the CI files, the private notes' README, the
# tests' own pages, the mined corpus inputs and every gate's or milestone's run folder.
NOT_PAGES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".claude/",
    ".github/",
    ".local_context/",
    "agentic/",
    "tests/",
    "docs/examples/gh-issues/",
)
NOT_PAGE_PATTERNS: tuple[str, ...] = ("docs/_integration/*/*",)

# A fence may sit in a list item or a blockquote, so `>` markers, list markers and indentation may precede it.
_LIST_MARKER = r"(?:[-*+]|\d{1,9}[.)])"
_CONTAINER_PREFIX = rf"(?:[ \t]*(?:>|{_LIST_MARKER}(?=[ \t])))*[ \t]*"
_FENCE_RE = re.compile(rf"^(?P<prefix>{_CONTAINER_PREFIX})(?P<fence>`{{3,}}|~{{3,}})(?P<info>.*)$")
_FENCE_RUN_RE = re.compile(r"`{3,}|~{3,}")
_QUOTES_RE = re.compile(r"^(?:[ \t]*>)*")
_LIST_MARKER_RE = re.compile(_LIST_MARKER)
# A list item's first line; `lead` runs to the column its content starts at.
_LIST_ITEM_START_RE = re.compile(rf"^(?P<lead>[ \t]*{_LIST_MARKER}[ \t]{{1,4}})\S")
# A code span: an exact run of backticks closed by the same run, across line breaks but not across a blank line.
_CODE_SPAN = r"(?<!`)(?P<ticks>`+)(?:(?!\n[ \t]*\n).)+?(?<!`)(?P=ticks)(?!`)"
_CODE_SPAN_RE = re.compile(_CODE_SPAN, re.S)
_COMMENT_MARK_RE = re.compile(r"<!--|-->")
# One left-to-right pass, so `<!--` inside a code span is text, not the start of a comment.
_CODE_SPAN_OR_COMMENT_RE = re.compile(rf"(?P<span>{_CODE_SPAN})|<!--.*?-->", re.S)

# The file kinds a `path::symbol` anchor may point into, and the anchor itself. A trailing `()` or pytest `[id]` is
# allowed and not part of the symbol.
FILE_TYPES = "py|md|yml|yaml|toml|sh|txt|json|example|cfg|ini|feature|ts"
_ANCHOR_PATH = rf"(?:[\w.-]+/)*(?:[\w-][\w.-]*\.(?:{FILE_TYPES})|Makefile|\.[\w-][\w.-]*)"
_ANCHOR_SYMBOL = r"[\w.-]*\w"
_ANCHOR_SUFFIX = r"(?:\(\)|\[[^\]\s]*\])?"
ANCHOR_RE = re.compile(rf"(?<![\w./<>-])(?P<path>{_ANCHOR_PATH})::(?P<symbol>{_ANCHOR_SYMBOL}){_ANCHOR_SUFFIX}")

_HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.*?)\s*#*\s*$")
_LIST_LINK_RE = re.compile(r"^[-*]\s+\[[^\]]*\]\((?P<target>[^)\s]*)\)\s*$")
# An inline link's destination, bare or in angle brackets, with its optional title.
_LINK_TARGET_RE = re.compile(r"""\]\(<?(?P<target>[^)\s>]+)>?(?:\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?\s*\)""")
_REFERENCE_DEFINITION_RE = re.compile(r"^ {0,3}\[(?P<label>[^\]]+)\]:[ \t]*<?(?P<target>[^\s>]+)>?.*$", re.M)
# A reference link: `[text][label]`, `[label][]` or `[label]`; an inline link's `](` is not one.
_REFERENCE_USE_RE = re.compile(r"\[(?P<text>[^\]]*)\](?:\[(?P<label>[^\]]*)\]|(?!\())")
# A redirect's one line: ``Moved to [`<path>`](<link>).``
_REDIRECT_LINE_RE = re.compile(r"^Moved to \[`(?P<shown>[^`]+)`\]\((?P<target>[^)\s]+)\)\.$")


class CodeBlock(NamedTuple):
    """One fenced block: its info string (e.g. `yaml`), its code, and the non-blank line right above it."""

    info: str
    code: str
    line_above: str


class _Fence(NamedTuple):
    """An open fence: its run, its `>` depth, its column in its blockquote's content, and its container's content
    column. A closing run may be indented up to three spaces from that column; a line left of it has left the
    container, which ends the block."""

    run: str
    depth: int
    column: int
    container: int


def _fence_open(line: str) -> re.Match[str] | None:
    """The opening-fence match for `line`, or `None` when it is not one: CommonMark forbids a backtick in a
    backtick fence's info string (a tilde fence's info string is unrestricted)."""
    match = _FENCE_RE.match(line)
    if match and match.group("fence")[0] == "`" and "`" in match.group("info"):
        return None
    return match


def _quotes(line: str, depth: int | None = None) -> str:
    """The `>` markers `line` opens with - at most `depth` of them, so a deeper `>` stays code - and the whitespace
    between them."""
    quotes_m = _QUOTES_RE.match(line) if depth is None else re.match(rf"^(?:[ \t]*>){{0,{depth}}}", line)
    return quotes_m.group(0) if quotes_m else ""


def _after_quotes(line: str, depth: int) -> str:
    """`line` after its `depth` `>` markers and the one optional space that follows them."""
    after = line[len(_quotes(line, depth)) :]
    return after[1:] if depth and after.startswith(" ") else after


def _open(fence_m: re.Match[str], list_column: int | None) -> _Fence:
    """The fence an opening-fence match starts; a list marker in its prefix counts as indentation. Its container's
    content column is the list item's it opens or sits in, else the margin, whatever its own indentation."""
    prefix = fence_m.group("prefix")
    depth = _quotes(prefix).count(">")
    inner = _after_quotes(prefix, depth)
    after = _LIST_MARKER_RE.sub(lambda marker_m: " " * len(marker_m.group(0)), inner)
    if after != inner:
        container = len(after)
    elif not depth and list_column is not None and list_column <= len(after):
        container = list_column
    else:
        container = 0
    return _Fence(fence_m.group("fence"), depth, len(after), container)


def _step(line: str, fence: _Fence) -> str:
    """`close` when `line` closes the block, `end` when the block's container ended before `line`, else `code`."""
    if _quotes(line, fence.depth).count(">") < fence.depth:
        return "end"
    after = _after_quotes(line, fence.depth)
    lead = len(after) - len(after.lstrip(" "))
    stripped = after.strip()
    run_m = _FENCE_RUN_RE.fullmatch(stripped)
    if run_m and stripped[0] == fence.run[0] and len(stripped) >= len(fence.run) and lead <= fence.container + 3:
        return "close"
    if stripped and lead < fence.container:
        return "end"
    return "code"


def _code_line(line: str, fence: _Fence) -> str:
    """A line of the block without its container's prefix: the quotes, and indentation up to the fence's column."""
    after = _after_quotes(line, fence.depth)
    return after[min(fence.column, len(after) - len(after.lstrip(" \t"))) :]


def _in_comment_after(line: str, in_comment: bool) -> bool:
    """Whether an HTML comment is still open after `line`, given whether one was open before it; a marker inside a
    code span is text."""
    for mark_m in _COMMENT_MARK_RE.finditer(_CODE_SPAN_RE.sub("", line)):
        if (mark_m.group(0) == "<!--") != in_comment:
            in_comment = not in_comment
    return in_comment


class _Outside:
    """What the lines outside fenced blocks say about the next line: whether an HTML comment is open, and the content
    column of the list item the line may sit in."""

    def __init__(self) -> None:
        self.in_comment = False
        self.list_column: int | None = None
        self.after_blank = False

    def fence(self, line: str) -> re.Match[str] | None:
        """The fence `line` opens, or `None`: none opens inside an HTML comment, and a fence indented four spaces or
        more is indented code unless it sits in a list item's content."""
        fence_m = None if self.in_comment else _fence_open(line)
        if fence_m is None:
            return None
        prefix = fence_m.group("prefix")
        if len(prefix) < 4 or _quotes(prefix) or _LIST_MARKER_RE.search(prefix):
            return fence_m
        column = self.list_column
        return fence_m if column is not None and column <= len(prefix) < column + 4 else None

    def read(self, line: str) -> None:
        """Take in a line outside fenced blocks: a list item opens a list; a heading, or a line indented less than the
        item's content after a blank line, ends it."""
        self.in_comment = _in_comment_after(line, self.in_comment)
        item_m = _LIST_ITEM_START_RE.match(line)
        if item_m:
            self.list_column = len(item_m.group("lead"))
        elif line.strip():
            indent = len(line) - len(line.lstrip(" "))
            if _HEADING_RE.match(line) or (
                self.after_blank and self.list_column is not None and indent < self.list_column
            ):
                self.list_column = None
        self.after_blank = not line.strip()


def read_page(page: str) -> str:
    """The text of a page, read from the repository."""
    return (REPO_ROOT / page).read_text(encoding="utf-8")


def tracked_markdown() -> set[str]:
    """Every Markdown file git tracks - `.md` or `.markdown`, in any case - that is a page: not a `CONTEXT.md`, not
    under a NOT_PAGES prefix and matching no NOT_PAGE_PATTERNS pattern."""
    listed = subprocess.run(
        ["git", "ls-files", "--", ":(icase)*.md", ":(icase)*.markdown"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.splitlines()
    return {
        path
        for path in listed
        if not path.startswith(NOT_PAGES)
        and not any(fnmatch(path, pattern) for pattern in NOT_PAGE_PATTERNS)
        and PurePosixPath(path).name != "CONTEXT.md"
    }


def check_page_list(listed: set[str], known: set[str]) -> list[str]:
    """Every tracked page is on a list, and every listed page is tracked."""
    problems = [f"{page}: a page on no list; add it to PAGES, CARDS or REDIRECTS" for page in sorted(listed - known)]
    problems += [f"{page}: listed but not tracked" for page in sorted(known - listed)]
    return problems


def unfenced_lines(text: str) -> list[str]:
    """The page's lines outside fenced code blocks and HTML comments, so a `#` comment in a code block, or a
    commented-out heading or link, is never read as one."""
    lines: list[str] = []
    fence: _Fence | None = None
    outside = _Outside()
    for line in text.splitlines():
        if fence is not None:
            step = _step(line, fence)
            if step != "end":
                fence = None if step == "close" else fence
                continue
            fence = None
        fence_m = outside.fence(line)
        if fence_m:
            fence = _open(fence_m, outside.list_column)
            continue
        lines.append(line)
        outside.read(line)
    return _CODE_SPAN_OR_COMMENT_RE.sub(lambda m: m.group("span") or "", "\n".join(lines)).splitlines()


def code_blocks(text: str) -> list[CodeBlock]:
    """Every fenced block of the page, in order; a fence inside an HTML comment, or indented code that looks like a
    fence, is not rendered as one, so it is no block."""
    blocks: list[CodeBlock] = []
    lines = text.splitlines()
    index = 0
    outside = _Outside()
    while index < len(lines):
        fence_m = outside.fence(lines[index])
        if fence_m is None:
            outside.read(lines[index])
            index += 1
            continue
        fence = _open(fence_m, outside.list_column)
        above = next((line.strip() for line in reversed(lines[:index]) if line.strip()), "")
        body: list[str] = []
        index += 1
        step = "code"
        while index < len(lines) and (step := _step(lines[index], fence)) == "code":
            body.append(_code_line(lines[index], fence))
            index += 1
        blocks.append(CodeBlock(fence_m.group("info").strip(), "\n".join(body) + "\n", above))
        if step == "close":
            index += 1  # a block its container ended leaves that line to be read again
    return blocks


def all_headings(text: str) -> list[tuple[int, str]]:
    """`(level, text)` of every heading outside fenced blocks, in page order."""
    found = []
    for line in unfenced_lines(text):
        heading_m = _HEADING_RE.match(line)
        if heading_m:
            found.append((len(heading_m.group("hashes")), heading_m.group("text")))
    return found


def headings(text: str, level: int) -> list[str]:
    """The text of every heading of exactly `level` (2 for `##`) outside fenced blocks."""
    return [title for heading_level, title in all_headings(text) if heading_level == level]


def slug(heading: str) -> str:
    """The fragment GitHub gives a heading: emphasis and code markers dropped, lowercased, punctuation removed,
    each space a hyphen."""
    rendered = heading.replace("`", "").replace("**", "").lower()
    kept = "".join(char for char in rendered if char.isalnum() or char in " -_")
    return kept.replace(" ", "-")


def _unique_fragments(titles: list[str]) -> list[tuple[str, str]]:
    """`(fragment, title)` per title, GitHub's way: a candidate already used - literal or itself generated -
    gets `-1`, `-2`, ... appended until it is unused."""
    used: set[str] = set()
    fragments: list[tuple[str, str]] = []
    for title in titles:
        base = slug(title)
        candidate, suffix = base, 0
        while candidate in used:
            suffix += 1
            candidate = f"{base}-{suffix}"
        used.add(candidate)
        fragments.append((candidate, title))
    return fragments


def section(text: str, title: str) -> list[str]:
    """The lines under the `## <title>` heading, up to the next `##` heading."""
    body: list[str] = []
    inside = False
    for line in unfenced_lines(text):
        heading_m = _HEADING_RE.match(line)
        if heading_m and len(heading_m.group("hashes")) == 2:
            inside = heading_m.group("text") == title
            continue
        if inside:
            body.append(line)
    return body


def check_purpose_then_contents(page: str, text: str) -> list[str]:
    """The page opens with its `#` title, then `## Purpose`, then `## Contents`: no heading comes between them."""
    opening = all_headings(text)[:3]
    if opening[:1] and opening[0][0] == 1 and opening[1:] == [(2, "Purpose"), (2, "Contents")]:
        return []
    found = [f"{'#' * level} {title}" for level, title in opening]
    return [f"{page}: the page must open with '# <title>', '## Purpose', '## Contents'; found {found!r}"]


def check_contents_links(page: str, text: str) -> list[str]:
    """`Contents` links to every other `##` chapter of the page, and to nothing else. GitHub numbers a repeated
    fragment across headings of every level, so every heading takes part in the numbering."""
    every = all_headings(text)
    chapters = {
        fragment: title
        for (fragment, title), (level, _) in zip(_unique_fragments([title for _, title in every]), every, strict=True)
        if level == 2 and title not in ("Purpose", "Contents")
    }
    problems: list[str] = []
    linked: set[str] = set()
    for line in section(text, "Contents"):
        if not line.strip():
            continue
        link_m = _LIST_LINK_RE.match(line.strip())
        if link_m is None or not link_m.group("target").startswith("#"):
            problems.append(f"{page}: 'Contents' may hold only '- [title](#chapter)' lines; found {line.strip()!r}")
            continue
        fragment = link_m.group("target")[1:]
        if fragment not in chapters:
            problems.append(f"{page}: 'Contents' links to '#{fragment}', which is no '##' chapter of the page")
        linked.add(fragment)
    for fragment, title in chapters.items():
        if fragment not in linked:
            problems.append(f"{page}: chapter '## {title}' is missing from 'Contents'")
    return problems


def check_card(page: str, text: str) -> list[str]:
    """A project card is its `#` title and `## Purpose`, nothing more: no `## Contents`, no other chapter, no table
    (an input table belongs to the repository's own pages), and at most CARD_MAX_LINES lines."""
    problems: list[str] = []
    every = all_headings(text)
    opening = every[:2]
    if not (opening[:1] and opening[0][0] == 1 and opening[1:] == [(2, "Purpose")]):
        found = [f"{'#' * level} {title}" for level, title in opening]
        problems.append(f"{page}: a card must open with '# <title>', '## Purpose'; found {found!r}")
    elif "Contents" in headings(text, 2):
        problems.append(f"{page}: a card has no '## Contents'")
    elif every[2:]:
        found = [f"{'#' * level} {title}" for level, title in every[2:]]
        problems.append(f"{page}: a card has no chapter but '## Purpose'; found {found!r}")
    if any(line.lstrip().startswith("|") for line in unfenced_lines(text)):
        problems.append(f"{page}: a card has no table")
    lines = len(text.splitlines())
    if lines > CARD_MAX_LINES:
        problems.append(f"{page}: a card has at most {CARD_MAX_LINES} lines; found {lines}")
    return problems


def check_redirect(page: str, text: str, target: str) -> list[str]:
    """A redirect is `# Title`, a blank line and one ``Moved to [`<target>`](<link>).`` line, whose link resolves to
    `target`, and nothing else."""
    lines = text.splitlines()
    line_m = _REDIRECT_LINE_RE.match(lines[2]) if len(lines) == 3 else None
    if not (line_m and _HEADING_RE.match(lines[0]) and lines[0].startswith("# ") and lines[1] == ""):
        return [f"{page}: a redirect is '# <title>', a blank line and one 'Moved to [`<path>`](<link>).' line"]
    if line_m.group("shown") != target or _resolve(page, line_m.group("target")) != target:
        return [f"{page}: the redirect must name and link {target}; found {lines[2]!r}"]
    return []


def _link_targets(prose: str) -> list[str]:
    """Every link destination of the page's prose: inline links, and the reference definitions a link uses; a
    definition nothing uses renders nothing."""
    definitions = {_label(m.group("label")): m.group("target") for m in _REFERENCE_DEFINITION_RE.finditer(prose)}
    body = _REFERENCE_DEFINITION_RE.sub("", prose)
    used = [_label(m.group("label") or m.group("text")) for m in _REFERENCE_USE_RE.finditer(body)]
    return [m.group("target") for m in _LINK_TARGET_RE.finditer(body)] + [
        definitions[label] for label in used if label in definitions
    ]


def _label(label: str) -> str:
    """A reference label as Markdown matches it: in any case, with runs of whitespace collapsed."""
    return " ".join(label.split()).casefold()


def _resolve(page: str, target: str) -> str | None:
    """A relative link of `page` as a repository path without its fragment; `None` for an absolute URL, a bare
    fragment, or a path that leaves the repository."""
    target = target.split("#", 1)[0]
    if not target or "://" in target or target.startswith("mailto:"):
        return None
    parts: list[str] = []
    for part in (PurePosixPath(page).parent / target).parts:
        if part == "..":
            if not parts:
                return None
            parts.pop()
        elif part != ".":
            parts.append(part)
    return "/".join(parts)


def _resolved_links(page: str, text: str) -> set[str]:
    """Every relative link of the page into the repository, as a repository path without its fragment. A link
    inside a fenced code block, an HTML comment or a code span does not count - GitHub renders no link there."""
    targets = _link_targets(_CODE_SPAN_RE.sub("", "\n".join(unfenced_lines(text))))
    return {path for path in (_resolve(page, target) for target in targets) if path}


def links_from_readme(pages: dict[str, str], dead_ends: set[str] | None = None) -> dict[str, int]:
    """The fewest links from `README.md` to each page it reaches, breadth-first over the relative links between
    the pages given; the walk reaches a dead end (a redirect) but never follows its links."""
    distance = {"README.md": 0}
    queue = deque(["README.md"])
    while queue:
        page = queue.popleft()
        if page in (dead_ends or set()):
            continue
        for linked in sorted(_resolved_links(page, pages[page])):
            if linked in pages and linked not in distance:
                distance[linked] = distance[page] + 1
                queue.append(linked)
    return distance


def check_reachable(pages: dict[str, str], exempt: set[str]) -> list[str]:
    """Every page but `README.md` and the exempt ones is within MAX_LINKS_FROM_README links of `README.md`."""
    distance = links_from_readme(pages, dead_ends=exempt)
    problems = []
    for page in sorted(set(pages) - exempt - {"README.md"}):
        if page not in distance:
            problems.append(f"{page}: not reachable from README.md")
        elif distance[page] > MAX_LINKS_FROM_README:
            problems.append(
                f"{page}: {distance[page]} links from README.md; at most {MAX_LINKS_FROM_README} are allowed"
            )
    return problems


def check_no_link_to_redirect(pages: dict[str, str], redirects: dict[str, str]) -> list[str]:
    """No page links a redirect: it links the page the redirect points to. A redirect is there for links from
    other repositories."""
    return [
        f"{page}: links the redirect {linked}; link {redirects[linked]}"
        for page in sorted(set(pages) - set(redirects))
        for linked in sorted(_resolved_links(page, pages[page]) & set(redirects))
    ]


def check_no_anchor(page: str, text: str) -> list[str]:
    """The page carries no `path::symbol` anchor outside its code blocks: the code a page describes is found from
    the `CONTEXT.md` beside it, never from the page."""
    return [
        f"{page}: carries the anchor '{anchor_m.group(0)}'; pages carry no path::symbol"
        for anchor_m in ANCHOR_RE.finditer("\n".join(unfenced_lines(text)))
    ]


def check_no_yaml_block(page: str, text: str) -> list[str]:
    """A conceptual page (README.md, docs/introduction/) shows no YAML block: workflows belong to the guides and
    tutorials."""
    return [
        f"{page}: a conceptual page shows no YAML block; found one after {block.line_above!r}"
        for block in code_blocks(text)
        if block.info.lower().split(maxsplit=1)[:1] in (["yaml"], ["yml"])
    ]


def path_filter_matches(pattern: str, path: str) -> bool:
    """Whether a GitHub Actions `paths` pattern matches `path`: `**` spans directories, `*` stays inside one. Only
    these two wildcards are supported; any other character, `?` among them, matches itself."""
    parts = re.split(r"(\*\*/?|\*)", pattern)
    wildcards = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*"}
    regex = "".join(wildcards.get(part, re.escape(part)) for part in parts)
    return re.fullmatch(regex, path) is not None
