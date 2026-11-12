from decimal import Decimal

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage, parse_money


class ProductPage(BasePage):
    PATH = "/inventory-item.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.name = page.get_by_test_id("inventory-item-name")
        self.description = page.get_by_test_id("inventory-item-desc")
        self.price_label = page.get_by_test_id("inventory-item-price")
        self.add_button = page.get_by_role("button", name="Add to cart")
        self.remove_button = page.get_by_role("button", name="Remove")
        self.back_button = page.get_by_test_id("back-to-products")

    def price(self) -> Decimal:
        return parse_money(self.price_label.inner_text())

    @allure.step("Add the product to the cart")
    def add_to_cart(self) -> None:
        self.add_button.click()

    @allure.step("Go back to products")
    def back_to_products(self) -> None:
        self.back_button.click()
        self.page.wait_for_url("**/inventory.html")
