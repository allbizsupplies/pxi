
from decimal import Decimal
from sqlalchemy.orm.session import Session
from typing import List

from pxi.dataclasses import SellPriceChange
from pxi.enum import PriceBasis, TaxCode
from pxi.models import ContractItem, PriceRegionItem


def dec(amount: str):
    """
    Creates a Decimal object from a string, rounded to the nearest hundredth
    of a cent.

    Params:
        amount: A str, int or float representing a price.

    Returns:
        The Decimal object.
    """
    if amount is not None:
        return Decimal(amount).quantize(Decimal("0.0001"))
    return None


# The tax factor to use. Equal to Australian GST (10% VAT).
TAX_FACTOR = dec("1.10")

# Rounding rules to be applied to prices.
#
# min: the smallest amount the rule applies to.
# rounding_step: the amount is rounded to the nearesr multiple of this value.
# charm rules:
#     - step: each charm price is a multiple of this value, minus the offset
#     - offset: this is subtracted from the step to get the charm price
#     - range: any amount within this distance from the charm price will become
#              the charm price.
ROUNDING_RULES = [
    {
        "min": dec("0.00"),
        "rounding_step": dec("0.01"),
        "charm_rules": None,
    },
    {
        "min": dec("1.00"),
        "rounding_step": dec("0.05"),
        "charm_rules": None,
    },
    {
        "min": dec("25.00"),
        "rounding_step": dec("0.05"),
        "charm_rules": [
            (dec("1.00"), dec("0.05"), dec("0.10")),
        ],
    },
    {
        "min": dec("99.00"),
        "rounding_step": dec("1.00"),
        "charm_rules": [
            (dec("10.00"), dec("1.00"), dec("2.00")),
        ],
    },
    {
        "min": dec("199.00"),
        "rounding_step": dec("10.00"),
        "charm_rules": [
            (dec("10.00"), dec("1.00"), dec("5.00")),
            (dec("100.00"), dec("1.00"), dec("10.00")),
        ],
    },
]


def apply_price_rule(price_region_item: PriceRegionItem):
    """
    Recalculate prices for price region, using price rule.

    Params:
        price_region_item: The PriceRegionItem to work on.

    Returns:
        A SellPriceChange if prices differ, otherwise None.
    """
    inventory_item = price_region_item.inventory_item
    price_rule = price_region_item.price_rule

    # Calculate and apply new prices for PriceRegionItem and record the
    # SellPriceChange.
    price_change = SellPriceChange(price_region_item)
    for level in range(PriceRegionItem.PRICE_LEVELS):
        # Get the price basis and multiplication factor for the given price
        # level in the PriceRule.
        basis = price_rule.price_basis(level)
        factor = price_rule.price_factor(level)

        # Select the base price for the price calculation depending on the
        # PriceBasis used in the price rule.
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

        # Throw an exception if the base price doesn't exist.
        if base_price is None:
            raise Exception(
                f"No base price for {inventory_item}, {price_region_item}")

        # Calculate the rounded price.
        price_now = round_price(
            dec(base_price) * dec(factor),
            tax_exempt=(price_region_item.tax_code == TaxCode.EXEMPT))

        # Fetch the old price before applying the new price.
        price_was = price_region_item.price(level)
        price_region_item.set_price(level, price_now)

        # Record the price difference in the SellPriceChange.
        price_diff = price_now - price_was
        price_change.price_diffs.append(price_diff)

    # Return the price change if the price has actually changed, otherwise
    # discard it.
    if price_change.price_differs:
        return price_change
    return None


def recalculate_sell_prices(
        price_region_items: List[PriceRegionItem],
        db_session: Session):
    """
    Recalculates sell prices for PriceRegionItems.

    Params:
        price_region_items: The PriceRegionItems to work on.
        session: The database sesssion.

    Returns:
        A list of price changes.
    """
    price_changes: List[SellPriceChange] = []
    for price_region_item in price_region_items:
        price_change = apply_price_rule(price_region_item)
        if price_change:
            price_changes.append(price_change)
    db_session.commit()
    return price_changes


def recalculate_contract_prices(
        price_changes: List[SellPriceChange],
        db_session: Session):

    updated_contract_items: List[ContractItem] = []

    def multiply_prices(con_item: ContractItem, price_ratio: Decimal):
        """
        Calculate and apply new prices to ContractItem.

        Params:
            con_item: The ContractItem to work on.
            price_ratio: The ratio of the new price to the old price.
        """
        for level in range(1, ContractItem.PRICE_LEVELS + 1):
            price_was = con_item.price(level)
            price_now = (price_was * price_ratio).quantize(price_was)
            con_item.set_price(level, price_now)

    for price_change in price_changes:
        inventory_item = price_change.price_region_item.inventory_item
        contract_items = db_session.query(ContractItem).filter(
            ContractItem.inventory_item == inventory_item
        ).all()
        # Adjust the contract prices in proportion to the retail price change.
        price_now = price_change.price_region_item.price(0)
        price_diff = price_change.price_diffs[0]
        price_was = price_now - price_diff
        price_ratio = Decimal()
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
