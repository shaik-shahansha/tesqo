"""
Automation: find Inactive users in a table and click Activate on each.
This is a state-changing automation, not a read-only test.
Run with:  pytest tests/automation/ -m automation -v
"""
import pytest
from config.settings import config


@pytest.mark.automation
def test_activate_all_inactive_users(page):
    """
    Scan the user table, find every row with status='Inactive',
    click its Activate button, and wait for the success toast.
    """
    page.goto(config.BASE_URL + "/admin/users")
    activated = []

    rows = page.locator("table tbody tr")
    for i in range(rows.count()):
        row = rows.nth(i)
        status = row.locator(".status").inner_text().strip()
        if status == "Inactive":
            name = row.locator("td:nth-child(1)").inner_text().strip()
            row.locator("button.activate").click()
            # Wait for toast confirmation, then wait for it to disappear
            page.wait_for_selector(".toast-success", timeout=6000)
            page.locator(".toast-success").wait_for(state="hidden", timeout=6000)
            activated.append(name)
            print(f"  ✅  Activated: {name}")

    print(f"\n  Total activated: {len(activated)}")
    if not activated:
        print("  ℹ  No inactive users found — nothing to activate.")
