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
"""The page rules of CONTRIBUTING.md § Writing documentation, over this repository's pages.

Run: ``python -m pytest tests/docs -q`` (needs pytest, PyYAML and git). Each rule is checked over the real pages,
then planted in a synthetic page to show it fails. Nothing goes online.
"""

from __future__ import annotations

import pytest
import yaml

from pages import (
    CARD_MAX_LINES,
    CARDS,
    CONCEPT_PAGES,
    PAGES,
    REDIRECTS,
    REPO_ROOT,
    check_card,
    check_contents_links,
    check_no_anchor,
    check_no_link_to_redirect,
    check_no_yaml_block,
    check_page_list,
    check_purpose_then_contents,
    check_reachable,
    check_redirect,
    headings,
    links_from_readme,
    path_filter_matches,
    read_page,
    tracked_markdown,
)

EVERY_PAGE = (*PAGES, *CARDS, *REDIRECTS)
EXAMPLES_CHECK = REPO_ROOT / ".github" / "workflows" / "examples-check.yml"

_GOOD_PAGE = """# Title

## Purpose

This page is a sample.

## Contents

- [Facts](#facts)

## Facts

- a fact
"""

_GOOD_CARD = """# living-doc-sample

## Purpose

This page is the card of `living-doc-sample`.

- **Role:** a sample
"""


def _workflow_paths(event: str) -> list[str]:
    """The `paths` filter of `examples-check.yml` for one event; YAML 1.1 reads the `on` key as `True`."""
    workflow = yaml.safe_load(EXAMPLES_CHECK.read_text(encoding="utf-8"))
    triggers = workflow.get("on", workflow.get(True))
    return triggers[event]["paths"]


# --- The page list -------------------------------------------------------------------------------------------------


def test_the_lists_hold_every_tracked_page_and_nothing_else():
    """Every tracked page is on exactly one list, and every listed page is tracked."""
    assert len(EVERY_PAGE) == len(set(EVERY_PAGE))
    assert check_page_list(tracked_markdown(), set(EVERY_PAGE)) == []


def test_planted_page_list_violations_are_reported_naming_the_page():
    """A tracked page on no list, and a listed page git does not track, each fail."""
    assert check_page_list({"README.md", "docs/guides/new.md"}, {"README.md", "docs/guides/gone.md"}) == [
        "docs/guides/new.md: a page on no list; add it to PAGES, CARDS or REDIRECTS",
        "docs/guides/gone.md: listed but not tracked",
    ]


def test_the_skipped_markdown_is_no_page():
    """The agentic setup and layer, the tests' pages, the mined corpus inputs, the run folders and every
    CONTEXT.md are tracked Markdown, not pages."""
    listed = tracked_markdown()
    for skipped in (
        "AGENTS.md",
        "CONTEXT.md",
        "docs/CONTEXT.md",
        ".local_context/README.md",
        ".github/pull_request_template.md",
        "agentic/README.md",
        "tests/README.md",
        "docs/examples/gh-issues/us-001-customer-login.md",
        "docs/_integration/MS1/report.md",
    ):
        assert skipped not in listed
    assert "docs/_integration/README.md" in listed


# --- Purpose, then Contents ----------------------------------------------------------------------------------------


@pytest.mark.parametrize("page", PAGES)
def test_page_opens_with_purpose_then_contents(page):
    """The page's first `##` heading is `Purpose` and its second is `Contents`."""
    assert check_purpose_then_contents(page, read_page(page)) == []


@pytest.mark.parametrize("page", PAGES)
def test_contents_links_every_chapter_and_nothing_else(page):
    """Every `Contents` link resolves to a `##` chapter of the same page, and every chapter is listed."""
    assert check_contents_links(page, read_page(page)) == []


def test_a_well_formed_page_passes_every_check():
    """The synthetic page the planted-violation tests start from is itself clean."""
    assert check_purpose_then_contents("docs/x.md", _GOOD_PAGE) == []
    assert check_contents_links("docs/x.md", _GOOD_PAGE) == []


def test_planted_missing_purpose_is_reported_naming_the_page():
    """A page without `## Purpose` fails, and the message names the page."""
    page = _GOOD_PAGE.replace("## Purpose\n\nThis page is a sample.\n\n", "")
    assert check_purpose_then_contents("docs/x.md", page) == [
        "docs/x.md: the page must open with '# <title>', '## Purpose', '## Contents'; "
        "found ['# Title', '## Contents', '## Facts']"
    ]


