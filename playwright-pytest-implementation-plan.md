# PyPlaywright Studio — Implementation Plan
> Playwright + pytest | Python | Chrome + Edge | Smart Record → Auto-Save → Run → Report
> **Design principle: Zero manual steps. Everything prompted, automated, and saved.**

---

## Final Project Structure

```
testframework/
│
├── .env                          # Secrets: BASE_URL, USERNAME, PASSWORD etc. (gitignored)
├── .env.example                  # Safe template to commit to git
├── .gitignore
├── pytest.ini                    # pytest config: markers, output, browser
├── requirements.txt
│
├── config/
│   └── settings.py               # Loads .env, exposes typed config object
│
├── data/
│   ├── test_data.xlsx            # Excel: data-driven test rows
│   └── data_loader.py            # Reads Excel → list of dicts for parametrize
│
├── tests/
│   ├── conftest.py               # Browser/page fixtures, auto-screenshot on fail
│   ├── smoke/                    # ← recorded tests auto-saved here (category=smoke)
│   │   └── test_login.py
│   ├── regression/               # ← recorded tests auto-saved here (category=regression)
│   │   ├── test_user_table.py
│   │   └── test_data_driven.py
│   └── automation/               # ← recorded tests auto-saved here (category=automation)
│       └── test_bulk_activate.py
│
├── pages/                        # Page Object Model — reusable page helpers
│   ├── base_page.py
│   ├── login_page.py
│   └── table_page.py
│
├── reports/
│   ├── html/                     # Auto-generated HTML reports
│   ├── allure-results/           # Allure raw results (optional)
│   └── screenshots/              # Auto-captured on any test failure
│
└── scripts/
    ├── record.py                 # ⭐ Smart recorder: prompts → records → auto-processes → saves
    ├── run.py                    # ⭐ Smart runner: interactive menu → run → open report
    ├── record.bat                # Thin wrapper: python scripts/record.py
    └── run.bat                   # Thin wrapper: python scripts/run.py
```

---

## Phase 1 — Setup & Scaffolding

### Step 1.1 — Install prerequisites
```bash
# Python 3.11+ required
python --version

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows

# Install all dependencies
pip install -r requirements.txt

# Install browsers (Chromium + Edge)
playwright install chromium msedge
```

### Step 1.2 — requirements.txt
```txt
playwright==1.51.0
pytest==8.3.5
pytest-playwright==0.7.0
pytest-html==4.1.1
pytest-xdist==3.6.1
allure-pytest==2.13.5
python-dotenv==1.0.1
openpyxl==3.1.3
pandas==2.2.3
```

### Step 1.3 — .env file (never commit — add to .gitignore)
```ini
BASE_URL=https://myapp.com
USERNAME=admin
PASSWORD=secret123
API_URL=https://api.myapp.com
BROWSER=chromium
HEADLESS=false
SLOW_MO=0
```

### Step 1.4 — .env.example (commit this instead)
```ini
BASE_URL=https://
USERNAME=
PASSWORD=
API_URL=
BROWSER=chromium
HEADLESS=false
SLOW_MO=0
```

### Step 1.5 — config/settings.py
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_URL   = os.getenv("BASE_URL", "http://localhost")
    USERNAME   = os.getenv("USERNAME", "")
    PASSWORD   = os.getenv("PASSWORD", "")
    API_URL    = os.getenv("API_URL", "")
    BROWSER    = os.getenv("BROWSER", "chromium")
    HEADLESS   = os.getenv("HEADLESS", "false").lower() == "true"
    SLOW_MO    = int(os.getenv("SLOW_MO", "0"))
    SCREENSHOT_DIR = "reports/screenshots"
    REPORT_DIR     = "reports/html"

config = Config()
```

### Step 1.6 — pytest.ini
```ini
[pytest]
addopts =
    --html=reports/html/report.html
    --self-contained-html
    --tb=short
    -v

markers =
    smoke:      Quick sanity checks - run on every deploy
    regression: Full regression suite
    automation: Automation scripts (not pure tests)
    slow:       Tests that take >30s

testpaths = tests
```

---

## Phase 2 — Core Fixtures (conftest.py)

```python
# tests/conftest.py
import os
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright
from config.settings import config

# ── Browser fixture ───────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser_type = getattr(p, config.BROWSER)          # chromium / msedge
        browser = browser_type.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO,
            channel="msedge" if config.BROWSER == "msedge" else None,
        )
        yield browser
        browser.close()

# ── Page fixture — fresh page per test ────────────────────────────────────────
@pytest.fixture
def page(browser_instance):
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 720},
        record_video_dir="reports/videos/" if not config.HEADLESS else None,
    )
    page = context.new_page()
    yield page
    context.close()

