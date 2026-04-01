"""
Example smoke test — login scenarios.
Generated via: record.bat  (then auto-processed by scripts/record.py)
Edit selectors to match your actual app.
"""
import pytest
from playwright.sync_api import expect
from config.settings import config


@pytest.mark.smoke
def test_login_success(page):
    """Happy path: valid credentials should reach the dashboard."""
    page.goto(config.BASE_URL + "/login")
    page.get_by_label("Username").fill(config.USERNAME)
    page.get_by_label("Password").fill(config.PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page.locator(".dashboard-header")).to_be_visible()


@pytest.mark.smoke
def test_login_wrong_password(page):
    """Wrong password should show an error message."""
    page.goto(config.BASE_URL + "/login")
    page.get_by_label("Username").fill(config.USERNAME)
    page.get_by_label("Password").fill("wrong_password_intentional")
    page.get_by_role("button", name="Sign in").click()
    expect(page.locator(".error-alert")).to_be_visible()
    expect(page.locator(".error-alert")).to_contain_text("Invalid")


@pytest.mark.smoke
def test_login_page_elements(page):
    """Login page should have all required fields and the submit button enabled."""
    page.goto(config.BASE_URL + "/login")
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
    expect(page.get_by_role("button", name="Sign in")).to_be_enabled()