def test_planted_wrong_order_is_reported_naming_the_page():
    """`Contents` before `Purpose` fails."""
    page = "# Title\n\n## Contents\n\n- [Purpose](#purpose)\n\n## Purpose\n\nText.\n"
    assert check_purpose_then_contents("docs/x.md", page) == [
        "docs/x.md: the page must open with '# <title>', '## Purpose', '## Contents'; "
        "found ['# Title', '## Contents', '## Purpose']"
    ]


def test_planted_heading_before_purpose_is_reported():
    """A `###` section between the title and `## Purpose` means the page does not open with its Purpose."""
    page = _GOOD_PAGE.replace("## Purpose", "Intro.\n\n### Quick start\n\nText.\n\n## Purpose")
    assert check_purpose_then_contents("docs/x.md", page) == [
        "docs/x.md: the page must open with '# <title>', '## Purpose', '## Contents'; "
        "found ['# Title', '### Quick start', '## Purpose']"
    ]


def test_planted_missing_title_is_reported():
    """A page that starts at `## Purpose`, with no `#` title, fails."""
    page = _GOOD_PAGE.replace("# Title\n\n", "")
    assert check_purpose_then_contents("docs/x.md", page) == [
        "docs/x.md: the page must open with '# <title>', '## Purpose', '## Contents'; "
        "found ['## Purpose', '## Contents', '## Facts']"
    ]


def test_badges_and_a_comment_between_title_and_purpose_are_allowed():
    """Badge lines and an HTML comment are no heading, so the page still opens with its Purpose."""
    page = _GOOD_PAGE.replace(
        "## Purpose", "![Status](https://img.shields.io/badge/x-y-blue)\n\n<!-- ## Draft -->\n\n## Purpose"
    )
    assert check_purpose_then_contents("docs/x.md", page) == []


def test_planted_dead_contents_link_is_reported_naming_the_page():
    """A `Contents` link to a chapter the page does not have fails, as does the chapter it leaves out."""
    page = _GOOD_PAGE.replace("- [Facts](#facts)", "- [Facts](#fact-list)")
    assert check_contents_links("docs/x.md", page) == [
        "docs/x.md: 'Contents' links to '#fact-list', which is no '##' chapter of the page",
        "docs/x.md: chapter '## Facts' is missing from 'Contents'",
    ]


def test_planted_contents_line_that_is_not_a_chapter_link_is_reported():
    """`Contents` holds only chapter links; prose or an outside link fails."""
    page = _GOOD_PAGE.replace("- [Facts](#facts)", "- [Facts](#facts)\n- [Elsewhere](other.md)")
    assert check_contents_links("docs/x.md", page) == [
        "docs/x.md: 'Contents' may hold only '- [title](#chapter)' lines; found '- [Elsewhere](other.md)'"
    ]


def test_a_second_chapter_with_the_same_title_needs_its_own_contents_entry():
    """GitHub gives a repeated `## Facts` the fragment `#facts-1`; `Contents` must link that too, not just `#facts`."""
    page = "# Title\n\n## Purpose\n\nText.\n\n## Contents\n\n- [Facts](#facts)\n\n## Facts\n\n- a\n\n## Facts\n\n- b\n"
    assert check_contents_links("docs/x.md", page) == ["docs/x.md: chapter '## Facts' is missing from 'Contents'"]


def test_a_subsection_takes_part_in_the_fragment_numbering():
    """GitHub numbers repeated fragments across every heading level: after a `### Usage`, the chapter `## Usage` is
    `#usage-1`, and `#usage` lands on the subsection."""
    page = (
        "# Title\n\n## Purpose\n\nText.\n\n## Contents\n\n- [Activation](#activation)\n- [Usage](#usage)\n\n"
        "## Activation\n\n### Usage\n\nText.\n\n## Usage\n\nText.\n"
    )
    assert check_contents_links("docs/x.md", page) == [
        "docs/x.md: 'Contents' links to '#usage', which is no '##' chapter of the page",
        "docs/x.md: chapter '## Usage' is missing from 'Contents'",
    ]
    assert check_contents_links("docs/x.md", page.replace("](#usage)", "](#usage-1)")) == []


def test_a_commented_out_heading_is_not_a_chapter():
    """A `##` line inside a multi-line HTML comment renders as nothing, so `Contents` need not link it."""
    page = _GOOD_PAGE + "\n<!--\n## Old\n\nRetired text.\n-->\n"
    assert check_contents_links("docs/x.md", page) == []


