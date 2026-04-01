import re
from playwright.sync_api import Page, expect
from config.settings import config
from pages.table_page import TablePage
import pytest

TABLE_URL = "https://www.w3schools.com/html/html_tables.asp"
TABLE_SEL = "#customers"
COUNTRY_COL_SEL = "td:nth-child(3)"   # Country is the 3rd column


@pytest.mark.smoke
def test_example(page: Page) -> None:
    page.goto(TABLE_URL)
    page.get_by_role("cell", name="Company").click(button="right")
    page.get_by_role("cell", name="Country").click()
    expect(page.locator(TABLE_SEL)).to_contain_text("Country")
    page.get_by_role("cell", name="Germany").click(button="right")
    page.get_by_role("cell", name="Germany").click()
    expect(page.locator(TABLE_SEL)).to_match_aria_snapshot("- cell \"Mexico\"")


@pytest.mark.smoke
def test_country_column_exists(page: Page) -> None:
    """Assert that a 'Country' header column is present in the table."""
    page.goto(TABLE_URL)
    headers = page.locator(f"{TABLE_SEL} th")
    header_texts = [headers.nth(i).inner_text().strip() for i in range(headers.count())]
    assert "Country" in header_texts, (
        f"Expected 'Country' column header but found: {header_texts}"
    )


@pytest.mark.smoke
def test_country_column_no_empty_values(page: Page) -> None:
    """Assert that every data row has a non-empty value in the Country column."""
    page.goto(TABLE_URL)
    # Use :has(td) to skip header rows that only contain <th> elements
    rows = page.locator(f"{TABLE_SEL} tbody tr:has(td)")
    row_count = rows.count()
    assert row_count > 0, "Table has no data rows"

    empty_rows = []
    for i in range(row_count):
        value = rows.nth(i).locator(COUNTRY_COL_SEL).inner_text().strip()
        if not value:
            empty_rows.append(i + 1)

    assert not empty_rows, (
        f"Rows with empty Country values: {empty_rows}"
    )
