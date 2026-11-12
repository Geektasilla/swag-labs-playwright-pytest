from collections.abc import Callable

import allure
import pytest
from playwright.sync_api import BrowserContext, Page, Playwright

from config.settings import settings
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutInfoPage, CheckoutOverviewPage
from pages.inventory_page import InventoryPage
from tests.data import CUSTOMER


@pytest.fixture(scope="session", autouse=True)
def _use_data_test_attribute(playwright: Playwright) -> None:
    """Swag Labs marks elements with `data-test`, so get_by_test_id() should use it."""
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def login_as(page: Page, context: BrowserContext, base_url: str) -> Callable[..., InventoryPage]:
    """Log in without the UI by setting the session cookie the app uses.

    The login form itself is covered by test_login.py; every other test skips it,
    which makes the suite faster and keeps failures focused on the feature under test.
    """

    def _login(username: str = settings.standard_user) -> InventoryPage:
        with allure.step(f"Log in as '{username}' via session cookie"):
            context.add_cookies([{"name": "session-username", "value": username, "url": base_url}])
            return InventoryPage(page).open()

    return _login


@pytest.fixture
def inventory(login_as) -> InventoryPage:
    return login_as()


@pytest.fixture
def checkout_overview(inventory: InventoryPage) -> Callable[..., CheckoutOverviewPage]:
    """Add the given products and walk through checkout up to the overview page."""

    def _go(*products: str) -> CheckoutOverviewPage:
        inventory.add_to_cart(*products)
        inventory.header.open_cart()
        CartPage(inventory.page).checkout()
        info = CheckoutInfoPage(inventory.page)
        info.fill_info(**CUSTOMER)
        info.submit()
        inventory.page.wait_for_url("**/checkout-step-two.html")
        return CheckoutOverviewPage(inventory.page)

    return _go


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """Attach a screenshot to the Allure report when a test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None and not page.is_closed():
            allure.attach(page.screenshot(full_page=True), name="screenshot", attachment_type=allure.attachment_type.PNG)
