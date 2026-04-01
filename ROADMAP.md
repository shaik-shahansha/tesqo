# Tesqo — Roadmap
> Evolving from a project template into a true installable CLI framework
> *Automate your web tests with ease — Record, Run & Report.*

---

## The Vision

```bash
pip install tesqo

tesqo new myapp               # scaffold a fresh project
tesqo record                  # smart recorder
tesqo run                     # interactive test runner
tesqo report                  # open last report
tesqo switch myapp            # switch between multiple projects
```

One install. Works across unlimited projects. No copy-pasting folders.

---

## Phase 1 — PyPI Package Structure

Transform the current project template into an installable Python package.

### Repository layout

```
tesqo/                              ← GitHub repo root
│
├── pyproject.toml                  ← Package metadata + build config (PEP 621)
├── LICENSE
├── README.md
├── CHANGELOG.md
│
├── tesqo/                          ← The actual Python package
│   ├── __init__.py                 ← version = "0.1.0"
│   ├── cli.py                      ← Entry point (Typer app)
│   │
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── cmd_new.py              ← tesqo new <project>
│   │   ├── cmd_record.py           ← tesqo record
│   │   ├── cmd_run.py              ← tesqo run
│   │   ├── cmd_report.py           ← tesqo report
│   │   ├── cmd_switch.py           ← tesqo switch <project>
│   │   └── cmd_info.py             ← tesqo info
│   │
│   ├── core/
│   │   ├── recorder.py             ← codegen + post-processing logic
│   │   ├── runner.py               ← pytest invocation + report opening
│   │   ├── code_cleaner.py         ← replace hardcoded values with config refs
│   │   └── project_config.py       ← locate / load testpilot.toml per project
│   │
│   ├── templates/                  ← Jinja2 templates for scaffolded files
│   │   ├── conftest.py.j2
│   │   ├── settings.py.j2
│   │   ├── pytest_ini.j2
│   │   ├── env_example.j2
│   │   ├── requirements_txt.j2
│   │   ├── gitignore.j2
│   │   ├── test_login_py.j2        ← sample smoke test
│   │   └── data_loader_py.j2
│   │
│   └── utils/
│       ├── console.py              ← Rich-based pretty printing
│       ├── file_ops.py             ← safe file read/write helpers
│       └── excel.py                ← openpyxl helpers
│
└── tests/                          ← TestPilot's own tests (meta!)
    └── test_cli.py
```

### pyproject.toml (key sections)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "tesqo"
version = "0.1.0"
description = "Automate your web tests with ease — Record, Run & Report"
license = {text = "MIT"}
requires-python = ">=3.11"
dependencies = [
    "playwright>=1.51",
    "pytest>=8.3",
    "pytest-playwright>=0.7",
    "pytest-html>=4.1",
    "pytest-xdist>=3.6",
    "openpyxl>=3.1",
    "pandas>=2.2",
    "python-dotenv>=1.0",
    "typer>=0.12",          # CLI framework
    "rich>=13.0",           # beautiful terminal output
    "jinja2>=3.1",          # template rendering for scaffolding
]

[project.scripts]
tesqo = "tesqo.cli:app"            # this makes "tesqo" a shell command

[project.urls]
Homepage = "https://github.com/yourusername/tesqo"
Documentation = "https://tesqo.readthedocs.io"
```

---

## Phase 2 — CLI Commands (Typer)

### cli.py (entry point)

```python
import typer
from tesqo.commands import cmd_new, cmd_record, cmd_run, cmd_report, cmd_switch, cmd_info

app = typer.Typer(
    name="tesqo",
    help="🧪 Tesqo — Automate your web tests with ease. Record, Run & Report.",
    no_args_is_help=True,
)

app.command("new")(cmd_new.run)
app.command("record")(cmd_record.run)
app.command("run")(cmd_run.run)
app.command("report")(cmd_report.run)
app.command("switch")(cmd_switch.run)
app.command("info")(cmd_info.run)

if __name__ == "__main__":
    app()