def test_a_comment_marker_inside_a_code_span_is_text():
    """`` `<!--` `` and a later `` `-->` `` are code on GitHub, not a comment, so the headings between them stay."""
    page = _GOOD_PAGE.replace("This page is a sample", "Write `<!--` to open one. This page is a sample") + (
        "\n## More\n\nClose it with `-->`.\n"
    )
    assert check_purpose_then_contents("docs/x.md", page) == []
    assert check_contents_links("docs/x.md", page) == ["docs/x.md: chapter '## More' is missing from 'Contents'"]


def test_emphasis_in_a_heading_is_dropped_from_its_fragment():
    """`## **Branch Naming**` is `#branch-naming` on GitHub, so `Contents` links it by that fragment."""
    page = (
        "# Title\n\n## Purpose\n\nText.\n\n## Contents\n\n- [Branch Naming](#branch-naming)\n\n## **Branch Naming**\n"
    )
    assert check_contents_links("docs/x.md", page) == []


def test_a_comment_line_in_a_code_block_is_no_heading():
    """A `# preconditions:` line inside a fenced header example is code, not a chapter."""
    page = _GOOD_PAGE + "\n```gherkin\n# preconditions:\n## not a chapter\n```\n"
    assert headings(page, 2) == ["Purpose", "Contents", "Facts"]


def test_a_backtick_in_a_backtick_fence_info_string_does_not_open_a_fence():
    """A backtick in a backtick-fence info string leaves the following heading visible to the parser."""
    page = "# Title\n\n```bad`info\n## Actually A Heading\n```\n"
    assert headings(page, 2) == ["Actually A Heading"]


def test_a_run_indented_four_spaces_does_not_close_an_indented_top_level_fence():
    """A closing fence takes at most three spaces, whatever the opener's own indentation; four or more are code."""
    page = "  ```text\n     ```\n## Not a heading\n  ```\n\n## Next\n"
    assert headings(page, 2) == ["Next"]


def test_a_fence_inside_an_html_comment_hides_nothing():
    """A fence in a commented-out block opens no code block, so the headings after the comment are still read."""
    page = "# T\n\n<!--\n```python\nraise SystemExit\n-->\n\n## Visible\n"
    assert headings(page, 2) == ["Visible"]


# --- Project cards -------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("page", CARDS)
def test_card_has_purpose_no_contents_and_fits(page):
    """A project card opens with `## Purpose`, has no `## Contents`, and is at most 25 lines."""
    assert check_card(page, read_page(page)) == []


def test_a_well_formed_card_passes():
    """The synthetic card the planted-violation tests start from is itself clean."""
    assert check_card("docs/projects/x.md", _GOOD_CARD) == []


def test_planted_contents_on_a_card_is_reported():
    """A card that lists its chapters fails: a card has Purpose only."""
    card = _GOOD_CARD.replace("- **Role:**", "## Contents\n\n- [Role](#role)\n\n## Role\n\n- **Role:**")
    assert check_card("docs/projects/x.md", card) == ["docs/projects/x.md: a card has no '## Contents'"]


def test_planted_long_card_is_reported():
    """A card over 25 lines fails, naming its length."""
    card = _GOOD_CARD + "- a line\n" * CARD_MAX_LINES
    assert check_card("docs/projects/x.md", card) == [
        f"docs/projects/x.md: a card has at most {CARD_MAX_LINES} lines; found {CARD_MAX_LINES + 7}"
    ]


def test_planted_chapter_or_table_on_a_card_is_reported():
    """A card is its title and Purpose only: a second chapter, or an input table, fails."""
    card = _GOOD_CARD + "\n## Inputs\n\n| Input | Meaning |\n|---|---|\n| `x` | y |\n"
    assert check_card("docs/projects/x.md", card) == [
        "docs/projects/x.md: a card has no chapter but '## Purpose'; found ['## Inputs']",
        "docs/projects/x.md: a card has no table",
    ]


def test_planted_card_without_purpose_is_reported():
    """A card whose first chapter is not `## Purpose` fails."""
    card = _GOOD_CARD.replace("## Purpose", "## Role")
    assert check_card("docs/projects/x.md", card) == [
        "docs/projects/x.md: a card must open with '# <title>', '## Purpose'; found ['# living-doc-sample', '## Role']"
    ]


