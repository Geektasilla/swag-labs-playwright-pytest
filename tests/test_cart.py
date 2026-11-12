import allure
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from tests.data import BACKPACK, BIKE_LIGHT, FLEECE_JACKET

pytestmark = allure.feature("Cart")


@pytest.fixture
def cart(inventory: InventoryPage) -> CartPage:
    inventory.add_to_cart(BACKPACK, BIKE_LIGHT)
    inventory.header.open_cart()
    return CartPage(inventory.page)


@pytest.mark.smoke
def test_cart_lists_added_products(cart: CartPage):
    expect(cart.title).to_have_text("Your Cart")
    expect(cart.item_names).to_have_text([BACKPACK, BIKE_LIGHT])


def test_remove_product_from_cart(cart: CartPage):
    cart.remove(BACKPACK)

    expect(cart.item_names).to_have_text([BIKE_LIGHT])
    expect(cart.header.cart_badge).to_have_text("1")


def test_cart_survives_page_reload(cart: CartPage):
    cart.page.reload()

    expect(cart.item_names).to_have_text([BACKPACK, BIKE_LIGHT])


def test_continue_shopping_keeps_cart(cart: CartPage):
    cart.continue_shopping()

    inventory = InventoryPage(cart.page)
    expect(inventory.title).to_have_text("Products")
    inventory.add_to_cart(FLEECE_JACKET)
    expect(inventory.header.cart_badge).to_have_text("3")
