#!/usr/bin/env python3
"""
Derive each `grading.json`'s `summary` block from its own `expectations` array.

`aggregate_benchmark.py` reads the pass rate from `grading["summary"]`. A grader that writes only
a top-level `pass_rate` therefore yields 0.0 % for every configuration — a whole run that looks
finished and means nothing. Recomputing `summary` from `expectations[]`, which is the actual record
of judgement, makes the two impossible to disagree.

Idempotent: safe to run after every grading pass.

Usage:
    normalize_grading.py <iteration_dir>
"""

import json
import sys
from pathlib import Path


def main(root: str) -> int:
    base = Path(root)
    if not base.is_dir():
        print(f"error: no such directory: {base}", file=sys.stderr)
        return 1

    changed = skipped = 0
    for f in sorted(base.rglob("grading.json")):
        d = json.loads(f.read_text())
        exps = d.get("expectations", [])
        if not exps:
            print(f"  SKIP (no expectations) {f.relative_to(base)}")
            skipped += 1
            continue
        total = len(exps)
        passed = sum(1 for e in exps if e.get("passed") is True)
        summary = {"total": total, "passed": passed, "failed": total - passed,
                   "pass_rate": round(passed / total, 4)}
        if d.get("summary") != summary:
            d["summary"] = summary
            f.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
            changed += 1

    print(f"normalized {changed} file(s)" + (f", {skipped} skipped" if skipped else ""))
    return 1 if skipped else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
