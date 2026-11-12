import re

import allure
import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

pytestmark = allure.feature("Login")

ACCEPTED_USERS = [
    settings.standard_user,
    settings.problem_user,
    settings.performance_glitch_user,
    settings.error_user,
    settings.visual_user,
]


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page).open()


@pytest.mark.smoke
def test_standard_user_can_log_in(login_page: LoginPage):
    login_page.login(settings.standard_user, settings.password)

    inventory = InventoryPage(login_page.page)
    expect(login_page.page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(inventory.title).to_have_text("Products")


@pytest.mark.parametrize("username", ACCEPTED_USERS)
def test_every_demo_user_except_locked_can_log_in(login_page: LoginPage, username: str):
    login_page.login(username, settings.password)

    # performance_glitch_user is intentionally slow (see BUG-09); here we only check that login works.
    expect(InventoryPage(login_page.page).title).to_have_text("Products", timeout=15_000)


def test_locked_out_user_is_rejected(login_page: LoginPage):
    login_page.login(settings.locked_out_user, settings.password)

    expect(login_page.error).to_have_text("Epic sadface: Sorry, this user has been locked out.")
    expect(login_page.login_button).to_be_visible()


@pytest.mark.parametrize(
    ("username", "password", "message"),
    [
        ("", "", "Epic sadface: Username is required"),
        (settings.standard_user, "", "Epic sadface: Password is required"),
        (settings.standard_user, "wrong_password", "Epic sadface: Username and password do not match any user in this service"),
        ("unknown_user", settings.password, "Epic sadface: Username and password do not match any user in this service"),
    ],
    ids=["empty-form", "empty-password", "wrong-password", "unknown-user"],
)
def test_invalid_credentials_show_error(login_page: LoginPage, username: str, password: str, message: str):
    login_page.login(username, password)

    expect(login_page.error).to_have_text(message)


def test_error_message_can_be_dismissed(login_page: LoginPage):
    login_page.login("", "")
    expect(login_page.error).to_be_visible()

    login_page.error_close_button.click()

    expect(login_page.error).to_be_hidden()


def test_protected_page_requires_login(page: Page):
    InventoryPage(page).open()

    login_page = LoginPage(page)
    expect(login_page.error).to_have_text(
        "Epic sadface: You can only access '/inventory.html' when you are logged in."
    )


@pytest.mark.smoke
def test_logout_ends_session(inventory: InventoryPage):
    inventory.header.logout()

    expect(LoginPage(inventory.page).login_button).to_be_visible()
    InventoryPage(inventory.page).open()
    expect(LoginPage(inventory.page).error).to_contain_text("when you are logged in")
