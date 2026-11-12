from decimal import ROUND_HALF_UP, Decimal

import allure
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutCompletePage, CheckoutInfoPage
from pages.inventory_page import InventoryPage
from tests.data import BACKPACK, BIKE_LIGHT, CATALOGUE, CUSTOMER, FLEECE_JACKET, TAX_RATE

pytestmark = allure.feature("Checkout")

CENT = Decimal("0.01")


@pytest.fixture
def checkout_info(inventory: InventoryPage) -> CheckoutInfoPage:
    inventory.add_to_cart(BACKPACK)
    inventory.header.open_cart()
    CartPage(inventory.page).checkout()
    return CheckoutInfoPage(inventory.page)


@pytest.mark.smoke
def test_complete_purchase(checkout_overview):
    overview = checkout_overview(BACKPACK, BIKE_LIGHT)
    overview.finish()

    complete = CheckoutCompletePage(overview.page)
    expect(complete.title).to_have_text("Checkout: Complete!")
    expect(complete.header_text).to_have_text("Thank you for your order!")
    expect(complete.header.cart_badge).to_be_hidden()


@pytest.mark.parametrize(
    "products",
    [[BACKPACK], [BACKPACK, BIKE_LIGHT], [BACKPACK, BIKE_LIGHT, FLEECE_JACKET], list(CATALOGUE)],
    ids=["1-item", "2-items", "3-items", "all-items"],
)
def test_order_totals_are_calculated_correctly(checkout_overview, products: list[str]):
    overview = checkout_overview(*products)

    expected_subtotal = sum((CATALOGUE[p] for p in products), Decimal("0"))
    expected_tax = (expected_subtotal * TAX_RATE).quantize(CENT, rounding=ROUND_HALF_UP)

    expect(overview.item_names).to_have_text(products)
    assert overview.prices() == [CATALOGUE[p] for p in products]
    assert overview.subtotal() == expected_subtotal
    assert overview.tax() == expected_tax
    assert overview.total() == expected_subtotal + expected_tax


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("first_name", "Error: First Name is required"),
        ("last_name", "Error: Last Name is required"),
        ("postal_code", "Error: Postal Code is required"),
    ],
)
def test_customer_info_fields_are_required(checkout_info: CheckoutInfoPage, field: str, message: str):
    data = {**CUSTOMER, field: ""}

    checkout_info.fill_info(**data)
    checkout_info.submit()

    expect(checkout_info.error).to_have_text(message)
    expect(checkout_info.title).to_have_text("Checkout: Your Information")


def test_cancel_on_overview_returns_to_products_and_keeps_cart(checkout_overview):
    overview = checkout_overview(BACKPACK)

    overview.cancel()

    expect(overview.title).to_have_text("Products")
    expect(overview.header.cart_badge).to_have_text("1")
