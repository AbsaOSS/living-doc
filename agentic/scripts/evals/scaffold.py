#!/usr/bin/env python3
"""
Build the run directories for one target from its eval file.

Layout, which is what `aggregate_benchmark.py`'s globs expect:

    <workspace>/iteration-<N>/<target>/eval-<id>-<slug>/
        eval_metadata.json
        with_skill/run-1/outputs/
        old_skill/run-1/outputs/

The eval files in this repository use `expectations`; the harness reads `assertions`. This maps
one to the other when writing `eval_metadata.json` and **never modifies the eval file** — other
tooling (`evals-inventory.py`, the skills themselves) depends on its shape.

Usage:
    scaffold.py <target> <workspace> <iteration> [eval_file]

`eval_file` is only needed when the set does not live at
`agentic/skills/<target>/evals/evals.json` — the agent's is at
`agentic/agents/evals/<agent>/evals.json`.
"""

import json
import re
import sys
from pathlib import Path

# agentic/scripts/evals/scaffold.py -> repository root
REPO = Path(__file__).resolve().parents[3]


def slug(text: str, words: int = 6) -> str:
    """A short, stable directory name taken from the prompt's first few words."""
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return "-".join(toks[:words]) or "eval"


def main(target: str, workspace: str, iteration: int, eval_file: str | None = None) -> int:
    src = Path(eval_file) if eval_file else REPO / "agentic/skills" / target / "evals/evals.json"
    if not src.is_file():
        print(f"error: no eval file at {src}", file=sys.stderr)
        return 1

    data = json.loads(src.read_text())
    base = Path(workspace) / f"iteration-{iteration}" / target
    seen: dict[str, int] = {}

    for ev in data["evals"]:
        name = ev.get("eval_name") or slug(ev["prompt"])
        # A slug collision would make two evals share a directory and overwrite each other.
        if name in seen:
            name = f"{name}-{ev['id']}"
        seen[name] = ev["id"]

        d = base / f"eval-{ev['id']}-{name}"
        for cfg in ("with_skill", "old_skill"):
            (d / cfg / "run-1" / "outputs").mkdir(parents=True, exist_ok=True)
        (d / "eval_metadata.json").write_text(
            json.dumps(
                {
                    "eval_id": ev["id"],
                    "eval_name": name,
                    "category": ev.get("category", ""),
                    "prompt": ev["prompt"],
                    "expected_output": ev.get("expected_output", ""),
                    "files": ev.get("files", []),
                    "assertions": ev.get("expectations", []),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
        print(f"  eval-{ev['id']}-{name}\t{len(ev.get('expectations', []))} assertions")

    print(f"{len(data['evals'])} eval(s) scaffolded under {base}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2], int(sys.argv[3]),
                  sys.argv[4] if len(sys.argv) > 4 else None))
