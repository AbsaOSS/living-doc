#!/usr/bin/env python3
"""
Compare a finished iteration against the recorded baseline.

"Did this change help?" should be a command, not an impression. This reads every target's
`grading.json` files in an iteration, computes the pass rate per target, and prints it beside the
figure recorded in `agentic/docs/testing/baseline.md`.

Two cautions it prints rather than hides:

* One run per eval per arm means there is no variance estimate, so a difference of a few
  hundredths is noise. The threshold below is deliberately coarse.
* A changed eval set makes an eval-by-eval comparison meaningless even when the aggregate still
  reads sensibly. The assertion count is shown so a changed denominator is visible.

Usage:
    compare_baseline.py <iteration_dir> [baseline_md]
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
NOISE = 0.02  # below this, call it unchanged


def recorded(baseline_md: Path) -> dict[str, float]:
    """Pull the aligned-arm pass rate per target out of baseline.md's table."""
    out: dict[str, float] = {}
    for line in baseline_md.read_text().splitlines():
        m = re.match(r"\|\s*`?@?([a-z0-9-]+)`?\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*\*{0,2}([0-9.]+)", line)
        if m:
            out[m.group(1)] = float(m.group(2))
    return out


def measured(iteration: Path) -> dict[str, tuple[float, int]]:
    out: dict[str, tuple[float, int]] = {}
    for d in sorted(p for p in iteration.iterdir() if p.is_dir()):
        passed = total = 0
        for f in d.glob("eval-*/with_skill/run-1/grading.json"):
            s = json.loads(f.read_text()).get("summary", {})
            passed += s.get("passed", 0)
            total += s.get("total", 0)
        if total:
            out[d.name] = (passed / total, total)
    return out


def main(iteration_dir: str, baseline_md: str | None = None) -> int:
    iteration = Path(iteration_dir)
    base_md = Path(baseline_md) if baseline_md else REPO / "agentic/docs/testing/baseline.md"
    if not iteration.is_dir():
        print(f"error: no such iteration directory: {iteration}", file=sys.stderr)
        return 1
    if not base_md.is_file():
        print(f"error: no baseline at {base_md}", file=sys.stderr)
        return 1

    base = recorded(base_md)
    now = measured(iteration)
    if not now:
        print(f"error: no graded runs under {iteration}", file=sys.stderr)
        return 1

    print(f"{'target':34} {'now':>6} {'baseline':>9} {'delta':>7} {'asserts':>8}")
    worse = []
    tp = tt = 0
    for name, (rate, total) in now.items():
        tp += rate * total
        tt += total
        b = base.get(name)
        if b is None:
            print(f"{name:34} {rate:6.3f} {'—':>9} {'new':>7} {total:8}")
            continue
        delta = rate - b
        flag = "" if abs(delta) < NOISE else ("  <= WORSE" if delta < 0 else "  better")
        print(f"{name:34} {rate:6.3f} {b:9.2f} {delta:+7.3f} {total:8}{flag}")
        if delta <= -NOISE:
            worse.append((name, b, rate))

    print(f"\n{'TOTAL':34} {tp/tt:6.3f} {'':>9} {'':>7} {tt:8}")
    missing = sorted(set(base) - set(now) - {"TOTAL"})
    if missing:
        print(f"\nnot run in this iteration: {', '.join(missing)}")
    print(f"\nDifferences under {NOISE:.2f} are noise: one run per eval per arm, so there is no "
          f"variance estimate.\nIf the assertion count changed, the eval set changed too — an "
          f"eval-by-eval comparison is then invalid.")
    if worse:
        print("\nBelow baseline — read the assertion before accepting it as a regression "
              "(see docs/testing/eval-protocol.md § 3):")
        for name, b, r in worse:
            print(f"  {name}: {b:.2f} -> {r:.3f}")
    return 0


if __name__ == "__main__":
    if not 2 <= len(sys.argv) <= 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
