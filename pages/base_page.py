import re
from decimal import Decimal

import allure
from playwright.sync_api import Page

from pages.components.header import Header

_MONEY = re.compile(r"\$\s*(\d+(?:\.\d+)?)")


def parse_money(text: str) -> Decimal:
    """Extract the amount from strings like '$29.99' or 'Item total: $121.95'."""
    match = _MONEY.search(text)
    if not match:
        raise ValueError(f"No price found in {text!r}")
    return Decimal(match.group(1))


class BasePage:
    """Common behaviour for all pages. Locators use the app's `data-test` attributes."""

    PATH = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)
        self.title = page.get_by_test_id("title")

    def open(self):
        with allure.step(f"Open {self.PATH}"):
            self.page.goto(self.PATH)
        return self