# ── Screenshot on failure ─────────────────────────────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = item.name.replace("/", "_").replace(" ", "_")
            path = f"{config.SCREENSHOT_DIR}/{name}_{timestamp}.png"
            page.screenshot(path=path, full_page=True)
            print(f"\n📸 Screenshot saved: {path}")
```

---

## Phase 3 — Smart Recorder (scripts/record.py)

There is **zero manual file management**. Run `record.bat`, answer three prompts, record, close the browser — done.

### What the smart recorder does automatically
1. Prompts for **test name**, **URL** (defaults to `.env` BASE_URL), **category** (smoke/regression/automation)
2. Launches `playwright codegen` — browser opens, you interact naturally
3. When browser is closed, auto-processes the generated code:
   - Replaces hardcoded `BASE_URL` with `config.BASE_URL`
   - Replaces hardcoded username/password with `config.USERNAME` / `config.PASSWORD`
   - Adds `import pytest` and `from config.settings import config`
   - Adds `@pytest.mark.<category>` to every test function
4. Saves directly to `tests/<category>/test_<name>.py`
5. Prints exact command to run the test immediately

### Usage — one command
```bat
record.bat
```
```
╔══════════════════════════════════════╗
║    PyPlaywright Studio — Recorder    ║
╚══════════════════════════════════════╝

  Test case name (e.g. login_admin_user): login_as_admin
  URL to record on [https://myapp.com]: 
  Category (smoke/regression/automation) [regression]: smoke

  🎬 Opening browser at: https://myapp.com
  → Interact with the page. Close the browser window when done.

  ✅ Test saved!
     File   : tests/smoke/test_login_as_admin.py
     Marker : @pytest.mark.smoke

  ▶ Run this test now:
     pytest tests/smoke/test_login_as_admin.py -v --headed
```

### Before / After — what gets auto-fixed
```python
# BEFORE (raw codegen output)
from playwright.sync_api import Page, expect

def test_example(page: Page) -> None:
    page.goto("https://myapp.com/login")
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("secret123")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Dashboard")).to_be_visible()

# AFTER (auto-processed by record.py)
import pytest
from playwright.sync_api import Page, expect
from config.settings import config

@pytest.mark.smoke
def test_example(page: Page) -> None:
    page.goto(config.BASE_URL + "/login")
    page.get_by_label("Username").fill(config.USERNAME)
    page.get_by_label("Password").fill(config.PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Dashboard")).to_be_visible()
```

> **Minimal edits needed after recording:** Only change selectors if they are fragile (e.g. replace auto-generated `nth-child` with semantic `get_by_role`). Everything else is ready to run.

---

## Phase 4 — Test Examples

### Login test (smoke)
```python
# tests/smoke/test_login.py
import pytest
from config.settings import config
from playwright.sync_api import expect

@pytest.mark.smoke
def test_login_success(page):
    page.goto(config.BASE_URL + "/login")
    page.fill("#username", config.USERNAME)
    page.fill("#password", config.PASSWORD)
    page.click("button[type='submit']")
    expect(page.locator(".dashboard-header")).to_be_visible()

@pytest.mark.smoke
def test_login_wrong_password(page):
    page.goto(config.BASE_URL + "/login")
    page.fill("#username", config.USERNAME)
    page.fill("#password", "wrongpass")
    page.click("button[type='submit']")
    expect(page.locator(".error-alert")).to_contain_text("Invalid")
```

### Table scan + individual value checks
```python
# tests/regression/test_user_table.py
import pytest
from config.settings import config
from playwright.sync_api import expect

@pytest.mark.regression
def test_all_users_have_active_status(page):
    page.goto(config.BASE_URL + "/admin/users")
    rows = page.locator("table tbody tr")
    count = rows.count()
    assert count > 0, "Table is empty"

    for i in range(count):
        row = rows.nth(i)
        name   = row.locator("td:nth-child(1)").inner_text()
        status = row.locator("td.status").inner_text().strip()
        assert status == "Active", f"User '{name}' has status '{status}', expected 'Active'"

@pytest.mark.regression
def test_specific_user_role(page):
    page.goto(config.BASE_URL + "/admin/users")
    row = page.locator("tr", has_text="John Doe")
    expect(row.locator("td.role")).to_have_text("Admin")
```

### Table with pagination (Next button)
```python
@pytest.mark.regression
def test_all_records_across_pages(page):
    page.goto(config.BASE_URL + "/records")
    checked_rows = 0

    while True:
        rows = page.locator("table tbody tr")
        for i in range(rows.count()):
            status = rows.nth(i).locator(".status").inner_text().strip()
            assert status != "Error", f"Row {checked_rows + i} has Error status"
        checked_rows += rows.count()

        next_btn = page.locator("button.next-page")
        if not next_btn.is_visible() or next_btn.is_disabled():
            break
        next_btn.click()
        page.wait_for_load_state("networkidle")

    print(f"Checked {checked_rows} total rows across all pages")
```

### Conditional automation (act on live web data)
```python
# tests/automation/test_bulk_activate.py
import pytest
from config.settings import config

@pytest.mark.automation
def test_activate_all_inactive_users(page):
    page.goto(config.BASE_URL + "/admin/users")
    activated = 0

    rows = page.locator("table tbody tr")
    for i in range(rows.count()):
        row = rows.nth(i)
        status = row.locator(".status").inner_text().strip()
        if status == "Inactive":
            name = row.locator("td:nth-child(1)").inner_text()
            row.locator("button.activate").click()
            page.wait_for_selector(".toast-success")
            page.locator(".toast-success").wait_for(state="hidden")
            activated += 1
            print(f"  ✅ Activated: {name}")

    print(f"\nTotal activated: {activated}")
```

---

## Phase 5 — Excel Data-Driven Tests

### data/data_loader.py
```python
import openpyxl

def load_excel(filepath: str, sheet: str = None) -> list[dict]:
    """Load an Excel sheet and return a list of row dicts."""
    wb = openpyxl.load_workbook(filepath)
    ws = wb[sheet] if sheet else wb.active
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if any(cell is not None for cell in row):          # skip blank rows
            rows.append(dict(zip(headers, row)))
    return rows
```

### Excel file format (data/test_data.xlsx)
| username | password | expected_role | should_pass |
|---|---|---|---|
| alice | pass1 | Admin | TRUE |
| bob | pass2 | User | TRUE |
| hacker | wrong | — | FALSE |

### Excel-driven test
```python
# tests/regression/test_data_driven.py
import pytest
from data.data_loader import load_excel
from config.settings import config
from playwright.sync_api import expect

TEST_ROWS = load_excel("data/test_data.xlsx", sheet="Login")

@pytest.mark.regression
@pytest.mark.parametrize("row", TEST_ROWS, ids=[r["username"] for r in TEST_ROWS])
def test_login_from_excel(page, row):
    page.goto(config.BASE_URL + "/login")
    page.fill("#username", str(row["username"]))
    page.fill("#password", str(row["password"]))
    page.click("button[type='submit']")

    if row["should_pass"]:
        expect(page.locator(".dashboard")).to_be_visible()
        expect(page.locator(".user-role")).to_have_text(row["expected_role"])
    else:
        expect(page.locator(".error-alert")).to_be_visible()
```

---

## Phase 6 — Page Object Model (Reusable Pages)

### pages/base_page.py
```python
from playwright.sync_api import Page
from config.settings import config

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, path: str = ""):
        self.page.goto(config.BASE_URL + path)

    def screenshot(self, name: str):
        self.page.screenshot(path=f"{config.SCREENSHOT_DIR}/{name}.png", full_page=True)

    def wait_for(self, selector: str, timeout: int = 10000):
        self.page.wait_for_selector(selector, timeout=timeout)
```

### pages/login_page.py
```python
from pages.base_page import BasePage

class LoginPage(BasePage):
    USERNAME = "#username"
    PASSWORD = "#password"
    SUBMIT   = "button[type='submit']"
    ERROR    = ".error-alert"
    DASHBOARD= ".dashboard-header"

    def login(self, username: str, password: str):
        self.navigate("/login")
        self.page.fill(self.USERNAME, username)
        self.page.fill(self.PASSWORD, password)
        self.page.click(self.SUBMIT)

    def get_error(self) -> str:
        return self.page.locator(self.ERROR).inner_text()
```

### Using Page Objects in tests
```python
from pages.login_page import LoginPage
from config.settings import config

def test_login(page):
    login = LoginPage(page)
    login.login(config.USERNAME, config.PASSWORD)
    login.wait_for(LoginPage.DASHBOARD)
```

---

## Phase 7 — Smart Runner (scripts/run.py)

One command gives you an interactive menu — no memorizing pytest flags.

```bat
run.bat
```
```
╔══════════════════════════════════════╗
║    PyPlaywright Studio — Runner      ║
╠══════════════════════════════════════╣
║  1. Run ALL tests                    ║
║  2. Run SMOKE tests                  ║
║  3. Run REGRESSION tests             ║
║  4. Run AUTOMATION scripts           ║
║  5. Run a SINGLE test file           ║
║  6. Record a NEW test                ║
║  7. Open last report                 ║
║  0. Exit                             ║
╚══════════════════════════════════════╝

  Choose (0-7): 5

  Available test files:
    1. tests/smoke/test_login_as_admin.py
    2. tests/regression/test_user_table.py
    3. tests/automation/test_bulk_activate.py

  Enter number or file path: 1

  Browser: 1=Chrome  2=Edge  [Enter=Chrome]
  Choose: 2

  → pytest reports saved and opened automatically
```

### Batch scripts (still available for CI/automation)
```bat
rem Run all tests headlessly on both browsers
pytest tests\ --browser chromium --browser msedge -n auto

rem Just smoke on Edge
pytest tests\ -m smoke --browser msedge -v
```

---

## Phase 8 — Reports

### pytest-html (default, zero config)
- Auto-generated at `reports/html/report.html` after every run
- Single self-contained HTML file — no server needed, share via email
- Shows: pass/fail per test, duration, error message, stdout logs
- Screenshots automatically embedded when captured in `conftest.py`

### Allure (richer dashboard — optional)
```bash
# Install Allure CLI (once)
# Windows: download from https://github.com/allure-framework/allure2/releases

# Run with Allure output
pytest tests\ --alluredir=reports/allure-results

# Open Allure dashboard
allure serve reports/allure-results
```

Allure gives you: trend graphs, test history, flaky test tracking, categorized failures.

---

## Phase 9 — Run on Both Chrome + Edge

### Option A: Run sequentially (two separate runs)
```bash
pytest tests\ -m smoke --browser chromium
pytest tests\ -m smoke --browser msedge
```

### Option B: Run in parallel on both browsers (fastest)
```bash
# Install pytest-xdist (already in requirements.txt)
pytest tests\ -m smoke --browser chromium --browser msedge -n auto
```

### Option C: Parametrize browser in conftest.py
```python
# In conftest.py — run every test on both browsers automatically
def pytest_generate_tests(metafunc):
    if "browser_name" in metafunc.fixturenames:
        metafunc.parametrize("browser_name", ["chromium", "msedge"])
```

---

## Implementation Sequence (Day by Day)

| Day | Task | Output |
|---|---|---|
| **Day 1** | Install deps, scaffold folders, `.env`, `settings.py`, `pytest.ini` | Working skeleton |
| **Day 1** | Write `conftest.py` with browser fixture + screenshot-on-fail hook | Fixtures ready |
| **Day 2** | Record first test with `playwright codegen`, clean it up, run it | First passing test |
| **Day 2** | Write `run_all.bat`, `run_smoke.bat`, verify HTML report generates | Batch runs work |
| **Day 3** | Create `test_data.xlsx`, write `data_loader.py`, write parametrized test | Excel-driven tests |
| **Day 3** | Write table scan test + pagination test | Regression tests |
| **Day 4** | Write automation test (conditional act on web data) | Automation scripts |
| **Day 4** | Add Page Object Model layer for reuse (`login_page.py`, `table_page.py`) | Reusable pages |
| **Day 5** | Add Edge browser run, test both, verify reports | Cross-browser coverage |
| **Day 5** | Polish: markers, Allure setup, clean up scripts | Production ready |

---

## Quick Reference Card

```bash
# ── Recording ────────────────────────────────────────────────
record.bat                          # Smart record: prompts → records → auto-saves

# ── Running (interactive menu) ───────────────────────────────
run.bat                             # Menu: pick suite, browser, opens report

# ── Running (direct commands) ────────────────────────────────
pytest tests\                       # All tests
pytest tests\ -m smoke              # Smoke only
pytest tests\ -m regression         # Regression only
pytest tests\smoke\test_login.py    # Single file
pytest tests\smoke\test_login.py::test_login_success  # Single test

# ── Browser ──────────────────────────────────────────────────
pytest tests\ --browser chromium    # Chrome
pytest tests\ --browser msedge      # Edge
pytest tests\ --browser chromium --browser msedge -n auto  # Both in parallel

# ── Debug ────────────────────────────────────────────────────
pytest tests\ --headed              # Visible browser
pytest tests\ --headed --slowmo 800 # Slow motion (ms)
pytest tests\ --tracing on          # Record trace for pw show-trace
playwright show-trace trace.zip     # View step-by-step trace

# ── Reports ──────────────────────────────────────────────────
start reports\html\report.html      # Open last HTML report
allure serve reports\allure-results # Open Allure dashboard (optional)
```