```

### tesqo new \<project\>

```bash
tesqo new myapp
tesqo new work/client-portal --browser edge
```

**What it does:**
1. Creates `myapp/` directory
2. Renders all Jinja2 templates into that folder (full project skeleton)
3. Creates `myapp/.env` from template, prompts for BASE_URL
4. Creates `myapp/testpilot.toml` (project config — name, browser, paths)
5. Runs `pip install` if inside a venv, otherwise prints install instructions
5. Prints: `cd myapp && tesqo record` to get started

```
  ✅  Project created: myapp/
      ├── .env               ← edit this now
      ├── tests/             ← your test cases go here
      ├── data/              ← Excel inputs
      └── reports/           ← auto-generated

  Next:  cd myapp
         tesqo record
```

### tesqo record

```bash
tesqo record
tesqo record --name login_admin --url https://myapp.com --category smoke
```

Same smart recorder as today, but:
- Reads project from `tesqo.toml` in current folder
- `--name`, `--url`, `--category` flags skip the prompts (good for scripting)
- Auto-detects BASE_URL from `.env` and pre-fills the URL prompt

### tesqo run

```bash
tesqo run                    # interactive menu
tesqo run smoke              # run directly by marker
tesqo run regression --browser edge
tesqo run --file tests/smoke/test_login.py
tesqo run --fn test_login_success
tesqo run --all --browser both    # chrome + edge parallel
```

### tesqo report

```bash
tesqo report                 # open most recent report
tesqo report --list          # list all saved reports
tesqo report --open smoke    # open most recent smoke report
```

### tesqo switch

```bash
tesqo switch                 # interactive picker of known projects
tesqo switch myapp           # set myapp as active project
tesqo switch ../client-portal
```

Writes the active project path to `~/.tesqo/active_project` so all commands
operate on the right project without `cd`-ing.

### tesqo info

```bash
tesqo info
```

Prints current project status:
```
  Project   : myapp  [Tesqo v0.1.0]
  BASE_URL  : https://myapp.com
  Browser   : chromium
  Tests     : 12 total  (4 smoke, 7 regression, 1 automation)
  Last run  : 2026-04-01 14:32  — 11 passed, 1 failed
  Report    : reports/html/report.html
```

---

## Phase 3 — Multi-Project Workspace Support

### testpilot.toml (per-project config file)

```toml
[project]
name = "myapp"
description = "E2E tests for MyApp"
created = "2026-04-01"

[browser]
default = "chromium"
headless = false
slow_mo = 0

[paths]
tests = "tests"
data  = "data"
reports = "reports"

[env]
file = ".env"
```

### Global workspace registry (~/.testpilot/workspace.toml)

```toml
[projects]
myapp        = "C:/dev/myapp"
client-portal = "C:/dev/client-portal"
internal-tools = "C:/dev/internal-tools"

[active]
project = "myapp"
```

### Example: Managing multiple projects

```bash
# Create two projects
tesqo new myapp
tesqo new client-portal

# Work on myapp
tesqo switch myapp
tesqo record            # records into myapp/tests/
tesqo run smoke

# Switch to client-portal
tesqo switch client-portal
tesqo record            # records into client-portal/tests/
tesqo run regression
```

Each project has completely isolated:
- `.env` (different URLs, creds)
- `tests/` folder
- `data/` Excel files
- `reports/` (timestamped, never overwritten)

---

## Phase 4 — Developer Experience Improvements

### 4.1 — Rich terminal output (via `rich`)

```
  ┌──────────────────────────────────────────────┐
  │  🧪 Tesqo  v1.0.0  │  Project: myapp          │
  └──────────────────────────────────────────────┘

  Running: smoke tests on chromium
  ──────────────────────────────────────────────

  ✅  test_login_success           0.8s
  ✅  test_login_wrong_password     0.6s
  ✅  test_login_page_elements      0.5s
  ──────────────────────────────────────────────
  3 passed in 1.9s  │  📄 Report: reports/html/smoke_report.html
```

### 4.2 — Allure report integration

```bash
testpilot run --allure             # generates Allure results
testpilot report --allure          # opens Allure server dashboard
```

### 4.3 — Scheduled / watch mode

```bash
testpilot run smoke --watch        # re-runs on any test file change
testpilot run smoke --every 30min  # scheduled repeated runs
```

### 4.4 — Auto-selector healing

If a recorded selector fails (e.g. `#username` changed to `#user-input`),
Tesqo logs a warning and suggests alternatives found on the page:

