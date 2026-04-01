"""
Table scanning, individual value checks, and pagination.
Edit selectors to match your actual app's table structure.
"""
import pytest
from playwright.sync_api import expect
from config.settings import config


@pytest.mark.regression
def test_all_rows_active_status(page):
    """Every row in the user table should have status = Active."""
    page.goto(config.BASE_URL + "/admin/users")
    rows = page.locator("table tbody tr")
    count = rows.count()
    assert count > 0, "User table is empty — nothing to check"

    for i in range(count):
        row = rows.nth(i)
        name   = row.locator("td:nth-child(1)").inner_text().strip()
        status = row.locator("td.status").inner_text().strip()
        assert status == "Active", f"User '{name}' has status '{status}' — expected 'Active'"


@pytest.mark.regression
def test_specific_user_role(page):
    """Find a row by username and assert its role column."""
    page.goto(config.BASE_URL + "/admin/users")
    row = page.locator("tr", has_text="John Doe")
    expect(row.locator("td.role")).to_have_text("Admin")


@pytest.mark.regression
def test_pagination_all_pages(page):
    """Loop through every page of a paginated table and check for Error status."""
    page.goto(config.BASE_URL + "/records")
    total_checked = 0

    while True:
        rows = page.locator("table tbody tr")
        row_count = rows.count()
        for i in range(row_count):
            status = rows.nth(i).locator(".status").inner_text().strip()
            assert status != "Error", (
                f"Row {total_checked + i + 1} has 'Error' status on page"
            )
        total_checked += row_count

        next_btn = page.locator("button.next-page, a[aria-label='Next page']")
        if not next_btn.is_visible() or next_btn.is_disabled():
            break
        next_btn.click()
        page.wait_for_load_state("networkidle")

    print(f"\n  ✅  Checked {total_checked} rows across all pages")


@pytest.mark.regression
def test_individual_field_assertions(page):
    """Spot-check individual values on a details page."""
    page.goto(config.BASE_URL + "/users/1")
    expect(page.locator("#user-status")).to_have_text("Active")
    expect(page.locator("#user-role")).not_to_have_text("Disabled")
    expect(page.locator("#edit-btn")).to_be_enabled()
    expect(page.locator("#delete-btn")).to_be_visible()
