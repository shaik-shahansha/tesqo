"""
Data-driven tests: reads rows from data/test_data.xlsx and runs the
same test once per row, parameterized automatically.
"""
import pytest
from playwright.sync_api import expect
from config.settings import config
from data.data_loader import load_excel

# Load at module level — rows are collected once before tests run
_ROWS = load_excel("data/test_data.xlsx", sheet="Login")


@pytest.mark.regression
@pytest.mark.parametrize("row", _ROWS, ids=[str(r.get("username", i)) for i, r in enumerate(_ROWS)])
def test_login_from_excel(page, row):
    """
    Each Excel row drives one test run.
    Columns expected: username | password | expected_role | should_pass
    """
    page.goto(config.BASE_URL + "/login")
    page.get_by_label("Username").fill(str(row["username"]))
    page.get_by_label("Password").fill(str(row["password"]))
    page.get_by_role("button", name="Sign in").click()

    if str(row.get("should_pass", "")).upper() in ("TRUE", "YES", "1"):
        expect(page.locator(".dashboard")).to_be_visible(timeout=8000)
        if row.get("expected_role"):
            expect(page.locator(".user-role")).to_have_text(str(row["expected_role"]))
    else:
        expect(page.locator(".error-alert")).to_be_visible(timeout=8000)
