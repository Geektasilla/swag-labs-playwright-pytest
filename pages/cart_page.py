import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class CartPage(BasePage):
    PATH = "/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    def names(self) -> list[str]:
        return self.item_names.all_text_contents()

    def remove(self, name: str) -> None:
        with allure.step(f"Remove '{name}' from the cart"):
            item = self.items.filter(has=self.page.get_by_text(name, exact=True))
            item.get_by_role("button", name="Remove").click()

    @allure.step("Proceed to checkout")
    def checkout(self) -> None:
        self.checkout_button.click()
        self.page.wait_for_url("**/checkout-step-one.html")

    @allure.step("Continue shopping")
    def continue_shopping(self) -> None:
        self.continue_shopping_button.click()
        self.page.wait_for_url("**/inventory.html")
