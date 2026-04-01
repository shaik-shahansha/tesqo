# 🧪 Tesqo

> **Automate your web tests with ease — Record, Run & Report.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.51%2B-green)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red)]()

**Tesqo** is a batteries-included web test automation framework built on **Playwright + pytest**.
Designed for testers, developers, and QA engineers who want to go from zero to a full
regression suite with minimal setup and zero boilerplate.

---

## ✨ Why Tesqo?

| Pain point | Tesqo solution |
|---|---|
| "Tests are hard to write" | Record in browser → code is generated → minimal edits needed |
| "Secrets end up in test code" | `.env` file — BASE_URL, credentials never touch test files |
| "Running tests is confusing" | Interactive `run.bat` menu — no pytest flags to memorise |
| "Data-driven tests need coding" | Point at an Excel file — rows become test cases automatically |
| "I don't know what failed" | HTML report + screenshots auto-captured on every failure |
| "Works on my machine" | Chrome and Edge both supported — same test, one flag |
| "I'm on Mac/Linux, not Windows" | `setup.sh` + `Makefile` — same workflow on all platforms |
| "Tables / pagination are hard" | Built-in `TablePage` helper iterates all rows across all pages |
| "Setup takes forever" | One command (`setup.bat` / `setup.sh` / `make setup`) installs everything |

---

## 🚀 Quick Start (5 minutes)

**Windows**
```bat
:: 1. Clone / download the project
git clone https://github.com/yourusername/tesqo.git
cd tesqo

:: 2. First-time setup (creates venv, installs deps, installs browsers)
setup.bat

:: 3. Edit .env with your app's URL and credentials
notepad .env

:: 4. Record your first test
record.bat

:: 5. Run everything and see the report
run.bat
```

**macOS / Linux**
```bash
# 1. Clone / download the project
git clone https://github.com/yourusername/tesqo.git
cd tesqo

# 2. First-time setup
bash setup.sh          # or: make setup

# 3. Edit .env
nano .env              # or: open .env (macOS)

# 4. Record your first test
make record

# 5. Run everything and see the report
make run
```

**Any platform — Makefile shortcuts**
```bash
make setup        # first-time setup
make smoke        # run smoke tests
make regression   # run regression tests
make record       # launch recorder
make run          # interactive runner menu
make report       # open last HTML report
make help         # list all targets
```

That's it. No pytest knowledge required to get started.

---

