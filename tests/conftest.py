import os
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright
from config.settings import config


# ── Browser (shared across entire test session) ───────────────────────────────

@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser_type = getattr(p, config.BROWSER)
        browser = browser_type.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO,
            channel="msedge" if config.BROWSER == "msedge" else None,
        )
        yield browser
        browser.close()


# ── Page (fresh isolated context per test) ────────────────────────────────────

@pytest.fixture
def page(browser_instance):
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 720},
    )
    page = context.new_page()
    yield page
    context.close()


# ── Auto-screenshot on any test failure ───────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = item.name.replace("/", "_").replace(" ", "_").replace("::", "_")
            path = f"{config.SCREENSHOT_DIR}/{safe_name}_{timestamp}.png"
            try:
                page.screenshot(path=path, full_page=True)
                print(f"\n  📸  Screenshot: {path}")
            except Exception:
                pass  # never let screenshot failure break the report
