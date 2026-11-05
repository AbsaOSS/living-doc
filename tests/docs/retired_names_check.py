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
"""Report every retired artifact, field or command name in living-doc and the pinned components.

Reads the tracked files of each checkout (``git ls-files``: untracked notes, virtual environments and
gitignored planning are never read) and matches every name in ``RETIRED_NAMES`` as a fixed string.
Skipped:

- every ``tests/`` directory and every ``CHANGELOG*`` file, which quote retired names on purpose;
- ``living-doc-collector-gh``'s kept-aside ``doc_issues/``;
- each living-doc file ``tests/docs/retired-names-allow.txt`` lists, one ``<path> <reason>`` line per
  file, with the reason its hit is not a use. An entry that skips no hit is a finding, so a stale entry
  cannot linger.

Usage:
    python tests/docs/retired_names_check.py [--strict] [CHECKOUT ...]

Each CHECKOUT is a git work tree; its repository is named by its ``origin`` remote, else by its
directory. living-doc is this repository's root unless a checkout of it is given. Each hit prints with
its repository, path, line and name. Exit codes: 0 no finding, or findings without ``--strict``; 1 a
finding under ``--strict``; 2 a checkout or the allow-list that cannot be read.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOW_LIST = REPO_ROOT / "tests" / "docs" / "retired-names-allow.txt"
THIS_REPOSITORY = "living-doc"

# Retired names, each matched as written. The canon: living-doc-utilities docs/contracts.md, R3 (no
# `$schema_version` key) and R8 (legacy provenance shapes are retired); the rest are the artifact, field
# and command names the contracts replaced.
RETIRED_NAMES = (
    # artifacts
    "doc-issues.json", "work-items.json", "output/doc-issues",
    # fields
    "content.user_stories", "items[]", '"items"', "meta.audit", "original_metadata", "descoped_at",
    "descoped_reason", "future_release", "meta.view", "$schema_version", "contracts_digest",
    # the toolkit command
    "normalize-issues", "normalize_issues",
)
# Per repository, the paths it keeps aside on purpose.
KEPT_ASIDE = {"living-doc-collector-gh": ("doc_issues/",)}
# `https://github.com/<owner>/<name>[.git]` or `git@github.com:<owner>/<name>[.git]`.
_ORIGIN_RE = re.compile(r"[:/](?P<repository>[^/:]+/[^/]+?)(?:\.git)?/?$")


class CheckError(Exception):
    """A checkout or the allow-list that cannot be read."""


@dataclass(frozen=True)
class Checkout:
    path: Path          # the work tree's top level
    repository: str     # `<owner>/<name>` from `origin`, else the directory name

    @property
    def name(self) -> str:
        return self.repository.rsplit("/", 1)[-1]


@dataclass(frozen=True)
class Hit:
    path: str
    line: int
    name: str


@dataclass(frozen=True)
class Entry:
    line: int           # in the allow-list
    path: str
    reason: str


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True,
                            encoding="utf-8")
    if result.returncode != 0:
        raise CheckError(f"{path}: git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def open_checkout(path: Path) -> Checkout:
    top = Path(_git(path, "rev-parse", "--show-toplevel").strip())
    try:
        origin = _git(top, "remote", "get-url", "origin").strip()
    except CheckError:
        origin = ""
    named = _ORIGIN_RE.search(origin)
    return Checkout(top, named.group("repository") if named else top.name)


def skipped(checkout: Checkout, path: str) -> bool:
    parts = path.split("/")
    return ("tests" in parts[:-1] or parts[-1].startswith("CHANGELOG")
            or path.startswith(KEPT_ASIDE.get(checkout.name, ())))


def hits(checkout: Checkout) -> list[Hit]:
    """Each retired name on each line of the checkout's tracked text files, outside the skipped paths."""
    found: list[Hit] = []
    for path in _git(checkout.path, "ls-files", "-z").split("\0"):
        file = checkout.path / path
        if not path or skipped(checkout, path) or not file.is_file():
            continue        # a file deleted from the work tree, or a submodule
        data = file.read_bytes()
        if b"\0" in data:
            continue        # binary
        for number, line in enumerate(data.decode("utf-8", errors="replace").split("\n"), 1):
            found += [Hit(path, number, name) for name in RETIRED_NAMES if name in line]
    return found


def read_allow_list(path: Path) -> list[Entry]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CheckError(f"cannot read {path}: {exc}") from exc
    entries: list[Entry] = []
    for number, line in enumerate(lines, 1):
        text = line.strip()
        if text and not text.startswith("#"):
            path_, _, reason = text.replace("\t", " ").partition(" ")
            entries.append(Entry(number, path_, reason.strip()))
    return entries


def findings(checkouts: list[Checkout], entries: list[Entry], allow_list: str) -> list[str]:
    """Each hit no allow-list entry skips, then each allow-list entry without a reason or a hit."""
    out: list[str] = []
    for checkout in checkouts:
        allowed = {entry.path for entry in entries} if checkout.name == THIS_REPOSITORY else set()
        found = hits(checkout)
        out += [f"{checkout.repository}  {hit.path}:{hit.line}  {hit.name}"
                for hit in found if hit.path not in allowed]
        if checkout.name == THIS_REPOSITORY:
            used = {hit.path for hit in found}
            for entry in entries:
                if not entry.reason:
                    out.append(f"{allow_list}:{entry.line}  {entry.path} gives no reason")
                if entry.path not in used:
                    out.append(f"{allow_list}:{entry.line}  {entry.path} skips no hit in "
                               f"{checkout.repository}: remove the entry")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strict", action="store_true", help="fail (exit 1) on any finding")
    parser.add_argument("checkouts", nargs="*", type=Path, metavar="CHECKOUT",
                        help="a git work tree of living-doc or a component")
    parser.add_argument("--allow-list", type=Path, default=ALLOW_LIST, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    allow_list = args.allow_list.resolve()
    try:
        allow_list_name = allow_list.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        allow_list_name = allow_list.as_posix()
    try:
        checkouts = [open_checkout(path) for path in args.checkouts]
        if not any(checkout.name == THIS_REPOSITORY for checkout in checkouts):
            checkouts.insert(0, open_checkout(REPO_ROOT))
        problems = findings(checkouts, read_allow_list(allow_list), allow_list_name)
    except CheckError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print("Retired names in " + ", ".join(checkout.repository for checkout in checkouts))
    for problem in problems:
        print(f"  {problem}")
    if not problems:
        print(f"OK: none of the {len(RETIRED_NAMES)} retired names appears.")
        return 0
    level = "error" if args.strict else "warning"
    print(f"{level}: {len(problems)} finding(s). Remove each retired name, or list its living-doc file "
          f"in {allow_list_name} with the reason it is not a use.")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
