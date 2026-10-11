#!/usr/bin/env python3
"""
migrate_pageobject_headers.py — bring existing PageObject headers to the current canon.

A PageObject header carries no state of its own: a Feature's state is derived from its
Functionalities, and a Feature has no deprecation date at all. Headers written before those
rules landed carry keys that the pipeline now rejects or ignores, and a project cannot migrate
them by hand without missing some. This reports every such key and, with --fix, removes the
ones whose correction is unambiguous.

What it reports, from Header Types' "Common mistakes" table
(skills/shared/references/living-doc-bdd-schemas.md#common-mistakes):

  removable — --fix deletes the line, nothing is lost
    status:            any value. A surface has no status. `status: STUB` / `status: candidate`
                       means the surface is not instrumented, which `stub-reason:` records.
    deprecated_at:     a Feature has no deprecation date, authored or derived.
    pageobject_statuses:  a Project Profile key that was never canon.

  renameable — --fix rewrites the key, keeping the value's column
    type:              -> surface_type:, and the value `screen` -> `UI`, the only surface type
                       a PageObject documents. Any other value is reported for a human.
    owner:             -> owners:            (the key is plural)

  reported only — the fix needs a human decision
    feature_dependencies: none    the field has no `none` value; omit the key instead
    a missing required key        `user_stories:` / `functionalities:` /
                                  `external_dependencies:` take `none`, they are not optional
    status: STUB with no stub-reason:   removing the status would lose the fact that the
                                  surface is not instrumented; write the reason first

Usage:
    python migrate_pageobject_headers.py <path> [<path> ...]      # report only
    python migrate_pageobject_headers.py <path> --fix             # apply the safe changes
    python migrate_pageobject_headers.py <path> --json            # machine-readable

A <path> is a file or a directory, which is walked for PageObject sources
(.ts, .tsx, .js, .py). Only the header block is touched: the lines between the first two
`====` rules of a file that carries a `LIVING DOC —` title.

Exit code 0 = nothing to migrate (or --fix applied everything safely).
Exit code 1 = something still needs a human.
Exit code 2 = usage or IO error.
"""

import argparse
import json
import re
import sys
from pathlib import Path

SOURCE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py"}

# The header's title line is what identifies an entity at all: without the id nothing in the
# header is read (see the canon's "Where a part starts and ends").
TITLE_RE = re.compile(r"LIVING DOC\s+[—-]\s+(?P<id>FEAT-\d+)")
RULE_RE = re.compile(r"={10,}")
# A header line carries its marker — ` * ` in a PageObject header, `# ` in a .feature header.
KEY_RE = re.compile(r"^(?P<prefix>\s*(?:\*|#|//)\s*)(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(?P<value>.*)$")

REMOVABLE = {
    "status": "a surface has no status — a Feature's state is derived from its Functionalities",
    "deprecated_at": "a Feature has no deprecation date, authored or derived",
    "pageobject_statuses": "never a canonical key",
}
RENAMEABLE = {"type": "surface_type", "owner": "owners"}
# A PageObject is the test abstraction for a UI surface only, so `type: screen` becomes
# `surface_type: UI` — the key and the value are both wrong in the old spelling.
VALUE_FIXES = {("type", "screen"): "UI"}
CANONICAL_SURFACE_TYPES = {"UI"}
REQUIRED_KEYS = ("surface_type", "route", "owners", "purpose", "user_stories",
                 "functionalities", "external_dependencies", "page-object")
TAKES_NONE = ("user_stories", "functionalities", "external_dependencies")


def _rewrite_key_line(line: str, m: "re.Match", new_key: str, new_value: str) -> str:
    """Rewrite a header line's key, and value when it changed, keeping the value's column.

    A header's values sit in one column, which is how the canon's examples read. A longer or
    shorter key would shift the value and leave the block ragged, so the padding absorbs the
    difference. A key too long for the column keeps one space.
    """
    prefix, old_key, old_value = m.group("prefix"), m.group("key"), m.group("value")
    value_column = line.index(old_value) if old_value else len(line.rstrip("\n"))
    head = f"{prefix}{new_key}:"
    pad = max(1, value_column - len(head))
    newline = "\n" if line.endswith("\n") else ""
    return f"{head}{' ' * pad}{new_value}".rstrip() + newline


def header_bounds(lines: list[str]) -> tuple[int, int] | None:
    """The header block's line range, or None when the file carries no living-doc header.

    The block runs from the first `====` rule to the next one after the title, which is how
    the canon delimits it; a rule inside the header is an optional end of a block, and the
    last rule ends the header.
    """
    rules = [i for i, l in enumerate(lines) if RULE_RE.search(l)]
    if len(rules) < 2:
        return None
    if not any(TITLE_RE.search(l) for l in lines[rules[0]:rules[-1] + 1]):
        return None
    return rules[0], rules[-1]