# --- Redirects -----------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("page", REDIRECTS)
def test_redirect_is_one_line_to_its_page(page):
    """A moved or merged page is its title and one line naming and linking the page that replaced it."""
    assert check_redirect(page, read_page(page), REDIRECTS[page]) == []


def test_a_redirect_may_link_a_chapter_of_its_page():
    """A fragment on the link lands the reader on the chapter that replaced the page."""
    text = "# Old\n\nMoved to [`docs/guides/new.md`](new.md#a-chapter).\n"
    assert check_redirect("docs/guides/old.md", text, "docs/guides/new.md") == []


def test_planted_redirect_with_content_is_reported():
    """A redirect that keeps a second line of content fails."""
    text = "# Old\n\nMoved to [`docs/guides/new.md`](new.md).\n\nStill here: the old table.\n"
    assert check_redirect("docs/guides/old.md", text, "docs/guides/new.md") == [
        "docs/guides/old.md: a redirect is '# <title>', a blank line and one 'Moved to [`<path>`](<link>).' line"
    ]


def test_planted_redirect_to_another_page_is_reported():
    """A redirect whose link lands elsewhere than the page it names fails."""
    text = "# Old\n\nMoved to [`docs/guides/new.md`](other.md).\n"
    assert check_redirect("docs/guides/old.md", text, "docs/guides/new.md") == [
        "docs/guides/old.md: the redirect must name and link docs/guides/new.md; "
        "found 'Moved to [`docs/guides/new.md`](other.md).'"
    ]


# --- Reachability --------------------------------------------------------------------------------------------------


def test_every_page_is_within_three_links_of_readme():
    """Breadth-first over the relative links between pages, every page but a redirect is at most three links from
    README.md."""
    pages = {page: read_page(page) for page in EVERY_PAGE}
    assert check_reachable(pages, exempt=set(REDIRECTS)) == []


def test_every_reference_page_and_card_is_one_link_from_readme():
    """README.md links each docs/reference/ page and each project card itself."""
    distance = links_from_readme({page: read_page(page) for page in EVERY_PAGE})
    for page in (*CARDS, *(page for page in PAGES if page.startswith("docs/reference/"))):
        assert distance.get(page) == 1, page


def test_planted_deep_and_unreachable_pages_are_reported():
    """A page four links down, and a page no link reaches, each fail."""
    pages = {
        "README.md": "[A](docs/a.md)",
        "docs/a.md": "[B](b.md)",
        "docs/b.md": "[C](c.md)",
        "docs/c.md": "[D](d.md)",
        "docs/d.md": "",
        "docs/e.md": "",
    }
    assert check_reachable(pages, exempt=set()) == [
        "docs/d.md: 4 links from README.md; at most 3 are allowed",
        "docs/e.md: not reachable from README.md",
    ]


def test_a_redirect_is_exempt_from_reachability():
    """No page links a redirect; it is there for links from outside."""
    assert check_reachable({"README.md": "", "docs/old.md": "# Old"}, exempt={"docs/old.md"}) == []


def test_a_page_reached_only_through_a_redirect_is_unreachable():
    """A redirect is a dead end for the walk, so a stale link to it hides no page."""
    pages = {
        "README.md": "[Old](docs/old.md)",
        "docs/old.md": "# Old\n\nMoved to [`docs/a.md`](a.md).\n",
        "docs/a.md": "",
    }
    assert check_reachable(pages, exempt={"docs/old.md"}) == ["docs/a.md: not reachable from README.md"]


def test_no_page_links_a_redirect():
    """Pages link the page a redirect points to, never the redirect."""
    pages = {page: read_page(page) for page in EVERY_PAGE}
    assert check_no_link_to_redirect(pages, REDIRECTS) == []


def test_planted_link_to_a_redirect_is_reported():
    """A page that still links a moved page's old path fails, naming both."""
    pages = {"README.md": "[Start](docs/guides/getting-started.md)", "docs/guides/getting-started.md": ""}
    assert check_no_link_to_redirect(pages, {"docs/guides/getting-started.md": "docs/guides/build-a-pipeline.md"}) == [
        "README.md: links the redirect docs/guides/getting-started.md; link docs/guides/build-a-pipeline.md"
    ]