```
  ⚠  Selector '#username' not found.
     Did you mean?
       • input[name='user']
       • #user-input
       • [data-testid='username-field']
  
  Update: tesqo fix tests/smoke/test_login.py
```

### 4.5 — Test generation from URL (AI-assisted, optional)

```bash
tesqo generate --url https://myapp.com/login --type smoke
```

Uses Playwright + heuristics to:
- Detect form fields, buttons, links
- Auto-generate a login/navigation test without recording

---

## Phase 5 — Publishing to PyPI

### Steps to publish

```bash
# 1. Build the package
pip install hatch
hatch build                        # creates dist/*.whl and dist/*.tar.gz

# 2. Test on TestPyPI first
pip install twine
twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ tesqo
tesqo --help

# 3. Publish to real PyPI
twine upload dist/*
```

### Then anyone does:

```bash
pip install tesqo
tesqo new myproject
```

### Versioning strategy
- `0.x.y` — current template-based approach (what exists today)
- `1.0.0` — full CLI with `tesqo new / record / run`
- `1.x.y` — multi-project workspace, Allure, watch mode
- `2.0.0` — AI-assisted test generation, self-healing selectors

---

## Phase 6 — Open Source Launch Checklist

```
Repository setup:
  ☐ GitHub repo: github.com/yourusername/tesqo
  ☐ Description: "Automate your web tests with ease — Record, Run & Report"
  ☐ Topics: playwright, pytest, testing, automation, e2e, python, web-testing
  ☐ LICENSE (MIT)
  ☐ README.md  ✅ (done)
  ☐ CONTRIBUTING.md
  ☐ CODE_OF_CONDUCT.md
  ☐ CHANGELOG.md
  ☐ .github/ISSUE_TEMPLATE/ (bug + feature)
  ☐ .github/workflows/ci.yml (run tests on PR)

Package:
  ☐ pyproject.toml
  ☐ PyPI account at pypi.org
  ☐ Publish tesqo to PyPI
  ☐ Add PyPI badge to README

Community:
  ☐ Write "Getting Started in 5 Minutes" blog/dev.to post
  ☐ Post to r/Python, r/softwaretesting, HackerNews Show HN
  ☐ Tag @playwright_dev on Twitter/X
```

---

## Build Timeline

| Week | Deliverable |
|---|---|
| Week 1 | `pyproject.toml`, Typer CLI skeleton, `tesqo --help` works |
| Week 2 | `tesqo new <project>` — scaffold via Jinja2 templates |
| Week 3 | `tesqo record` — current recorder wrapped as CLI command |
| Week 4 | `tesqo run` — current runner wrapped with markers + browser flags |
| Week 5 | `tesqo report`, `tesqo info`, Rich output |
| Week 6 | Multi-project: `tesqo switch`, `tesqo.toml`, workspace registry |
| Week 7 | First publish to TestPyPI, bug fixes |
| Week 8 | **v1.0.0 published to PyPI** |
| v1.1+ | Allure integration, watch mode, self-healing selectors |
| v2.0+ | AI-assisted test generation |

---

## Why Typer (not Click or argparse)?

| Feature | Typer | Click | argparse |
|---|---|---|---|
| Type hints → CLI flags automatically | ✅ | ❌ manual | ❌ manual |
| Automatic `--help` with types | ✅ | ✅ | ✅ |
| Built on Click (battle-tested) | ✅ | N/A | N/A |
| Autocompletion (bash/zsh/fish/PowerShell) | ✅ | ⚠️ plugin | ❌ |
| Rich output integration | ✅ native | ❌ | ❌ |
| Lines of code for same functionality | **~30%** | 100% | 150% |

---

## Immediate Next Steps (before full CLI)

These improvements work **right now** with zero restructuring:

1. **Add `testcase_registry.json`** — tracks all recorded tests, when last run, pass/fail history
2. **Add `testpilot.bat` shim** — allows `testpilot record`, `testpilot run` even before PyPI
3. **Add CI workflow** — `.github/workflows/test.yml` so PRs auto-run tests
4. **Add `setup.sh`** — Linux/Mac equivalent of `setup.bat`
5. **Add Allure** — `pytest tests/ --alluredir reports/allure-results && allure serve`
