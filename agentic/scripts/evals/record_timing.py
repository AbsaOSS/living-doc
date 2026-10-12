#!/usr/bin/env python3
"""
Write `timing.json` for finished runs, with the model that produced them.

Token and duration figures arrive when a run reports and cannot be recovered afterwards, so they
are written as each run lands rather than batched at the end.

A run killed after writing its answer but before reporting usage has no figures at all. Passing
`<eval>:<arm>:missing` records that honestly — zeros plus a `note` saying they are unrecoverable —
because a zero that looks like a measurement is worse than an admitted gap.

Usage:
    record_timing.py <target_dir> <model> <eval-N>:<arm>:<tokens>:<ms> ...
    record_timing.py <target_dir> <model> <eval-N>:<arm>:missing

Example:
    record_timing.py $W/iteration-1/living-doc-update haiku \\
        eval-1:with_skill:45822:24317 eval-1:old_skill:44252:22208 eval-7:with_skill:missing
"""

import json
import sys
from pathlib import Path

MISSING_NOTE = (
    "The run produced its answer.md, but was terminated before it reported usage, so token and "
    "duration figures for this one run are unrecoverable. Treat the zeros as missing data, not as "
    "a measurement."
)


def main(argv: list[str]) -> int:
    target = Path(argv[1])
    model = argv[2]
    if not target.is_dir():
        print(f"error: no such target directory: {target}", file=sys.stderr)
        return 1

    rc = 0
    for spec in argv[3:]:
        parts = spec.split(":")
        if len(parts) == 3 and parts[2] == "missing":
            eval_id, arm, payload = parts[0], parts[1], None
        elif len(parts) == 4:
            eval_id, arm, tokens, ms = parts
            payload = (int(tokens), int(ms))
        else:
            print(f"error: cannot parse {spec!r}", file=sys.stderr)
            rc = 1
            continue

        matches = sorted(target.glob(f"{eval_id}-*/{arm}/run-1"))
        if len(matches) != 1:
            print(f"error: {eval_id}/{arm} matched {len(matches)} run dirs", file=sys.stderr)
            rc = 1
            continue

        if payload is None:
            data = {"model": model, "total_tokens": 0, "duration_ms": 0,
                    "total_duration_seconds": 0.0, "note": MISSING_NOTE}
        else:
            tokens, ms = payload
            data = {"model": model, "total_tokens": tokens, "duration_ms": ms,
                    "total_duration_seconds": round(ms / 1000, 1)}

        (matches[0] / "timing.json").write_text(json.dumps(data, indent=2) + "\n")
        # matches[0] is <eval-dir>/<arm>/run-1, so the eval directory is two levels up.
        print(f"  {'MISSING ' if payload is None else 'ok      '}{matches[0].parents[1].name}/{arm}")
    return rc


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv))
