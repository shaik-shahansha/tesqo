from playwright.sync_api import Page
from config.settings import config
import os


class BasePage:
    """Shared helpers available to all page objects."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, path: str = "") -> None:
        self.page.goto(config.BASE_URL + path)
        self.page.wait_for_load_state("networkidle")

    def wait_for(self, selector: str, timeout: int = 10_000) -> None:
        self.page.wait_for_selector(selector, timeout=timeout)

    def screenshot(self, name: str) -> None:
        os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
        self.page.screenshot(
            path=f"{config.SCREENSHOT_DIR}/{name}.png",
            full_page=True,
        )

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text().strip()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def is_enabled(self, selector: str) -> bool:
        return self.page.locator(selector).is_enabled()
