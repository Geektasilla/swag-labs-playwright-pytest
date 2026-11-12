from decimal import Decimal

import allure
from playwright.sync_api import Locator, Page

from pages.base_page import BasePage, parse_money


class InventoryPage(BasePage):
    PATH = "/inventory.html"

    SORT_OPTIONS = {
        "az": "Name (A to Z)",
        "za": "Name (Z to A)",
        "lohi": "Price (low to high)",
        "hilo": "Price (high to low)",
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.item_images = page.locator(".inventory_item_img img")
        self.sort_dropdown = page.get_by_test_id("product-sort-container")

    def item(self, name: str) -> Locator:
        return self.items.filter(has=self.page.get_by_test_id("inventory-item-name").get_by_text(name, exact=True))

    def cart_button(self, name: str) -> Locator:
        """The 'Add to cart' / 'Remove' toggle button of a product card."""
        return self.item(name).locator("button")

    def add_to_cart(self, *names: str) -> None:
        for name in names:
            with allure.step(f"Add '{name}' to the cart"):
                self.item(name).get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, name: str) -> None:
        with allure.step(f"Remove '{name}' from the cart"):
            self.item(name).get_by_role("button", name="Remove").click()

    def sort_by(self, option: str) -> None:
        with allure.step(f"Sort by '{self.SORT_OPTIONS[option]}'"):
            self.sort_dropdown.select_option(option)

    def open_product(self, name: str) -> None:
        with allure.step(f"Open product details for '{name}'"):
            self.item_names.get_by_text(name, exact=True).click()
            self.page.wait_for_url("**/inventory-item.html*")

    def names(self) -> list[str]:
        return self.item_names.all_text_contents()

    def prices(self) -> list[Decimal]:
        return [parse_money(text) for text in self.item_prices.all_text_contents()]

    def catalogue(self) -> dict[str, Decimal]:
        return dict(zip(self.names(), self.prices(), strict=True))

    def image_sources(self) -> list[str]:
        return self.item_images.evaluate_all("images => images.map(img => img.getAttribute('src'))")
