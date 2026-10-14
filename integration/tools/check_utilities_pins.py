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
"""Report the ``living-doc-utilities`` version each component pins, and warn on a minor skew.

Reads the pin from each component's runtime ``requirements.txt`` at the ref
``integration/tools/collector-snapshot-pins.env`` pins it to (fetched from GitHub at that ref), and
from ``tools/requirements-examples-check.txt``, the corpus checker's own requirements. Prints a
component -> pin table, then:

- a warning when two pins differ in their ``major.minor``, when a component pins no
  ``living-doc-utilities`` at all, or when a pin is not an exact ``==`` version;
- with ``--strict``, the same findings fail the run (exit 1) - for gates and milestones.

It reports and nothing more: whether the artifacts validate is the snapshot job's own check.

Usage:
    python integration/tools/check_utilities_pins.py [--strict] [--requirements COMPONENT=PATH ...]

``--requirements`` reads a component's requirements from a local file instead, e.g. a
working copy of the collector. Exit codes: 0 pins reported (warnings allowed unless
``--strict``), 1 a warning under ``--strict``, 2 a pin or requirements file that cannot be read.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
PINS_FILE = REPO_ROOT / "integration" / "tools" / "collector-snapshot-pins.env"
PACKAGE = "living-doc-utilities"

# Each component the snapshot job installs: its pin key in the pins file, its GitHub repository and
# the runtime requirements file its venv is built from.
COMPONENTS = {
    "collector-gh": ("COLLECTOR_GH_REF", "AbsaOSS/living-doc-collector-gh", "requirements.txt"),
}
# Requirements files of this repository's own tools, read from the working tree.
LOCAL = {
    "examples-check": "tools/requirements-examples-check.txt",
}

# `name[extras] <op> <version> ; <marker>` - one requirement line, comments already stripped.
_REQUIREMENT_RE = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*"
                             r"(?P<spec>[^;]*)")
_EXACT_RE = re.compile(r"^==\s*(?P<version>\d+(?:\.\d+)*)$")
_FETCH_TIMEOUT_SECONDS = 30


class PinError(Exception):
    """A pin or requirements file that cannot be read."""


@dataclass
class Pin:
    component: str
    source: str             # where the requirements were read from
    spec: Optional[str]     # the version specifier, e.g. '==0.6.0'; None when nothing is pinned

    @property
    def version(self) -> Optional[str]:
        m = _EXACT_RE.match(self.spec or "")
        return m.group("version") if m else None

    @property
    def minor(self) -> Optional[str]:
        return ".".join(self.version.split(".")[:2]) if self.version else None


def _canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def utilities_spec(requirements: str) -> Optional[str]:
    """The version specifier ``requirements`` gives ``living-doc-utilities``; None when absent."""
    for line in requirements.splitlines():
        text = line.split("#", 1)[0].strip()
        if not text or text.startswith("-"):
            continue        # an option line (-r, -e, --index-url, ...) pins nothing here
        m = _REQUIREMENT_RE.match(text)
        if m and _canonical(m.group("name")) == PACKAGE:
            return re.sub(r"\s+", "", m.group("spec"))
    return None


def read_pins_file(path: Path) -> dict[str, str]:
    """``KEY=VALUE`` lines of the pins file, read as data - never sourced."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise PinError(f"cannot read {path}: {exc}") from exc
    pins: dict[str, str] = {}
    for line in lines:
        text = line.strip()
        if text and not text.startswith("#") and "=" in text:
            key, _, value = text.partition("=")
            pins[key.strip()] = value.strip()
    return pins


def fetch(url: str) -> str:
    """The text at ``url``; a GitHub raw-content URL at a pinned ref."""
    try:
        with urllib.request.urlopen(url, timeout=_FETCH_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PinError(f"cannot fetch {url}: {exc}") from exc


def _read_local(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PinError(f"cannot read {path}: {exc}") from exc


def collect(pins_file: Path, overrides: dict[str, Path],
            fetcher: Callable[[str], str] = fetch) -> list[Pin]:
    """Each component's pin, in table order: the pinned components first, then the local tools."""
    result: list[Pin] = []
    refs = read_pins_file(pins_file) if set(COMPONENTS) - set(overrides) else {}
    for component, (key, repository, requirements) in COMPONENTS.items():
        if component in overrides:
            path = overrides[component]
            result.append(Pin(component, path.as_posix(), utilities_spec(_read_local(path))))
            continue
        ref = refs.get(key)
        if not ref:
            raise PinError(f"{pins_file.name} sets no {key}")
        url = f"https://raw.githubusercontent.com/{repository}/{ref}/{requirements}"
        result.append(Pin(component, f"{repository}@{ref[:12]} {requirements}",
                          utilities_spec(fetcher(url))))
    for component, relative in LOCAL.items():
        path = overrides.get(component, REPO_ROOT / relative)
        source = relative if component not in overrides else path.as_posix()
        result.append(Pin(component, source, utilities_spec(_read_local(path))))
    return result


def findings(pins: list[Pin]) -> list[str]:
    """What the table does not agree on: a missing or inexact pin, or a minor-version skew."""
    out: list[str] = []
    for pin in pins:
        if pin.spec is None:
            out.append(f"{pin.component} pins no {PACKAGE}")
        elif pin.version is None:
            out.append(f"{pin.component} pins {PACKAGE}{pin.spec}, not one exact '==' version")
    minors = {pin.minor for pin in pins if pin.minor is not None}
    if len(minors) > 1:
        pinned = ", ".join(f"{pin.component} {pin.version}" for pin in pins if pin.version)
        out.append(f"{PACKAGE} minor-version mismatch: {pinned}")
    return out


def table(pins: list[Pin]) -> list[str]:
    rows = [("component", "pin", "read from")]
    rows += [(pin.component, pin.version or pin.spec or "-", pin.source) for pin in pins]
    widths = [max(len(row[i]) for row in rows) for i in range(2)]
    return [f"  {a:<{widths[0]}}  {b:<{widths[1]}}  {c}" for a, b, c in rows]


def main(argv: Optional[list[str]] = None, fetcher: Callable[[str], str] = fetch) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strict", action="store_true",
                        help="fail (exit 1) on any warning - for gates and milestones")
    parser.add_argument("--requirements", action="append", default=[], metavar="COMPONENT=PATH",
                        help="read COMPONENT's requirements from a local file instead "
                             f"(components: {', '.join([*COMPONENTS, *LOCAL])})")
    parser.add_argument("--pins", type=Path, default=PINS_FILE, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    overrides: dict[str, Path] = {}
    for item in args.requirements:
        component, sep, path = item.partition("=")
        if not sep or component not in {*COMPONENTS, *LOCAL} or not path:
            parser.error(f"--requirements expects COMPONENT=PATH with COMPONENT one of "
                         f"{', '.join([*COMPONENTS, *LOCAL])}; got {item!r}")
        overrides[component] = Path(path)

    try:
        pins = collect(args.pins, overrides, fetcher)
    except PinError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"{PACKAGE} pins")
    print("\n".join(table(pins)))
    problems = findings(pins)
    if not problems:
        print(f"OK: every component pins {PACKAGE} {pins[0].minor}.")
        return 0
    # A workflow annotation surfaces the warning on the run's summary page as well as in the log.
    level = "error" if args.strict else "warning"
    prefix = f"::{level}::" if os.environ.get("GITHUB_ACTIONS") == "true" else f"{level}: "
    for problem in problems:
        print(f"{prefix}{problem}")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
