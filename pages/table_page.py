from typing import Generator
from playwright.sync_api import Locator
from pages.base_page import BasePage


class TablePage(BasePage):
    """Generic helpers for HTML tables with optional pagination."""

    def __init__(self, page, table_selector: str = "table", path: str = ""):
        super().__init__(page)
        self._table_sel = table_selector
        self._path = path

    def open(self) -> None:
        if self._path:
            self.navigate(self._path)

    def rows(self) -> Locator:
        return self.page.locator(f"{self._table_sel} tbody tr")

    def row_count(self) -> int:
        return self.rows().count()

    def get_cell(self, row_index: int, col_selector: str) -> str:
        """Get the text of a specific cell in a row."""
        return self.rows().nth(row_index).locator(col_selector).inner_text().strip()

    def find_row_by_text(self, text: str) -> Locator:
        """Return the first row that contains the given text."""
        return self.page.locator(f"{self._table_sel} tbody tr", has_text=text)

    def iter_rows(self) -> Generator[Locator, None, None]:
        """Yield each row locator (current page only)."""
        count = self.row_count()
        for i in range(count):
            yield self.rows().nth(i)

    def iter_all_pages(
        self,
        next_selector: str = "button.next-page, a[aria-label='Next page']",
    ) -> Generator[Locator, None, None]:
        """Yield every row locator across all pages, clicking Next automatically."""
        while True:
            yield from self.iter_rows()
            next_btn = self.page.locator(next_selector)
            if not next_btn.is_visible() or next_btn.is_disabled():
                break
            next_btn.click()
            self.page.wait_for_load_state("networkidle")

    def assert_column_value(self, col_selector: str, expected: str) -> None:
        """Assert that every row's column matches the expected value."""
        count = self.row_count()
        assert count > 0, f"Table '{self._table_sel}' has no rows"
        for i in range(count):
            actual = self.get_cell(i, col_selector)
            assert actual == expected, (
                f"Row {i + 1}: expected '{expected}', got '{actual}'"
            )
