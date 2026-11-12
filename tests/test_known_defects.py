"""Regression tests for defects documented in docs/bug-reports.md.

Each test asserts the *correct* behaviour and is marked xfail(strict=True):
- while the defect exists, the test is reported as "expected failure";
- if the defect is fixed, the test unexpectedly passes and the run fails,
  signalling that the marker and the bug report must be updated.
"""

import re
import time

import allure
import pytest
from playwright.sync_api import Dialog, expect

from config.settings import settings
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutCompletePage, CheckoutInfoPage
from pages.login_page import LoginPage
from tests.data import BACKPACK, BIKE_LIGHT, CATALOGUE, CUSTOMER, FLEECE_JACKET

# Response-time budget for page transitions (an assumed non-functional requirement).
RESPONSE_BUDGET_MS = 2_000

pytestmark = [allure.feature("Known defects"), pytest.mark.known_defect]


def known_defect(bug_id: str, summary: str):
    return pytest.mark.xfail(reason=f"{bug_id}: {summary}", strict=True)


@known_defect("BUG-01", "Item total is shown with floating-point noise, e.g. $59.980000000000004")
def test_item_total_has_two_decimal_places(checkout_overview):
    overview = checkout_overview(BIKE_LIGHT, FLEECE_JACKET)

    expect(overview.subtotal_label).to_have_text(re.compile(r"^Item total: \$\d+\.\d{2}$"))


@known_defect("BUG-02", "problem_user: every product shows the same image")
def test_problem_user_sees_unique_product_images(login_as):
    inventory = login_as(settings.problem_user)

    assert len(set(inventory.image_sources())) == len(CATALOGUE)


@known_defect("BUG-03", "problem_user: sorting does not change the product order")
def test_problem_user_can_sort_by_price(login_as):
    inventory = login_as(settings.problem_user)

    inventory.sort_by("lohi")

    prices = inventory.prices()
    assert prices == sorted(prices)


@known_defect("BUG-04", "problem_user: 'Add to cart' does nothing for half of the products")
def test_problem_user_can_add_every_product(login_as):
    inventory = login_as(settings.problem_user)

    inventory.add_to_cart(*CATALOGUE)

    expect(inventory.header.cart_badge).to_have_text(str(len(CATALOGUE)), timeout=2_000)


@known_defect("BUG-05", "problem_user: typing the last name overwrites the first name field")
def test_problem_user_can_enter_last_name(login_as):
    inventory = login_as(settings.problem_user)
    inventory.add_to_cart(BACKPACK)
    inventory.header.open_cart()
    CartPage(inventory.page).checkout()

    info = CheckoutInfoPage(inventory.page)
    info.fill_info(**CUSTOMER)

    expect(info.first_name).to_have_value(CUSTOMER["first_name"], timeout=2_000)
    expect(info.last_name).to_have_value(CUSTOMER["last_name"], timeout=2_000)


@known_defect("BUG-06", "error_user: sorting shows the alert 'Sorting is broken!'")
def test_error_user_can_sort_without_errors(login_as):
    inventory = login_as(settings.error_user)
    dialogs: list[str] = []

    def record(dialog: Dialog) -> None:
        dialogs.append(dialog.message)
        dialog.dismiss()

    inventory.page.on("dialog", record)
    inventory.sort_by("za")

    assert dialogs == []


@known_defect("BUG-07", "error_user: 'Finish' does not complete the order")
def test_error_user_can_complete_order(login_as):
    inventory = login_as(settings.error_user)
    inventory.add_to_cart(BACKPACK)
    inventory.header.open_cart()
    CartPage(inventory.page).checkout()
    info = CheckoutInfoPage(inventory.page)
    info.fill_info(**CUSTOMER)
    info.submit()

    inventory.page.get_by_test_id("finish").click()

    expect(CheckoutCompletePage(inventory.page).title).to_have_text("Checkout: Complete!", timeout=2_000)


@known_defect("BUG-08", "visual_user: inventory prices differ from the catalogue")
def test_visual_user_sees_correct_prices(login_as):
    inventory = login_as(settings.visual_user)

    assert inventory.catalogue() == CATALOGUE


@known_defect("BUG-09", "performance_glitch_user: login and navigation take ~5 s")
def test_performance_glitch_user_logs_in_within_budget(page):
    assert measure_login_ms(page, settings.performance_glitch_user) < RESPONSE_BUDGET_MS


def test_standard_user_logs_in_within_budget(page):
    """Control test for BUG-09: the same budget is met by the standard user."""
    assert measure_login_ms(page, settings.standard_user) < RESPONSE_BUDGET_MS


def measure_login_ms(page, username: str) -> float:
    """Time from clicking 'Login' until the product list is rendered."""
    login_page = LoginPage(page).open()
    started = time.perf_counter()
    login_page.login(username, settings.password)
    expect(login_page.title).to_have_text("Products", timeout=15_000)
    elapsed_ms = (time.perf_counter() - started) * 1000
    allure.attach(f"{elapsed_ms:.0f} ms", name=f"login time ({username})", attachment_type=allure.attachment_type.TEXT)
    return elapsed_ms


def test_standard_user_has_none_of_these_defects(checkout_overview):
    """Control test: the same flows work for the standard user, so the defects are user-specific."""
    overview = checkout_overview(BACKPACK, BIKE_LIGHT)
    overview.finish()

    expect(CheckoutCompletePage(overview.page).title).to_have_text("Checkout: Complete!")
