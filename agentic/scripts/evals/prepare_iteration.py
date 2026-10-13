#!/usr/bin/env python3
"""
Set up a new iteration that reuses the previous iteration's measured arm as its baseline arm.

When the skills under test at iteration N-1 are exactly the baseline you now want to compare
against, re-running them is pure cost: the previous `with_skill` answers already are that arm,
produced by the same executor model. This builds `iteration-<N>` from the current eval files,
copies `<prev>/<target>/<eval>/with_skill/run-1/` into `old_skill/run-1/` wherever the eval's
prompt is unchanged, and creates `run-1 … run-<k>` for the arm being measured.

An eval whose prompt changed, or that is new, gets an empty `old_skill/run-1/` — run it against
the baseline worktree. Assertions may have changed freely: the reused answers are graded again
against the new ones, which is the point.

Usage:
    prepare_iteration.py <workspace> <new_iteration> <prev_iteration> <runs> [<target> ...]

Default targets: every target directory in the previous iteration.
Prints, per target, how many baseline answers were reused and which evals still need a baseline run.
"""

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scaffold  # noqa: E402

AGENT = "living-doc-bdd-copilot"


def _meta(eval_dir: Path) -> dict:
    return json.loads((eval_dir / "eval_metadata.json").read_text(encoding="utf-8"))


def main(workspace: str, new_it: int, prev_it: int, runs: int, targets: list[str]) -> int:
    ws = Path(workspace)
    prev_root = ws / f"iteration-{prev_it}"
    targets = targets or sorted(p.name for p in prev_root.iterdir() if p.is_dir() and not p.name.startswith("."))
    rc = 0
    for target in targets:
        eval_file = str(scaffold.REPO / "agentic/agents/evals" / target / "evals.json") if target == AGENT else None
        if scaffold.main(target, workspace, new_it, eval_file) != 0:
            rc = 1
            continue
        prev = {(_meta(d)["eval_id"]): d for d in (prev_root / target).glob("eval-*") if (d / "eval_metadata.json").is_file()}
        reused, need = 0, []
        for ed in sorted((ws / f"iteration-{new_it}" / target).glob("eval-*")):
            m = _meta(ed)
            for k in range(1, runs + 1):
                (ed / "with_skill" / f"run-{k}" / "outputs").mkdir(parents=True, exist_ok=True)
            src = prev.get(m["eval_id"])
            src_run = src / "with_skill" / "run-1" if src else None
            if src and _meta(src)["prompt"] == m["prompt"] and (src_run / "outputs" / "answer.md").is_file():
                dst = ed / "old_skill" / "run-1"
                for name in ("outputs/answer.md", "timing.json"):
                    if (src_run / name).is_file():
                        (dst / name).parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_run / name, dst / name)
                reused += 1
            else:
                need.append(m["eval_id"])
        note = f"; baseline run still needed for eval(s) {need}" if need else ""
        print(f"{target}: {reused} baseline answer(s) reused from iteration-{prev_it}{note}")
    return rc


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5:]))
