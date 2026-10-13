#!/usr/bin/env python3
"""
Output-encoding tests for every skill script.

An agent runs a skill's script and reads its output through a pipe. On Windows a pipe uses the
legacy code page (cp1252, cp1250, ...), so a report line carrying ✅, ⚠️ or an em dash raised
UnicodeEncodeError — and these scripts exit 1 on any exception, which is also the code they use to
mean "findings". A crash read as findings, on every Windows machine, was found by running the
script tests there; CI on Linux never saw it.

Not only the scripts' own markers: they also print the user's data, so a Czech entity name crashes
a script that prints nothing non-ASCII itself. The guard therefore requires every command-line
script to switch stdout to UTF-8, and runs two of them end to end under a forced legacy encoding,
which reproduces the Windows failure on any OS.
"""
__test__ = False  # pytest: ignore this helper script

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent
LEGACY_PIPE = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}


def _scripts():
    for path in sorted(SKILLS_DIR.glob("*/scripts/*.py")) + sorted((SKILLS_DIR / "shared" / "lib").glob("*.py")):
        if not path.name.startswith("test_"):
            yield path


def test_every_cli_script_switches_stdout_to_utf8():
    offenders, checked = [], 0
    for script in _scripts():
        text = script.read_text(encoding="utf-8")
        if 'if __name__ == "__main__":' not in text:
            continue
        checked += 1
        if 'sys.stdout.reconfigure(encoding="utf-8")' not in text:
            offenders.append(str(script.relative_to(SKILLS_DIR)))
    assert not offenders, (
        "command-line script never switches stdout to UTF-8 — it crashes when its output is piped "
        "on Windows and it prints anything non-ASCII:\n  " + "\n  ".join(offenders)
    )
    print(f"✓ All {checked} command-line script(s) switch stdout to UTF-8")


def test_script_survives_a_legacy_code_page_pipe():
    """find_unused_po_methods.py prints its own ✅ marker."""
    script = SKILLS_DIR / "bdd-maintain" / "scripts" / "find_unused_po_methods.py"
    with tempfile.TemporaryDirectory() as tmp:
        pages, steps = Path(tmp, "pages"), Path(tmp, "steps")
        pages.mkdir()
        steps.mkdir()
        (pages / "checkout.page.ts").write_text(
            "export class CheckoutPage {\n  async confirmOrder() {}\n}\n", encoding="utf-8"
        )
        (steps / "checkout.steps.ts").write_text(
            "When('x', async function () { await this.checkoutPage.confirmOrder(); });\n", encoding="utf-8"
        )
        result = subprocess.run(
            [sys.executable, str(script), "--pages-dir", str(pages), "--steps-dir", str(steps)],
            capture_output=True, env=LEGACY_PIPE,
        )
    assert result.returncode == 0, (
        f"exit {result.returncode} under a cp1252 pipe:\n{result.stderr.decode('utf-8', 'replace')[-600:]}"
    )
    assert "All PageObject methods are used." in result.stdout.decode("utf-8")
    print("✓ A report with non-ASCII markers survives a legacy code-page pipe")


def test_user_data_survives_a_legacy_code_page_pipe():
    """validate_entity.py prints the entity it checks — user data, often not ASCII."""
    script = SKILLS_DIR / "living-doc-update" / "scripts" / "validate_entity.py"
    with tempfile.TemporaryDirectory() as tmp:
        entity = Path(tmp, "entity.json")
        entity.write_text(
            '{"type": "Feature", "id": "FEAT-001", "name": "Nákupní košík", "surface_type": "UI",'
            ' "purpose": "Zákazník upraví položky před objednávkou.", "user_stories": [],'
            ' "functionalities": [], "owners": ["tým-prodej"], "external_dependencies": []}',
            encoding="utf-8",
        )
        result = subprocess.run([sys.executable, str(script), str(entity)], capture_output=True, env=LEGACY_PIPE)
    stderr = result.stderr.decode("utf-8", "replace")
    assert "UnicodeEncodeError" not in stderr and "Traceback" not in stderr, (
        f"exit {result.returncode} under a cp1252 pipe:\n{stderr[-600:]}"
    )
    print("✓ A report carrying non-ASCII user data survives a legacy code-page pipe")


if __name__ == "__main__":
    try:
        test_every_cli_script_switches_stdout_to_utf8()
        test_script_survives_a_legacy_code_page_pipe()
        test_user_data_survives_a_legacy_code_page_pipe()
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