def scan_file(path: Path) -> dict:
    """Every finding in one file, with the migrated lines when there are safe changes."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {"file": str(path), "error": str(e), "findings": [], "lines": None}
    lines = text.splitlines(keepends=True)
    bounds = header_bounds(lines)
    if bounds is None:
        return {"file": str(path), "findings": [], "lines": None}
    start, end = bounds

    findings: list[dict] = []
    out = list(lines)
    seen: dict[str, str] = {}
    drop: set[int] = set()

    for i in range(start, end + 1):
        m = KEY_RE.match(lines[i].rstrip("\n"))
        if not m:
            continue
        key, value = m.group("key"), m.group("value").strip()
        seen[key] = value
        if key in REMOVABLE:
            # `status: STUB` without a stub-reason carries the only record that the surface is
            # not instrumented. Dropping it silently would lose that, so it needs a human.
            if key == "status" and value.lower() in {"stub", "candidate"} and "stub-reason" not in seen:
                findings.append({"line": i + 1, "key": key, "value": value,
                                 "action": "needs-human",
                                 "detail": f"'{key}: {value}' records that the surface is not "
                                           "instrumented, and the header has no 'stub-reason:'. "
                                           "Write 'stub-reason: <why>' first, then remove the status."})
                continue
            findings.append({"line": i + 1, "key": key, "value": value, "action": "remove",
                             "detail": REMOVABLE[key]})
            drop.add(i)
        elif key in RENAMEABLE:
            new_key = RENAMEABLE[key]
            new_value = VALUE_FIXES.get((key, value.lower()), value)
            detail = f"'{key}:' is '{new_key}:' in the canon"
            if new_value != value:
                detail += f", and '{value}' is '{new_value}'"
            findings.append({"line": i + 1, "key": key, "value": value, "action": "rename",
                             "detail": detail})
            out[i] = _rewrite_key_line(lines[i], m, new_key, new_value)
            if new_key == "surface_type" and new_value not in CANONICAL_SURFACE_TYPES:
                findings.append({"line": i + 1, "key": new_key, "value": new_value,
                                 "action": "needs-human",
                                 "detail": f"'surface_type: {new_value}' is not canonical — a "
                                           "PageObject documents a UI surface, so the value is 'UI'"})
        elif key == "feature_dependencies" and value.lower() == "none":
            findings.append({"line": i + 1, "key": key, "value": value, "action": "needs-human",
                             "detail": "the field has no 'none' value — omit the key entirely "
                                       "when the surface calls no documented API Feature"})

    # A stub-reason that survived means the surface is documented but not instrumented; that is
    # the marker, so nothing else is expected. Missing required keys are a separate matter.
    present = set(seen) | {RENAMEABLE[k] for k in seen if k in RENAMEABLE}
    for key in REQUIRED_KEYS:
        if key not in present:
            hint = "takes 'none' when there is nothing to list" if key in TAKES_NONE else "is required"
            findings.append({"line": start + 1, "key": key, "value": None, "action": "needs-human",
                             "detail": f"'{key}:' is missing — it {hint}"})

    migrated = [l for i, l in enumerate(out) if i not in drop] if findings else None
    return {"file": str(path), "findings": findings, "lines": migrated}


def iter_sources(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            found.extend(sorted(f for f in p.rglob("*") if f.suffix in SOURCE_SUFFIXES and f.is_file()))
        elif p.is_file():
            found.append(p)
        else:
            print(f"Error: no such file or directory: {raw}", file=sys.stderr)
            sys.exit(2)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="Bring existing PageObject headers to the current canon.")
    ap.add_argument("paths", nargs="+", help="PageObject files or directories to walk")
    ap.add_argument("--fix", action="store_true", help="apply the removals and renames")
    ap.add_argument("--json", action="store_true", dest="as_json", help="machine-readable output")
    args = ap.parse_args()

    results = [r for r in (scan_file(p) for p in iter_sources(args.paths)) if r["findings"] or r.get("error")]
    safe = sum(1 for r in results for f in r["findings"] if f["action"] in {"remove", "rename"})
    human = sum(1 for r in results for f in r["findings"] if f["action"] == "needs-human")

    if args.fix:
        for r in results:
            if r["lines"] is not None and any(f["action"] in {"remove", "rename"} for f in r["findings"]):
                Path(r["file"]).write_text("".join(r["lines"]), encoding="utf-8")

    if args.as_json:
        print(json.dumps({"headers_with_findings": len(results), "safe": safe,
                          "needs_human": human, "applied": bool(args.fix),
                          "results": results}, indent=2))
        return 1 if human else 0

    if not results:
        print("Every PageObject header scanned is already at the current canon.")
        return 0

    for r in results:
        print(f"\n{r['file']}")
        if r.get("error"):
            print(f"  ! could not read: {r['error']}")
            continue
        for f in r["findings"]:
            mark = {"remove": "- ", "rename": "~ ", "needs-human": "? "}[f["action"]]
            where = f"line {f['line']}"
            shown = f"{f['key']}: {f['value']}" if f["value"] is not None else f"{f['key']}:"
            print(f"  {mark}{where:9} {shown}")
            print(f"              {f['detail']}")

    verb = "applied" if args.fix else "to apply"
    print(f"\n{safe} safe change(s) {verb}, {human} needing a human decision.")
    if not args.fix and safe:
        print("Re-run with --fix to apply the removals and renames.")
    return 1 if human else 0


if __name__ == "__main__":
    sys.exit(main())
