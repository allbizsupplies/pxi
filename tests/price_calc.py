from decimal import Decimal
from pxi.dataclasses import SellPriceChange

from pxi.enum import TaxCode
from pxi.models import PriceRegionItem
from pxi.price_calc import (
    apply_price_rule,
    recalculate_contract_prices,
    recalculate_sell_prices,
    round_price,
    incl_tax,
    excl_tax)
from tests import DatabaseTestCase
from tests.fakes import (
    fake_contract_item,
    fake_inventory_item,
    fake_price_region_item,
    fake_price_rule,
    fake_sell_price_change)


class PriceCalcTests(DatabaseTestCase):

    def test_tax_calc(self):
        """
        Adds and subtracts tax from a price.
        """
        price = Decimal("10.00")
        expected_price_inc = Decimal("11.00")
        expected_price_ex = Decimal("9.0909")
        self.assertEqual(expected_price_inc, incl_tax(price))
        self.assertEqual(expected_price_ex, excl_tax(price))

    def test_round_price(self):
        """
        Rounds prices according to charm price rules.
        """
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
            ("209.00", "209.00"),
            ("210.50", "209.00"),
            ("4012.13", "4009.00"),
            ("4100.00", "4099.00"),
            ("4589.02", "4599.00"),
        ]]

        for price_incl, expected_price_rd_incl in prices:
            price_excl = excl_tax(price_incl)
            price_rd_excl = round_price(price_excl)
            expected_price_rd_excl = excl_tax(expected_price_rd_incl)
            self.assertEqual(price_rd_excl, expected_price_rd_excl)

    def test_apply_price_rule(self):
        """
        Recalculates sell prices on an item.
        """
        price_rule = fake_price_rule({
            "price_0_factor": "6.00",
            "price_1_factor": "5.00",
            "price_2_factor": "4.00",
            "price_3_factor": "3.00",
            "price_4_factor": "2.00",
        })
        inv_item = fake_inventory_item({
            "replacement_cost": "10.00",
        })
        pr_item = fake_price_region_item(inv_item, price_rule, {
            "tax_code": TaxCode.TAXABLE,
        })
        self.seed([
            inv_item,
            price_rule,
            pr_item,
        ])

        price_changes = apply_price_rule(pr_item)
        self.db_session.commit()

        calculated_prices = [
            pr_item.price(level)
            for level in range(5)
        ]
        self.assertListEqual(calculated_prices, [
            Decimal("59.9545"),  # 65.95 incl tax
            Decimal("49.9545"),  # 54.95 incl tax
            Decimal("39.9545"),  # 43.95 incl tax
            Decimal("29.9545"),  # 32.95 incl tax
            Decimal("20.0000"),  # 22.00 incl tax
        ])
        self.assertIsNotNone(price_changes)

    def test_recalculate_sell_prices(self):
        """
        Calculate new prices for PriceRegionItemms and return a list of 
        SellPriceChanges.
        """
        inv_item = fake_inventory_item()
        price_rule = fake_price_rule()
        pr_item = fake_price_region_item(inv_item, price_rule)
        self.seed([
            inv_item,
            price_rule,
            pr_item,
        ])
        price_changes = recalculate_sell_prices(
            [pr_item], self.db_session)
        for price_change in price_changes:
            self.assertGreater(len(price_change.price_diffs), 0)

    def test_recalculate_contract_prices(self):
        """
        Calculate new prices for ContractItems.
        """
        inv_item = fake_inventory_item()
        price_rule = fake_price_rule()
        pr_item = fake_price_region_item(inv_item, price_rule)
        con_item = fake_contract_item(inv_item)
        self.seed([
            inv_item,
            price_rule,
            pr_item,
        ])
        price_change = fake_sell_price_change(pr_item)
        updated_contract_items = recalculate_contract_prices(
            [price_change], self.db_session)
        self.assertEqual(len(updated_contract_items), 1)
