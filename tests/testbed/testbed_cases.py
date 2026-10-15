#!/usr/bin/env python3
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
"""Problem cases derived from a copy of the testbed's ``core``.

``core`` follows the canon 100 %, so a problem the pipeline must report is never authored in the
testbed: it is derived here, from a copy. A case is a named function that takes the path to a
copy of ``core``, changes it in place and returns what the run over the copy must report: one
warning code, at the line it changed. A case finds what it changes by structure, never by literal
text, so an edit to ``core`` does not break it.

``tests/testbed/run-testbed-stage.sh`` runs every case in ``CASES``: it copies ``core``, applies the
case, makes the copy a git checkout, runs ``doc-source`` over it, and asserts that the run reports
exactly that one warning (``tests/testbed/check_testbed_stage.py case``). A case run is not held to
the invariants of ``core`` itself: what a case breaks can leave other data dangling.

Usage:
    python tests/testbed/testbed_cases.py --list                # the case names, one per line
    python tests/testbed/testbed_cases.py <case> <core-copy>    # applies one; prints
                                                              # "<code>\\t<line>\\t<file>\\t<what changed>"
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator


@dataclass(frozen=True)
class Expected:
    """What the run over a changed copy must report: exactly one warning, ``code``, at ``line``
    (1-based) of ``path``."""

    code: str
    line: int
    path: Path
    # What the case changed, for the run's log.
    change: str


# A Functionality .feature file declares its id in this tag (`@FUNC_ID:FUNC-001`).
_FUNCTIONALITY_TAG_RE = re.compile(r"^\s*@FUNC_ID:\S", re.MULTILINE)
# A header comment line: `#`, then the line's indent and text.
_HEADER_LINE_RE = re.compile(r"^#(?P<indent>[ \t]*)(?P<text>.*?)\r?\n?$")
_AC_HEADER_RE = re.compile(r"^AC:\S+\s*\(")


def _functionality_files(core: Path) -> Iterator[Path]:
    """Every Functionality .feature file under ``core``, in path order."""
    for path in sorted(core.rglob("*.feature")):
        if _FUNCTIONALITY_TAG_RE.search(path.read_text(encoding="utf-8")):
            yield path


def _ac_blocks(lines: list[str]) -> Iterator[list[int]]:
    """The line numbers (0-based) of each acceptance-criterion block in a file's header comment:
    the lines after an ``AC:<id> (…)`` line that sit deeper than it, up to the first shallower
    header line (the next ``AC:`` header, a key at the key level, or a ``# =====`` rule). A blank
    line is layout and ends nothing, as the canon reads it: the block runs past it, never holds it."""
    header = []
    for line in lines:
        if not line.startswith("#"):
            break
        header.append(_HEADER_LINE_RE.match(line))
    index = 0
    while index < len(header):
        match = header[index]
        index += 1
        if not _AC_HEADER_RE.match(match.group("text")):
            continue
        ac_indent = len(match.group("indent"))
        block = []
        while index < len(header):
            line = header[index]
            if line.group("text"):
                if len(line.group("indent")) <= ac_indent:
                    break
                block.append(index)
            index += 1
        yield block


def misindented_ac_line(core: Path) -> Expected:
    """Dedents one line of a multi-line acceptance-criterion block by one space.

    A block's content level is its first bullet's indent, so dedenting the first or only line
    moves the level and reports nothing. The case takes, in the first Functionality file that has
    one, the first block whose last line is a bullet at the content level other than the first:
    one space less, that line fits no level and is reported ``MISINDENTED_LINE`` and dropped. It
    must be the block's last line, because every later line deeper than the dropped one would be
    reported with it.
    """
    for path in _functionality_files(core):
        with open(path, encoding="utf-8", newline="") as handle:
            lines = handle.readlines()
        for block in _ac_blocks(lines):
            bullets = [number for number in block if _HEADER_LINE_RE.match(lines[number]).group("text").startswith("- ")]
            if len(bullets) < 2 or bullets[-1] != block[-1]:
                continue
            content_indent = len(_HEADER_LINE_RE.match(lines[bullets[0]]).group("indent"))
            last = bullets[-1]
            if len(_HEADER_LINE_RE.match(lines[last]).group("indent")) != content_indent:
                continue
            lines[last] = "#" + lines[last][2:]
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.writelines(lines)
            return Expected("MISINDENTED_LINE", last + 1, path,
                            f"line {last + 1} dedented by one space: {lines[last].rstrip()}")
    raise LookupError(f"no Functionality file under {core} has a block whose last line is a non-first bullet")


# Every case, in run order. Further cases only on need.
CASES: dict[str, Callable[[Path], Expected]] = {case.__name__: case for case in (misindented_ac_line,)}


def main(argv: list[str]) -> int:
    if argv == ["--list"]:
        print("\n".join(CASES))
        return 0
    if len(argv) != 2 or argv[0] not in CASES:
        print(f"usage: testbed_cases.py --list | <case> <core-copy>; cases: {', '.join(CASES)}", file=sys.stderr)
        return 2
    expected = CASES[argv[0]](Path(argv[1]))
    print(f"{expected.code}\t{expected.line}\t{expected.path.as_posix()}\t{expected.change}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
