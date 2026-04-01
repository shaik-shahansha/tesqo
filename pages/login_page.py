from playwright.sync_api import expect
from pages.base_page import BasePage
from config.settings import config


class LoginPage(BasePage):
    # Selectors — update to match your app
    SEL_USERNAME  = "[name='username'], #username, input[type='text']:first-of-type"
    SEL_PASSWORD  = "[name='password'], #password, input[type='password']"
    SEL_SUBMIT    = "button[type='submit'], button:has-text('Sign in'), button:has-text('Login')"
    SEL_ERROR     = ".error-alert, .alert-danger, [role='alert']"
    SEL_DASHBOARD = ".dashboard-header, #dashboard, [data-testid='dashboard']"

    def login(self, username: str = None, password: str = None) -> None:
        """Navigate to login page and submit credentials."""
        self.navigate("/login")
        self.page.fill(self.SEL_USERNAME, username or config.USERNAME)
        self.page.fill(self.SEL_PASSWORD, password or config.PASSWORD)
        self.page.click(self.SEL_SUBMIT)

    def assert_login_success(self) -> None:
        expect(self.page.locator(self.SEL_DASHBOARD)).to_be_visible(timeout=8000)

    def assert_login_error(self, contains: str = None) -> None:
        locator = self.page.locator(self.SEL_ERROR)
        expect(locator).to_be_visible(timeout=6000)
        if contains:
            expect(locator).to_contain_text(contains)

    def get_error_message(self) -> str:
        return self.get_text(self.SEL_ERROR)
