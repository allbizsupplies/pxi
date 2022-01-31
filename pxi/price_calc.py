
from copy import copy
from math import ceil
from decimal import Decimal
from pxi.data import SellPriceChange

from pxi.enum import PriceBasis, TaxCode
from pxi.models import ContractItem, PriceRegionItem


def d(amount):
    if amount is not None:
        return Decimal(amount).quantize(Decimal("0.0001"))


TAX_FACTOR = d("1.10")

PRICE_LEVELS = 5

# min: the smallest amount the rule applies to.
# rounding_step: the amount is rounded to the nearesr multiple of this value.
# charm rules:
#     - step: each charm price is a multiple of this value, minus the offset
#     - offset: this is subtracted from the step to get the charm price
#     - range: any amount within this distance from the charm price will become
#              the charm price.
ROUNDING_RULES = [
    {
        "min": d("0.00"),
        "rounding_step": d("0.01"),
        "charm_rules": None,
    },
    {
        "min": d("1.00"),
        "rounding_step": d("0.05"),
        "charm_rules": None,
    },
    {
        "min": d("25.00"),
        "rounding_step": d("0.05"),
        "charm_rules": [
            (d("1.00"), d("0.05"), d("0.10")),
        ],
    },
    {
        "min": d("99.00"),
        "rounding_step": d("1.00"),
        "charm_rules": [
            (d("10.00"), d("1.00"), d("2.00")),
        ],
    },
    {
        "min": d("199.00"),
        "rounding_step": d("10.00"),
        "charm_rules": [
            (d("10.00"), d("1.00"), d("5.00")),
            (d("100.00"), d("1.00"), d("10.00")),
        ],
    },
]


def apply_price_rule(price_region_item):
    """Recalculate prices for price region."""
    inventory_item = price_region_item.inventory_item
    price_rule = price_region_item.price_rule
    price_change = SellPriceChange(price_region_item)
    for i in range(PRICE_LEVELS):
        basis = getattr(price_rule, f"price_{i}_basis")
        factor = getattr(price_rule, f"price_{i}_factor")
        base_price = None
        if basis == PriceBasis.REPLACEMENT_COST:
            base_price = inventory_item.replacement_cost
        elif basis == PriceBasis.RRP_EXCL_TAX:
            base_price = price_region_item.rrp_excl_tax
        elif basis == PriceBasis.RRP_INCL_TAX:
            base_price = price_region_item.rrp_incl_tax
        elif basis == PriceBasis.EXISTING_PRICE_0:
            base_price = price_region_item.price_0
        elif basis == PriceBasis.EXISTING_PRICE_1:
            base_price = price_region_item.price_1
        elif basis == PriceBasis.EXISTING_PRICE_2:
            base_price = price_region_item.price_2
        elif basis == PriceBasis.EXISTING_PRICE_3:
            base_price = price_region_item.price_3
        elif basis == PriceBasis.EXISTING_PRICE_4:
            base_price = price_region_item.price_4
        if base_price is None:
            raise Exception(
                f"no base price for {inventory_item}, {price_region_item}")
        price = base_price * factor
        tax_exempt = price_region_item.tax_code == TaxCode.EXEMPT
        rounded_price = round_price(price, tax_exempt=tax_exempt)
        price_was = getattr(price_region_item, f"price_{i}")
        price_diff = rounded_price - price_was
        price_change.price_diffs.append(price_diff)
        setattr(price_region_item, f"price_{i}", rounded_price)
    if price_change.price_differs:
        return price_change
    return None


def recalculate_sell_prices(price_region_items, db_session):
    price_changes = []
    for price_region_item in price_region_items:
        price_change = apply_price_rule(price_region_item)
        if price_change:
            price_changes.append(price_change)
        db_session.commit()
    return price_changes


def recalculate_contract_prices(price_changes, db_session):
    updated_contract_items = []

    def multiply_prices(contract_item, price_ratio):
        for i in range(1, 7):
            price_field = f"price_{i}"
            price_was = getattr(contract_item, price_field)
            price_now = (price_was * price_ratio).quantize(price_was)
            setattr(contract_item, price_field, price_now)

    for price_change in price_changes:
        inventory_item = price_change.price_region_item.inventory_item
        contract_items = db_session.query(ContractItem).filter(
            ContractItem.inventory_item == inventory_item
        ).all()
        # Adjust the contract prices in proportion to the retail price change.
        price_now = price_change.price_region_item.price_0
        price_diff = price_change.price_diffs[0]
        price_was = price_now - price_diff
        price_ratio = None
        if price_was > 0:
            price_ratio = (price_now / price_was).quantize(price_now)
        elif price_now > 0:
            price_ratio = Decimal(1)
        for contract_item in contract_items:
            multiply_prices(contract_item, price_ratio)
            db_session.commit()
            updated_contract_items.append(contract_item)
    return updated_contract_items


def round_price(price_excl, tax_exempt=False):
    """Calculate rounded price."""

    def round_to_step(price_incl, step):
        """Round the price to the nearest step"""
        remainder = price_incl % step
        rounding_amount = -(remainder)
        if remainder > step / 2:
            rounding_amount = step - remainder
        rounded_price = price_incl + rounding_amount
        return rounded_price

    # Get the rounded price, including tax.
    price_incl = price_excl
    if not tax_exempt:
        price_incl = incl_tax(price_excl)
    selected_rule = None
    for rule in ROUNDING_RULES:
        if selected_rule:
            # pylint: disable=unsubscriptable-object
            if rule["min"] >= selected_rule["min"] and rule["min"] <= price_incl:
                selected_rule = rule
        else:
            selected_rule = rule
    min = selected_rule["min"]
    rounding_step = selected_rule["rounding_step"]
    charm_rules = selected_rule["charm_rules"]
    rounded_price_incl = round_to_step(price_incl, rounding_step)

    # Use charm price (e.g. 29.95 instead of 30.02) if it is within two
    # rounding steps of the rounded price.
    if charm_rules:
        for step, offset, range in charm_rules:
            # Calculate the charm price, and use it if it's within range.
            charm_price_incl = round_to_step(price_incl, step) - offset
            difference = (charm_price_incl - rounded_price_incl).copy_abs()
            if difference <= range:
                rounded_price_incl = charm_price_incl

    # Make sure price doesn't dip below the minimum.
    if rounded_price_incl < min:
        rounded_price_incl = min

    # Return new price ex GST.
    rounded_price_excl = rounded_price_incl
    if not tax_exempt:
        rounded_price_excl = excl_tax(rounded_price_incl)
    return rounded_price_excl


def incl_tax(amount):
    amount_incl = amount * TAX_FACTOR
    return round(amount_incl, 4)


def excl_tax(amount):
    amount_excl = amount / TAX_FACTOR
    return round(amount_excl, 4)
