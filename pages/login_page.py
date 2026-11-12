import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username = page.get_by_test_id("username")
        self.password = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error = page.get_by_test_id("error")
        self.error_close_button = page.get_by_test_id("error-button")

    def login(self, username: str, password: str) -> None:
        with allure.step(f"Log in as '{username}'"):
            self.username.fill(username)
            self.password.fill(password)
            self.login_button.click()