@pytest.mark.parametrize(
    "readme",
    [
        "```text\n[A](docs/a.md)\n```\n",
        "<!-- [A](docs/a.md) -->\n",
        "`[A](docs/a.md)`\n",
        "[A](https://github.com/AbsaOSS/living-doc/blob/master/docs/a.md)\n",
    ],
    ids=["code-block", "html-comment", "code-span", "absolute-url"],
)
def test_a_link_github_does_not_render_or_that_leaves_the_checkout_does_not_reach(readme):
    """A link in a code block, an HTML comment or a code span renders as none, and an absolute URL reads the
    published branch, not this checkout."""
    assert check_reachable({"README.md": readme, "docs/a.md": ""}, exempt=set()) == [
        "docs/a.md: not reachable from README.md"
    ]


@pytest.mark.parametrize(
    "readme",
    [
        '[A](docs/a.md "A page")\n',
        "[A](<docs/a.md>)\n",
        "[A](docs/a.md#a-chapter)\n",
        "[A][a]\n\n[a]: docs/a.md\n",
        "[a][]\n\n[a]: docs/a.md\n",
        "[a]\n\n[a]: docs/a.md\n",
    ],
    ids=["titled", "angle-brackets", "fragment", "full-reference", "collapsed", "shortcut"],
)
def test_every_markdown_link_form_reaches(readme):
    """A titled, bracketed, fragment or reference-style link renders as a link on GitHub, so it reaches the page."""
    assert check_reachable({"README.md": readme, "docs/a.md": ""}, exempt=set()) == []


def test_a_reference_definition_nothing_uses_does_not_reach():
    """A definition alone renders nothing, so the page it names stays unreached."""
    assert check_reachable({"README.md": "[a]: docs/a.md\n", "docs/a.md": ""}, exempt=set()) == [
        "docs/a.md: not reachable from README.md"
    ]


# --- No anchors, no YAML on a conceptual page ----------------------------------------------------------------------


@pytest.mark.parametrize("page", (*PAGES, *CARDS))
def test_page_carries_no_anchor(page):
    """No page carries a `path::symbol` anchor."""
    assert check_no_anchor(page, read_page(page)) == []


def test_planted_anchor_is_reported_and_one_in_a_code_block_is_not():
    """An anchor in prose fails; the same text inside a fenced example is code."""
    page = _GOOD_PAGE + "\n- parsed by `doc_source/collector.py::GHDocSourceCollector`\n"
    assert check_no_anchor("docs/x.md", page) == [
        "docs/x.md: carries the anchor 'doc_source/collector.py::GHDocSourceCollector'; pages carry no path::symbol"
    ]
    assert check_no_anchor("docs/x.md", _GOOD_PAGE + "\n```text\nmain.py::run\n```\n") == []


@pytest.mark.parametrize("page", CONCEPT_PAGES)
def test_conceptual_page_shows_no_yaml(page):
    """README.md and docs/introduction/ show no YAML block."""
    assert check_no_yaml_block(page, read_page(page)) == []


def test_planted_yaml_block_on_a_conceptual_page_is_reported():
    """A YAML block fails; a Mermaid diagram does not."""
    page = _GOOD_PAGE + "\n```mermaid\nflowchart LR\n```\n\nThe step:\n\n```yaml\n- uses: x\n```\n"
    assert check_no_yaml_block("README.md", page) == [
        "README.md: a conceptual page shows no YAML block; found one after 'The step:'"
    ]
    assert len(check_no_yaml_block("README.md", "```YAML\n- uses: x\n```\n")) == 1


# --- CI runs the check on a page change ----------------------------------------------------------------------------


@pytest.mark.parametrize("event", ["push", "pull_request"])
def test_a_change_of_any_page_runs_the_page_check(event):
    """Every page, card and redirect matches a `paths` filter of examples-check.yml, which runs pytest tests/docs."""
    filters = _workflow_paths(event)
    assert [page for page in EVERY_PAGE if not any(path_filter_matches(f, page) for f in filters)] == []
    assert "python -m pytest tests/docs -q" in EXAMPLES_CHECK.read_text(encoding="utf-8")


def test_planted_unfiltered_page_is_reported():
    """A page under no filter would change without running the check."""
    filters = ["docs/guides/**", "tests/docs/**"]
    assert not any(path_filter_matches(f, "README.md") for f in filters)
    assert path_filter_matches("docs/**", "docs/projects/agentic.md")
    assert not path_filter_matches("docs/*", "docs/projects/agentic.md")


def test_a_path_filter_question_mark_is_not_a_wildcard_here():
    """GitHub reads `?` as "zero or one of the preceding character"; the check supports only `*` and `**`, so a `?`
    matches itself and never widens a filter."""
    assert not path_filter_matches("README.m?", "README.mx")
