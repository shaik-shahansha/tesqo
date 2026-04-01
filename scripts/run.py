#!/usr/bin/env python3
"""
Tesqo — Smart Runner
=====================================
Automate your web tests with ease — Record, Run & Report.
Interactive menu to run tests, pick browser, open reports, or record a new test.
No memorising pytest flags needed.

Usage:
    run.bat
    python scripts/run.py
"""

import subprocess
import sys
import os
import glob
from pathlib import Path
from datetime import datetime


# ── Helpers ───────────────────────────────────────────────────────────────────

def run_pytest(args: list, report_name: str = "report.html") -> int:
    """Run pytest with the given args, generate an HTML report, offer to open it."""
    Path("reports/html").mkdir(parents=True, exist_ok=True)
    # Insert timestamp before .html to avoid overwriting previous reports
    stem, _, suffix = report_name.rpartition(".")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stamped_name = f"{stem}_{ts}.{suffix}"
    report_path = Path("reports/html") / stamped_name
    cmd = [sys.executable, "-m", "pytest"] + args + [
        f"--html={report_path}",
        "--self-contained-html",
        "-v",
    ]
    print(f"\n  Running: {' '.join(str(a) for a in cmd)}\n")
    print("  " + "─" * 60)
    result = subprocess.run(cmd)
    print("  " + "─" * 60)
    abs_report = report_path.resolve()
    print(f"\n  📄  Report: {abs_report}")
    if abs_report.exists():
        yn = input("  Open report in browser? (y/n) [y]: ").strip().lower()
        if yn != "n":
            open_file(str(abs_report))
    else:
        print("  ⚠  Report not generated (pytest failed before writing it).")
    return result.returncode


def open_file(path: str) -> None:
    """Open a file with the default OS application."""
    if os.name == "nt":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])


def pick_browser() -> str:
    """Ask user which browser to use."""
    print("\n  Browser: 1=Chrome (default)   2=Edge   3=Both (parallel)")
    b = input("  Choose: ").strip()
    return {"2": "msedge", "3": "both"}.get(b, "chromium")


def build_browser_args(browser: str) -> list:
    """Turn browser choice into pytest args (browser must not be 'both')."""
    if browser == "msedge":
        return ["--browser", "chromium", "--channel", "msedge"]
    return ["--browser", browser]


def run_with_browser(base_args: list, browser: str, report_name: str) -> int:
    """Run pytest for one or both browsers; returns last exit code."""
    if browser == "both":
        rc1 = run_pytest(base_args + ["--browser", "chromium"], "chrome_" + report_name)
        rc2 = run_pytest(base_args + ["--browser", "chromium", "--channel", "msedge"], "edge_" + report_name)
        return rc1 or rc2
    return run_pytest(base_args + build_browser_args(browser), report_name)


def list_test_files() -> list:
    """Return all test_*.py files under tests/, sorted."""
    files = sorted(glob.glob("tests/**/*.py", recursive=True))
    return [f for f in files if Path(f).name.startswith("test_")]


def header():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║    Tesqo — Runner                    ║")
    print("  ╠══════════════════════════════════════╣")
    print("  ║  1.  Run ALL tests                   ║")
    print("  ║  2.  Run SMOKE tests                 ║")
    print("  ║  3.  Run REGRESSION tests            ║")
    print("  ║  4.  Run AUTOMATION scripts          ║")
    print("  ║  5.  Run a SINGLE test file          ║")
    print("  ║  6.  Run a SINGLE test function      ║")
    print("  ║  7.  Record a NEW test               ║")
    print("  ║  8.  Open last report                ║")
    print("  ║  0.  Exit                            ║")
    print("  ╚══════════════════════════════════════╝")


# ── Menu actions ──────────────────────────────────────────────────────────────

def action_run_all():
    browser = pick_browser()
    run_with_browser(["tests/"], browser, "full_report.html")


def action_run_marker(marker: str, report: str):
    browser = pick_browser()
    run_with_browser(["tests/", "-m", marker], browser, report)


def action_run_single_file():
    files = list_test_files()
    if not files:
        print("\n  ⚠  No test files found under tests/")
        return
    print("\n  Available test files:")
    for i, f in enumerate(files, 1):
        print(f"    {i:3d}.  {f}")
    sel = input("\n  Enter number or path: ").strip()
    try:
        path = files[int(sel) - 1]
    except (ValueError, IndexError):
        path = sel
    if not Path(path).exists():
        print(f"\n  ⚠  File not found: {path}")
        return
    browser = pick_browser()
    run_with_browser([path], browser, "single_report.html")


def action_run_single_function():
    files = list_test_files()
    if not files:
        print("\n  ⚠  No test files found under tests/")
        return
    print("\n  Available test files:")
    for i, f in enumerate(files, 1):
        print(f"    {i:3d}.  {f}")
    sel = input("\n  Choose file (number or path): ").strip()
    try:
        path = files[int(sel) - 1]
    except (ValueError, IndexError):
        path = sel
    if not Path(path).exists():
        print(f"\n  ⚠  File not found: {path}")
        return

    # List test functions in file
    content = Path(path).read_text(encoding="utf-8")
    import re
    fns = re.findall(r"^def (test_\w+)", content, re.MULTILINE)
    if not fns:
        print("  ⚠  No test functions found in that file.")
        return
    print(f"\n  Test functions in {path}:")
    for i, fn in enumerate(fns, 1):
        print(f"    {i:3d}.  {fn}")
    sel2 = input("\n  Choose function (number): ").strip()
    try:
        fn_name = fns[int(sel2) - 1]
    except (ValueError, IndexError):
        print("  ⚠  Invalid selection.")
        return
    browser = pick_browser()
    run_with_browser([f"{path}::{fn_name}"], browser, "single_report.html")


def action_record():
    subprocess.run([sys.executable, "scripts/record.py"])


def action_open_last_report():
    reports = sorted(
        glob.glob("reports/html/*.html"),
        key=os.path.getmtime,
        reverse=True,
    )
    if reports:
        print(f"\n  Opening: {reports[0]}")
        open_file(reports[0])
    else:
        print("\n  ⚠  No reports found yet. Run some tests first.")


# ── Main loop ─────────────────────────────────────────────────────────────────

ACTIONS = {
    "1": action_run_all,
    "2": lambda: action_run_marker("smoke",      "smoke_report.html"),
    "3": lambda: action_run_marker("regression", "regression_report.html"),
    "4": lambda: action_run_marker("automation", "automation_report.html"),
    "5": action_run_single_file,
    "6": action_run_single_function,
    "7": action_record,
    "8": action_open_last_report,
}


def main():
    while True:
        header()
        choice = input("\n  Choose (0-8): ").strip()
        if choice == "0":
            print("\n  Bye!\n")
            sys.exit(0)
        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("\n  ⚠  Invalid choice — please enter a number from 0 to 8.")


if __name__ == "__main__":
    main()
