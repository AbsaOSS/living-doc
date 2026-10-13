#!/usr/bin/env python3
"""
evals-inventory.py — what eval material exists for each skill and the agent, and whether it
is well formed. A local aid for the manual eval loop described in
agentic/docs/testing/skill-testing.md and agent-testing.md.

This is **not** a test and it is deliberately not wired into CI: the eval files are the source
material the skill-creator loop reads, and nothing in this repository runs an eval. What this
script does is answer the two questions you have before starting a loop — which cases exist,
and is any of them broken — without opening 25 JSON files by hand.

Usage:
  python agentic/scripts/evals-inventory.py                   # every skill and the agent
  python agentic/scripts/evals-inventory.py living-doc-update # one skill
  python agentic/scripts/evals-inventory.py --check           # shape only, exit 1 on a problem

Checks, when --check is given or a problem is found anyway:
  - every eval file parses as JSON
  - a body eval file is an object with `evals`; a trigger file is an array
  - each body case has an id, a prompt and an expected_output
  - each trigger case has a query and a boolean should_trigger
  - every `files:` entry resolves, relative to the skill folder
  - ids are unique within a file
"""

import argparse
import json
import sys
from pathlib import Path

LAYER = Path(__file__).resolve().parent.parent


def _problems(path: Path, data) -> list[str]:
    """Everything wrong with one eval file, in the author's terms."""
    out: list[str] = []
    rel = path.relative_to(LAYER).as_posix()
    is_trigger = path.name == "trigger-eval.json"

    if is_trigger:
        if not isinstance(data, list):
            return [f"{rel}: a trigger eval file is a bare array of queries, got "
                    f"{type(data).__name__}"]
        cases = data
    else:
        if not isinstance(data, dict) or "evals" not in data:
            return [f"{rel}: a body eval file is an object with an 'evals' array, got "
                    f"{type(data).__name__}"]
        cases = data["evals"]

    seen: set = set()
    for i, case in enumerate(cases):
        where = f"{rel}[{i}]"
        if not isinstance(case, dict):
            out.append(f"{where}: a case is an object, got {type(case).__name__}")
            continue
        case_id = case.get("id")
        if case_id is None:
            out.append(f"{where}: no 'id'")
        elif case_id in seen:
            out.append(f"{where}: duplicate id {case_id!r}")
        else:
            seen.add(case_id)
        if is_trigger:
            if not case.get("query"):
                out.append(f"{where}: a trigger case needs a 'query'")
            if not isinstance(case.get("should_trigger"), bool):
                out.append(f"{where}: 'should_trigger' must be true or false")
        else:
            if not case.get("prompt"):
                out.append(f"{where}: a body case needs a 'prompt'")
            if not case.get("expected_output"):
                out.append(f"{where}: a body case needs an 'expected_output'")
        # Fixture paths are written relative to the skill folder, as the guides show.
        for f in case.get("files", []) or []:
            if not (path.parent.parent / f).exists():
                out.append(f"{where}: fixture '{f}' does not exist")
    return out


def _owners() -> list[tuple[str, Path]]:
    """Every skill with an evals folder, plus the agent, in report order."""
    owners = [
        (d.name, d / "evals")
        for d in sorted((LAYER / "skills").iterdir())
        if (d / "evals").is_dir()
    ]
    for d in sorted((LAYER / "agents" / "evals").iterdir()):
        if d.is_dir():
            owners.append((f"@{d.name}", d))
    return owners


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("skill", nargs="?", help="limit to one skill or agent name")
    ap.add_argument("--check", action="store_true",
                    help="report shape problems only, and exit 1 when there are any")
    args = ap.parse_args()

    problems: list[str] = []
    rows: list[tuple[str, int, int, int]] = []

    for name, evals_dir in _owners():
        if args.skill and args.skill.lstrip("@") != name.lstrip("@"):
            continue
        body = trigger = fixtures = 0
        for path in sorted(evals_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                problems.append(f"{path.relative_to(LAYER).as_posix()}: invalid JSON — {e}")
                continue
            problems.extend(_problems(path, data))
            if path.name == "trigger-eval.json":
                trigger += len(data) if isinstance(data, list) else 0
            elif isinstance(data, dict):
                body += len(data.get("evals", []))
        files_dir = evals_dir / "files"
        if files_dir.is_dir():
            fixtures = sum(1 for _ in files_dir.iterdir() if _.is_file())
        rows.append((name, body, trigger, fixtures))

    if not rows:
        print(f"No evals found for {args.skill!r}.", file=sys.stderr)
        return 1

    if not args.check:
        print(f"{'skill / agent':38} {'body':>5} {'trigger':>8} {'fixtures':>9}")
        print("-" * 63)
        for name, body, trigger, fixtures in rows:
            print(f"{name:38} {body:5} {trigger:8} {fixtures:9}")
        totals = [sum(r[i] for r in rows) for i in (1, 2, 3)]
        print("-" * 63)
        print(f"{'total':38} {totals[0]:5} {totals[1]:8} {totals[2]:9}")
        print("\nThese are inputs for the manual loop, not a test suite — see "
              "agentic/docs/testing/skill-testing.md.")

    if problems:
        print(f"\n{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    if args.check:
        print(f"Every eval file is well formed ({len(rows)} skill(s)/agent(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
