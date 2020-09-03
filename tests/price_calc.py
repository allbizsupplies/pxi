from decimal import Decimal

from pxi.enum import (
    TaxCode)
from pxi.models import PriceRegionItem
from pxi.price_calc import (
    PriceChange,
    apply_price_rule,
    recalculate_contract_prices,
    recalculate_sell_prices,
    round_price,
    incl_tax,
    excl_tax)
from tests import DatabaseTestCase
from tests.fixtures.models import (
    random_contract_item,
    random_inventory_item,
    random_price_rule,
    random_pricelist)


class PriceCalcTests(DatabaseTestCase):

    def test_tax_calc(self):
        """Add and subtract tax from a price."""
        price = Decimal("10.00")
        expected_price_inc = Decimal("11.00")
        expected_price_ex = Decimal("9.0909")
        self.assertEqual(expected_price_inc, incl_tax(price))
        self.assertEqual(expected_price_ex, excl_tax(price))

    def test_round_price(self):
        """Round prices according to charm price rules."""
        prices = [(Decimal(x), Decimal(y)) for x, y in [
            ("0.47", "0.47"),
            ("0.99", "0.99"),
            ("1.00", "1.00"),
            ("5.02", "5.00"),
            ("5.03", "5.05"),
            ("5.05", "5.05"),
            ("24.82", "24.80"),
            ("24.93", "24.95"),
            ("24.99", "25.00"),
            ("25.02", "25.00"),
            ("25.05", "25.00"),
            ("25.08", "25.10"),
            ("25.85", "25.95"),
            ("25.99", "25.95"),
            ("26.00", "25.95"),
            ("99.90", "99.00"),
            ("99.99", "99.00"),
            ("100.00", "99.00"),
            ("152.71", "153.00"),
            ("151.02", "149.00"),
            ("152.02", "152.00"),
            ("204.30", "199.00"),
            ("209.00", "199.00"),
            ("210.50", "199.00"),
            ("4012.13", "3999.00"),
            ("4100.00", "4099.00"),
            ("4012.13", "3999.00"),
            ("4589.02", "4599.00"),
        ]]

        for price_incl, expected_price_rd_incl in prices:
            price_excl = excl_tax(price_incl)
            price_rd_excl = round_price(price_excl)
            expected_price_rd_excl = excl_tax(expected_price_rd_incl)
            self.assertEqual(price_rd_excl, expected_price_rd_excl)

    def test_apply_price_rule(self):
        """Recalculate sell prices on an item."""
        price_rule = random_price_rule()
        price_rule.price_0_factor = Decimal("6.00")
        price_rule.price_1_factor = Decimal("5.00")
        price_rule.price_2_factor = Decimal("4.00")
        price_rule.price_3_factor = Decimal("3.00")
        price_rule.price_4_factor = Decimal("2.00")
        # pylint:disable=no-member
        self.session.add(price_rule)

        inventory_item = random_inventory_item()
        inventory_item.replacement_cost = Decimal("10.00")
        # pylint:disable=no-member
        self.session.add(inventory_item)

        price_region_item = PriceRegionItem(
            code="",
            inventory_item=inventory_item,
            price_rule=price_rule,
            tax_code=TaxCode.TAXABLE,
            quantity_1=99999999,
            quantity_2=99999999,
            quantity_3=99999999,
            quantity_4=99999999,
            price_0=Decimal("24.00"),
            price_1=Decimal("20.00"),
            price_2=Decimal("16.00"),
            price_3=Decimal("12.00"),
            price_4=Decimal("8.00"),
            rrp_excl_tax=Decimal("0.00"),
            rrp_incl_tax=Decimal("0.00")
        )
        self.session.add(price_region_item)

        price_changes = apply_price_rule(price_region_item)

        calculated_prices = [
            price_region_item.price_0,
            price_region_item.price_1,
            price_region_item.price_2,
            price_region_item.price_3,
            price_region_item.price_4,
        ]
        expected_prices = [
            Decimal("59.9545"),  # 65.95 incl tax
            Decimal("49.9545"),  # 54.95 incl tax
            Decimal("39.9545"),  # 43.95 incl tax
            Decimal("29.9545"),  # 32.95 incl tax
            Decimal("20.0000"),  # 22.00 incl tax
        ]

        self.assertListEqual(expected_prices, calculated_prices)
        self.assertIsNotNone(price_changes)

    def test_recalculate_sell_prices(self):
        """Calculate new prices for items and return a list of changes."""
        price_region_items = random_pricelist(items=5)
        # pylint:disable=no-member
        [self.session.add(item) for item in price_region_items]
        price_changes = recalculate_sell_prices(
            price_region_items, self.session)
        self.assertIsInstance(price_changes, list)
        for price_change in price_changes:
            self.assertIsInstance(price_change, PriceChange)
            self.assertIsNotNone(price_change.price_diffs)

    def test_recalculate_contract_prices(self):
        """Calculate new prices for contract items."""
        item_count = 5
        contract_items = []
        price_region_items = random_pricelist(items=item_count)
        for price_region_item in price_region_items:
            inventory_item = price_region_item.inventory_item
            contract_item = random_contract_item(inventory_item)
            # pylint:disable=no-member
            self.session.add(price_region_item)
            contract_items.append(contract_item)
        price_changes = recalculate_sell_prices(
            price_region_items, self.session)
        updated_contract_items = recalculate_contract_prices(
            price_changes, self.session)
        self.assertEqual(len(updated_contract_items), item_count)
