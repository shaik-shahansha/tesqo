#!/usr/bin/env python3
"""
Tesqo — Smart Recorder
=====================================
Automate your web tests with ease — Record, Run & Report.
Prompts for test name, URL, and category, then:
  1. Launches playwright codegen (browser opens — just interact normally)
  2. When browser is closed, auto-processes the generated code:
       - Replaces hardcoded BASE_URL  → config.BASE_URL
       - Replaces hardcoded username  → config.USERNAME
       - Replaces hardcoded password  → config.PASSWORD
       - Adds missing imports
       - Adds @pytest.mark.<category> to every test function
  3. Saves to tests/<category>/test_<name>.py
  4. Prints the exact command to run the test immediately

Usage:
    record.bat
    python scripts/record.py
"""

import subprocess
import sys
import os
import re
from pathlib import Path
from datetime import datetime


# ── Helpers ───────────────────────────────────────────────────────────────────

def prompt(label: str, default: str = None, required: bool = False) -> str:
    """Print a prompt and return user input, falling back to default."""
    suffix = f" [{default}]" if default else ""
    while True:
        val = input(f"  {label}{suffix}: ").strip()
        if val:
            return val
        if default is not None:
            return default
        if required:
            print("    ⚠  This field is required.")
        else:
            return ""


def load_env() -> dict:
    """Read .env without importing python-dotenv (used before venv is active)."""
    env: dict = {}
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def sanitize_name(name: str) -> str:
    """Convert any string to a safe Python/file identifier."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_") or "recorded_test"


# ── Post-processing ───────────────────────────────────────────────────────────

def replace_urls(code: str, base_url: str) -> str:
    """Replace 'https://base/path' → config.BASE_URL + '/path'  (or just config.BASE_URL)."""
    if not base_url:
        return code
    escaped = re.escape(base_url)
    for q in ('"', "'"):
        # Full URL with path suffix:  "https://app.com/login"  → config.BASE_URL + "/login"
        code = re.sub(
            rf'{q}{escaped}(/[^{q}]*){q}',
            r'config.BASE_URL + "\1"',
            code,
        )
        # Full URL with no path:  "https://app.com"  → config.BASE_URL
        code = code.replace(f'{q}{base_url}{q}', "config.BASE_URL")
    return code


def replace_credentials(code: str, username: str, password: str) -> str:
    """Replace literal username/password strings with config references."""
    for q in ('"', "'"):
        if username:
            code = code.replace(f"{q}{username}{q}", "config.USERNAME")
        if password:
            code = code.replace(f"{q}{password}{q}", "config.PASSWORD")
    return code


def ensure_imports(code: str) -> str:
    """Add missing top-level imports without duplicating existing ones."""
    needed = []
    if "from config.settings import config" not in code:
        needed.append("from config.settings import config")
    if "import pytest" not in code:
        needed.append("import pytest")
    if not needed:
        return code

    lines = code.split("\n")
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
    for imp in reversed(needed):
        lines.insert(insert_at, imp)
    return "\n".join(lines)


def add_markers(code: str, category: str) -> str:
    """Prepend @pytest.mark.<category> before every def test_... function."""
    lines = code.split("\n")
    result = []
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("def test_"):
            # Only add if not already marked (check last few lines)
            recent = " ".join(result[-4:])
            if f"@pytest.mark.{category}" not in recent:
                indent = " " * (len(line) - len(stripped))
                result.append(f"{indent}@pytest.mark.{category}")
        result.append(line)
    return "\n".join(result)


def post_process(code: str, base_url: str, username: str, password: str, category: str) -> str:
    code = replace_urls(code, base_url)
    code = replace_credentials(code, username, password)
    code = ensure_imports(code)
    code = add_markers(code, category)
    return code


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║    Tesqo — Smart Recorder            ║")
    print("  ╚══════════════════════════════════════╝")
    print()

    env = load_env()
    base_url = env.get("BASE_URL", "")
    username = env.get("USERNAME", "")
    password = env.get("PASSWORD", "")

    # ── Gather inputs ─────────────────────────────────────────────────────────
    test_name_raw = prompt("Test name (e.g. login_as_admin)", required=True)
    test_name = sanitize_name(test_name_raw)

    url = prompt("URL to record on", default=base_url or None, required=True)

    print("  Category options: smoke | regression | automation")
    category = prompt("Category", default="regression")
    if category not in ("smoke", "regression", "automation"):
        print(f"    → Unknown category '{category}', defaulting to: regression")
        category = "regression"

    # ── Resolve output path ───────────────────────────────────────────────────
    output_dir = Path(f"tests/{category}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"test_{test_name}.py"

    if output_file.exists():
        print(f"\n  ⚠  File already exists: {output_file}")
        overwrite = prompt("Overwrite? (y/n)", default="n")
        if overwrite.lower() != "y":
            ts = datetime.now().strftime("%H%M%S")
            output_file = output_dir / f"test_{test_name}_{ts}.py"
            print(f"  → Will save as: {output_file}")

    temp_file = Path("tests/_recorded_temp.py")

    # ── Launch recorder ───────────────────────────────────────────────────────
    print()
    print(f"  🎬  Opening browser at: {url}")
    print("  →   Interact with the page. Close the browser window when done.\n")

    subprocess.run([
        sys.executable, "-m", "playwright", "codegen",
        "--target", "python-pytest",
        "--output", str(temp_file),
        url,
    ])

    # ── Handle empty / cancelled recording ────────────────────────────────────
    if not temp_file.exists() or temp_file.stat().st_size < 80:
        print("\n  ⚠  Nothing was recorded — no interactions detected.")
        if temp_file.exists():
            temp_file.unlink()
        sys.exit(0)

    # ── Post-process & save ───────────────────────────────────────────────────
    code = temp_file.read_text(encoding="utf-8")
    code = post_process(code, base_url, username, password, category)
    output_file.write_text(code, encoding="utf-8")
    temp_file.unlink()

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("  ✅  Test saved!")
    print(f"      File    : {output_file}")
    print(f"      Marker  : @pytest.mark.{category}")
    print()
    print("  ▶  Run this test now (headed / visible browser):")
    print(f"      pytest {output_file} -v --headed")
    print()
    print(f"  ▶  Batch run all {category} tests:")
    print(f"      pytest tests/{category}/ -v")
    print()
    print("  ▶  Or just launch:  run.bat  (interactive menu)")
    print()


if __name__ == "__main__":
    main()