## 📋 Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | https://python.org |
| Node.js | Not required | — |
| Chrome or Edge | Any modern | Pre-installed on most systems |
| make | Any | Pre-installed on macOS/Linux; Windows: [Git Bash](https://gitforwindows.org/) or [Chocolatey](https://chocolatey.org/) `choco install make` |

---

## 📁 Project Structure

```
tesqo/
│
├── .env                    ← 🔐 Your secrets (never commit this)
├── .env.example            ← Template — safe to commit
├── setup.bat               ← One-time first-run setup (Windows)
├── setup.sh                ← One-time first-run setup (macOS/Linux)
├── Makefile                ← Universal commands for all platforms
├── record.bat              ← Smart recorder launcher (Windows)
├── run.bat                 ← Interactive test runner menu (Windows)
├── pytest.ini              ← pytest config and markers
├── requirements.txt        ← All dependencies pinned
│
├── config/
│   └── settings.py         ← Loads .env, typed Config object
│
├── data/
│   ├── test_data.xlsx      ← Excel: data rows → test cases
│   ├── data_loader.py      ← Reads Excel → list of dicts
│   └── create_sample_data.py  ← Bootstraps sample Excel file
│
├── tests/
│   ├── conftest.py         ← Browser/page fixtures, auto-screenshot on fail
│   ├── smoke/              ← @pytest.mark.smoke — quick sanity tests
│   ├── regression/         ← @pytest.mark.regression — full suite
│   └── automation/         ← @pytest.mark.automation — state-changing scripts
│
├── pages/                  ← Page Object Model (reusable page helpers)
│   ├── base_page.py
│   ├── login_page.py
│   └── table_page.py
│
├── reports/
│   ├── html/               ← HTML reports (auto-generated)
│   └── screenshots/        ← Auto-captured on test failure
│
└── scripts/
    ├── record.py           ← Smart recorder (prompts → records → auto-saves)
    └── run.py              ← Interactive runner menu
```

---

## ⚙️ Configuration (.env)

```ini
# Application
BASE_URL=https://myapp.com
USERNAME=admin
PASSWORD=secret123
API_URL=https://api.myapp.com

# Browser  (chromium | msedge)
BROWSER=chromium
HEADLESS=false
SLOW_MO=0          # milliseconds between actions — useful for demos/debugging
```

All test files access config via:
```python
from config.settings import config

page.goto(config.BASE_URL + "/login")
page.fill("#user", config.USERNAME)
```

Secrets never appear hardcoded in test files.

---

## 🎬 Recording Tests

Run `record.bat` (Windows), `make record` (any platform), or `python scripts/record.py` and answer three questions:

```
  ╔══════════════════════════════════════╗
  ║    Tesqo — Smart Recorder            ║
  ╚══════════════════════════════════════╝

  Test name (e.g. login_as_admin): login_admin
  URL to record on [https://myapp.com]: 
  Category (smoke | regression | automation) [regression]: smoke
```

The browser opens at your URL. **Just interact normally** — click, type, navigate.
Close the browser when done. Tesqo automatically:

- Replaces `https://myapp.com` → `config.BASE_URL`
- Replaces `"admin"` → `config.USERNAME`
- Replaces `"secret123"` → `config.PASSWORD`
- Adds `import pytest` and `from config.settings import config`
- Adds `@pytest.mark.smoke` to every test function
- Saves to `tests/smoke/test_login_admin.py`
- Prints the exact command to run it immediately

Minimal editing needed — usually just fixing selectors.

---

## ▶️ Running Tests

Run `run.bat` (Windows) or `make run` (any platform) for the interactive menu:

```
  ╔══════════════════════════════════════╗
  ║    Tesqo — Runner                    ║
  ╠══════════════════════════════════════╣
  ║  1.  Run ALL tests                   ║
  ║  2.  Run SMOKE tests                 ║
  ║  3.  Run REGRESSION tests            ║
  ║  4.  Run AUTOMATION scripts          ║
  ║  5.  Run a SINGLE test file          ║
  ║  6.  Run a SINGLE test function      ║
  ║  7.  Record a NEW test               ║
  ║  8.  Open last report                ║
  ║  0.  Exit                            ║
  ╚══════════════════════════════════════╝
```

**Browser choice** is asked for every run: Chrome (1), Edge (2), or Both in parallel (3).

### Command-line equivalents
```bash
# Run all tests
pytest tests/

# Smoke tests only  
pytest tests/ -m smoke

# Regression only
pytest tests/ -m regression

# One file
pytest tests/smoke/test_login.py -v

# One specific test
pytest tests/smoke/test_login.py::test_login_success -v

# Headed browser (visible)
pytest tests/ --headed

# On Edge
pytest tests/ --browser msedge

# Both browsers in parallel
pytest tests/ --browser chromium --browser msedge -n auto

# Slow down for debugging
pytest tests/ --headed --slowmo 1000
```

---

## 📊 Reports

HTML reports are auto-generated after every run at `reports/html/report.html`.
Open via `run.bat → Option 8` or double-click the file.

The report includes:
- ✅ / ❌ per test with duration
- Full error messages and tracebacks
- Embedded screenshots (auto-captured on every failure)
- Environment info

**Screenshots** are saved to `reports/screenshots/` on every test failure, named:
```
test_login_wrong_password_20260401_143022.png
```

---

## 📊 Excel Data-Driven Tests

Place test inputs in `data/test_data.xlsx`:

| username | password | expected_role | should_pass |
|---|---|---|---|
| alice | pass_alice | Admin | TRUE |
| bob | pass_bob | User | TRUE |
| hacker | wrong | | FALSE |

Then parametrize in a test:

```python
from data.data_loader import load_excel

rows = load_excel("data/test_data.xlsx", sheet="Login")

@pytest.mark.parametrize("row", rows, ids=[r["username"] for r in rows])
def test_login_from_excel(page, row):
    page.goto(config.BASE_URL + "/login")
    page.fill("#username", str(row["username"]))
    page.fill("#password", str(row["password"]))
    page.click("button[type='submit']")

    if str(row["should_pass"]).upper() in ("TRUE", "YES", "1"):
        expect(page.locator(".dashboard")).to_be_visible()
    else:
        expect(page.locator(".error-alert")).to_be_visible()
```

Each row becomes a separate test case in the report. Named `[alice]`, `[bob]`, etc.

---

## 🔁 Common Test Patterns

### Check every row in a table

```python
rows = page.locator("table tbody tr")
for i in range(rows.count()):
    status = rows.nth(i).locator(".status").inner_text().strip()
    assert status == "Active", f"Row {i+1} status is '{status}'"
```

### Loop through paginated table (Next button)

```python
while True:
    for row in page.locator("table tbody tr").all():
        assert row.locator(".status").inner_text() != "Error"
    next_btn = page.locator("button.next-page")
    if not next_btn.is_visible() or next_btn.is_disabled():
        break
    next_btn.click()
    page.wait_for_load_state("networkidle")
```

### Conditional automation (act on web data)

```python
rows = page.locator("table tbody tr")
for i in range(rows.count()):
    row = rows.nth(i)
    if row.locator(".status").inner_text() == "Inactive":
        row.locator("button.activate").click()
        page.wait_for_selector(".toast-success")
```

### Wait, exist, enabled, disabled checks

```python
expect(page.locator("#submit")).to_be_visible()
expect(page.locator("#submit")).to_be_enabled()
expect(page.locator(".spinner")).to_be_hidden()
expect(page.locator("#status")).to_have_text("Active")
expect(page.locator(".error")).not_to_be_visible()
```

---

## 🗂️ Markers (Test Categories)

| Marker | Purpose | When to run |
|---|---|---|
| `@pytest.mark.smoke` | Critical path — login, core navigation | Every deploy |
| `@pytest.mark.regression` | Full feature coverage | Before every release |
| `@pytest.mark.automation` | State-changing scripts (activate, bulk update) | On demand |
| `@pytest.mark.slow` | Tests taking >30 seconds | Nightly |

---

## 🌐 Multi-Browser Support

| Browser | Flag | Notes |
|---|---|---|
| Chrome (Chromium) | `--browser chromium` | Default |
| Microsoft Edge | `--browser msedge` | Set in `.env`: `BROWSER=msedge` |
| Both (parallel) | `--browser chromium --browser msedge -n auto` | Requires `pytest-xdist` |
| Headed (visible) | `--headed` | Good for debugging |
| Headless (CI) | `HEADLESS=true` in `.env` | Faster, no display needed |

---

## 🧩 Page Object Model

Tesqo ships with a `BasePage` and `TablePage` helper so tests stay clean:

```python
from pages.login_page import LoginPage
from config.settings import config

def test_login(page):
    lp = LoginPage(page)
    lp.login(config.USERNAME, config.PASSWORD)
    lp.assert_login_success()
```

```python
from pages.table_page import TablePage

def test_all_active(page):
    tbl = TablePage(page, table_selector="table#users", path="/admin/users")
    tbl.open()
    for row in tbl.iter_all_pages():           # handles pagination automatically
        status = row.locator(".status").inner_text()
        assert status == "Active"
```

Create new page objects by extending `BasePage`:
```python
from pages.base_page import BasePage

class DashboardPage(BasePage):
    def go(self):
        self.navigate("/dashboard")
    def get_welcome_text(self):
        return self.get_text(".welcome-header")
```

---

## 🛠️ Tech Stack

| Component | Library | Version |
|---|---|---|
| Browser automation | [Playwright](https://playwright.dev/python/) | 1.51+ |
| Test runner | [pytest](https://pytest.org) | 8.3+ |
| Playwright integration | [pytest-playwright](https://pypi.org/project/pytest-playwright/) | 0.7+ |
| HTML reports | [pytest-html](https://pypi.org/project/pytest-html/) | 4.1+ |
| Parallel execution | [pytest-xdist](https://pypi.org/project/pytest-xdist/) | 3.6+ |
| Excel data input | [openpyxl](https://pypi.org/project/openpyxl/) | 3.1+ |
| Environment secrets | [python-dotenv](https://pypi.org/project/python-dotenv/) | 1.0+ |

All open source. No paid services required.

---

## 📦 Installation from Scratch

```bash
# Clone
git clone https://github.com/yourusername/tesqo.git
cd tesqo

# Windows — one command
setup.bat

# macOS / Linux — one command
bash setup.sh

# Any platform with make
make setup

# Manual
python3 -m venv .venv
source .venv/bin/activate           # macOS/Linux
.venv\Scripts\activate              # Windows cmd
pip install -r requirements.txt
playwright install chromium msedge
cp .env.example .env                # macOS/Linux
copy .env.example .env              # Windows cmd
python data/create_sample_data.py
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-improvement`
3. Add tests for your changes
4. Open a pull request

All contributions welcome — new page helpers, CI integrations, report themes, etc.

---

## 📄 License

MIT — free to use, fork, and distribute.

---

## 🌟 Roadmap

See [ROADMAP.md](ROADMAP.md) for the plan to evolve Tesqo into a fully installable CLI
package (`pip install tesqo`) with multi-project workspace support.

---

*Built with ❤️ for testers who believe web automation should be easy — record it, run it, ship it.*
