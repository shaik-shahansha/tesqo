import re
from playwright.sync_api import Page, expect
from config.settings import config
import pytest


@pytest.mark.smoke
def test_example(page: Page) -> None:
    page.goto("https://shahansha.com/")
    page.get_by_label("Main Menu", exact=True).get_by_role("link", name="About").click()
    page.get_by_label("Main Menu", exact=True).get_by_role("link", name="AI Apps").click()
    page.get_by_label("Main Menu", exact=True).get_by_role("link", name="Contact").click()
    page.get_by_role("textbox", name="Name *").click()
    page.get_by_role("textbox", name="Name *").fill("test")
    page.get_by_role("textbox", name="Email *").click()
    page.get_by_role("textbox", name="Email *").fill("t@t.com")
    page.get_by_role("textbox", name="How can we help? *").click()
    page.get_by_role("textbox", name="How can we help? *").fill("test")
    page.get_by_role("button", name="Let's Talk").click()
