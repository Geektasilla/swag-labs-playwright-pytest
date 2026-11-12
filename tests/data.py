"""Expected test data for the Swag Labs catalogue."""

from decimal import Decimal

TAX_RATE = Decimal("0.08")

# Product name -> price as published in the catalogue.
CATALOGUE: dict[str, Decimal] = {
    "Sauce Labs Backpack": Decimal("29.99"),
    "Sauce Labs Bike Light": Decimal("9.99"),
    "Sauce Labs Bolt T-Shirt": Decimal("15.99"),
    "Sauce Labs Fleece Jacket": Decimal("49.99"),
    "Sauce Labs Onesie": Decimal("7.99"),
    "Test.allTheThings() T-Shirt (Red)": Decimal("15.99"),
}

BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"
FLEECE_JACKET = "Sauce Labs Fleece Jacket"

CUSTOMER = {"first_name": "Anna", "last_name": "Tester", "postal_code": "69117"}
