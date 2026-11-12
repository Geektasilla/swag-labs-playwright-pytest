import allure
import pytest
from playwright.sync_api import expect

from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage
from tests.data import BACKPACK, BIKE_LIGHT, CATALOGUE

pytestmark = allure.feature("Inventory")


@pytest.mark.smoke
def test_catalogue_matches_expected_products_and_prices(inventory: InventoryPage):
    expect(inventory.item_names).to_have_text(list(CATALOGUE))

    assert inventory.catalogue() == CATALOGUE


def test_every_product_has_its_own_image(inventory: InventoryPage):
    sources = inventory.image_sources()

    assert len(set(sources)) == len(CATALOGUE)


@pytest.mark.parametrize(
    ("option", "key", "reverse"),
    [
        ("az", "name", False),
        ("za", "name", True),
        ("lohi", "price", False),
        ("hilo", "price", True),
    ],
    ids=["name-a-z", "name-z-a", "price-low-high", "price-high-low"],
)
def test_sorting(inventory: InventoryPage, option: str, key: str, reverse: bool):
    inventory.sort_by(option)

    values = inventory.names() if key == "name" else inventory.prices()
    assert values == sorted(values, reverse=reverse)
    expect(inventory.sort_dropdown).to_have_value(option)


@pytest.mark.smoke
def test_add_and_remove_updates_badge_and_button(inventory: InventoryPage):
    inventory.add_to_cart(BACKPACK, BIKE_LIGHT)

    expect(inventory.header.cart_badge).to_have_text("2")
    expect(inventory.cart_button(BACKPACK)).to_have_text("Remove")

    inventory.remove_from_cart(BACKPACK)

    expect(inventory.header.cart_badge).to_have_text("1")
    expect(inventory.cart_button(BACKPACK)).to_have_text("Add to cart")


def test_product_details_match_inventory(inventory: InventoryPage):
    inventory.open_product(BACKPACK)

    product = ProductPage(inventory.page)
    expect(product.name).to_have_text(BACKPACK)
    assert product.price() == CATALOGUE[BACKPACK]

    product.add_to_cart()
    expect(product.header.cart_badge).to_have_text("1")

    product.back_to_products()
    expect(inventory.title).to_have_text("Products")


def test_reset_app_state_empties_cart(inventory: InventoryPage):
    inventory.add_to_cart(BACKPACK)
    expect(inventory.header.cart_badge).to_have_text("1")

    inventory.header.reset_app_state()

    expect(inventory.header.cart_badge).to_be_hidden()
