import re
from playwright.sync_api import Page, expect
from config.settings import config
import pytest


@pytest.mark.automation
def test_example(page: Page) -> None:
    page.goto(config.testcase1_url)
    page.get_by_role("searchbox", name="Search Amazon.in").click()
    page.get_by_role("searchbox", name="Search Amazon.in").fill("smartwatch")
    page.get_by_role("button", name="Go", exact=True).click()
    page.wait_for_load_state("networkidle")
    page.goto("https://www.amazon.in/Fire-Boltt-Bluetooth-Calling-Assistance-Resolution/dp/B0BF57RN3K/ref=sr_1_4?crid=1JY85CBY6Z8Y3&dib=eyJ2IjoiMSJ9.RtT-LqHLWem_r2ClinpK29OOBLOjfn58Uar_sZoJGA_O0oDuSWkAioHSixKkCg2I5MiL_Jse54YXZoWu9bYrdKQMmj0Dgna_Anto3a6th2DH8IdBkSH2RrUfhECBTBI-NeVmhRocQhjfbVS0ZSBbWV2AeOUBzP5jQB1pgVn7RLFlCf0Sg_cUk-VKcfZ06yKSrHVtYJKJXVXD0uhJEY-p4v98R-ccnqN9wVZKZ-2XySo.Iow2rXK6XYE2AsSmDFMUJR6Wgs6NhhJ_XSqL4sAHtFc&dib_tag=se&keywords=smartwatch&qid=1775022924&sprefix=smartwatch%2Caps%2C458&sr=8-4&th=1")
