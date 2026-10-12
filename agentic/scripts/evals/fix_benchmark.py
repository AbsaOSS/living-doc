#!/usr/bin/env python3
"""
Correct `aggregate_benchmark.py`'s output in place.

Three fixes, none of which require patching skill-creator:

1. **The delta comes out inverted.** Config directories are discovered with `sorted(iterdir())`,
   so `old_skill` sorts before `with_skill` and `run_summary.delta` is computed the wrong way
   round. Reorder so the aligned arm is first and recompute as `with_skill - old_skill`.
2. **The benchmark does not say what it measured.** Stamp the executor and grader models and the
   baseline commit into `metadata`, so the file stays comparable once memory of the run has gone.
3. **The viewer needs `eval_name`** on each run as its section header, and
   `runs_per_configuration` set to the real value rather than the harness default.

Usage:
    fix_benchmark.py <target_dir> <executor_model> <grader_model> [baseline_commit]
"""

import json
import sys
from pathlib import Path


def main(bench_dir: str, executor_model: str, grader_model: str,
         baseline_commit: str = "c6dbcc7") -> None:
    d = Path(bench_dir)
    bench = json.loads((d / "benchmark.json").read_text())

    names = {}
    for meta in d.glob("eval-*/eval_metadata.json"):
        m = json.loads(meta.read_text())
        names[m["eval_id"]] = m["eval_name"]

    rs = bench["run_summary"]
    order = [c for c in ("with_skill", "old_skill") if c in rs]
    order += [c for c in rs if c not in order and c != "delta"]
    new = {c: rs[c] for c in order}
    if len(order) >= 2:
        a, b = new[order[0]], new[order[1]]
        new["delta"] = {
            "pass_rate": f"{a['pass_rate']['mean'] - b['pass_rate']['mean']:+.2f}",
            "time_seconds": f"{a['time_seconds']['mean'] - b['time_seconds']['mean']:+.1f}",
            "tokens": f"{a['tokens']['mean'] - b['tokens']['mean']:+.0f}",
        }
    bench["run_summary"] = new

    for r in bench["runs"]:
        r["eval_name"] = names.get(r["eval_id"], "")
    rank = {c: i for i, c in enumerate(order)}
    bench["runs"].sort(key=lambda r: (r["eval_id"], rank.get(r["configuration"], 9)))

    bench["metadata"]["executor_model"] = executor_model
    bench["metadata"]["analyzer_model"] = grader_model
    bench["metadata"]["runs_per_configuration"] = 1
    bench["metadata"]["baseline_commit"] = baseline_commit
    (d / "benchmark.json").write_text(json.dumps(bench, indent=2) + "\n")

    s = bench["run_summary"]
    print(f"{bench['metadata']['skill_name']}: "
          f"with_skill={s.get('with_skill', {}).get('pass_rate', {}).get('mean')} "
          f"old_skill={s.get('old_skill', {}).get('pass_rate', {}).get('mean')} "
          f"delta={s.get('delta', {}).get('pass_rate')}")



if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2], sys.argv[3],
         sys.argv[4] if len(sys.argv) > 4 else "c6dbcc7")
