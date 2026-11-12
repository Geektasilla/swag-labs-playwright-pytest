from decimal import Decimal

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage, parse_money


class CheckoutInfoPage(BasePage):
    """Step one: customer information."""

    PATH = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.cancel_button = page.get_by_test_id("cancel")
        self.error = page.get_by_test_id("error")

    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        with allure.step(f"Fill customer info: {first_name!r} {last_name!r} {postal_code!r}"):
            for field, value in ((self.first_name, first_name), (self.last_name, last_name), (self.postal_code, postal_code)):
                field.fill(value)

    @allure.step("Continue to overview")
    def submit(self) -> None:
        self.continue_button.click()


class CheckoutOverviewPage(BasePage):
    """Step two: order summary with prices and tax."""

    PATH = "/checkout-step-two.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.subtotal_label = page.get_by_test_id("subtotal-label")
        self.tax_label = page.get_by_test_id("tax-label")
        self.total_label = page.get_by_test_id("total-label")
        self.finish_button = page.get_by_test_id("finish")
        self.cancel_button = page.get_by_test_id("cancel")

    def prices(self) -> list[Decimal]:
        return [parse_money(text) for text in self.item_prices.all_text_contents()]

    def subtotal(self) -> Decimal:
        return parse_money(self.subtotal_label.inner_text())

    def tax(self) -> Decimal:
        return parse_money(self.tax_label.inner_text())

    def total(self) -> Decimal:
        return parse_money(self.total_label.inner_text())

    @allure.step("Finish the order")
    def finish(self) -> None:
        self.finish_button.click()
        self.page.wait_for_url("**/checkout-complete.html")

    @allure.step("Cancel the order")
    def cancel(self) -> None:
        self.cancel_button.click()
        self.page.wait_for_url("**/inventory.html")


class CheckoutCompletePage(BasePage):
    PATH = "/checkout-complete.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header_text = page.get_by_test_id("complete-header")
        self.back_home_button = page.get_by_test_id("back-to-products")
