import allure
from playwright.sync_api import Page


class Header:
    """Top bar shared by all pages after login: cart icon and burger menu."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.menu_button = page.get_by_role("button", name="Open Menu")
        self.logout_link = page.get_by_test_id("logout-sidebar-link")
        self.reset_link = page.get_by_test_id("reset-sidebar-link")

    @allure.step("Open the cart")
    def open_cart(self) -> None:
        self.cart_link.click()
        self.page.wait_for_url("**/cart.html")

    @allure.step("Log out")
    def logout(self) -> None:
        self.menu_button.click()
        self.logout_link.click()
        self.page.wait_for_url(lambda url: url.rstrip("/").endswith("saucedemo.com"))

    @allure.step("Reset app state")
    def reset_app_state(self) -> None:
        self.menu_button.click()
        self.reset_link.click()
