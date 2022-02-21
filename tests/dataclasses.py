
from decimal import Decimal

from pxi.dataclasses import BuyPriceChange, SellPriceChange
from tests import PXITestCase
from tests.fakes import (
    fake_inventory_item,
    fake_price_region_item,
    fake_price_rule,
    fake_supplier_item,
    random_price)


class BuyPriceChangeTests(PXITestCase):

    def test_price_diff(self):
        """
        price_diff is equal to difference between price_now and price_was.
        """
        supp_item = fake_supplier_item(fake_inventory_item())
        for diff in range(-9, 10):
            diff = Decimal(diff)
            price_was = random_price()
            price_now = price_was + diff
            bp_change = BuyPriceChange(
                supplier_item=supp_item,
                price_was=price_was,
                price_now=price_now)
            self.assertEqual(bp_change.price_diff, diff)

    def test_price_diff_abs(self):
        """
        price_diff_abs is equal to absolute difference between price_now and 
        price_was.
        """
        supp_item = fake_supplier_item(fake_inventory_item())
        for diff in range(-9, 10):
            diff = Decimal(diff)
            price_was = random_price()
            price_now = price_was + diff
            bp_change = BuyPriceChange(
                supplier_item=supp_item,
                price_was=price_was,
                price_now=price_now)
            self.assertEqual(bp_change.price_diff_abs, abs(diff))

    def test_price_diff_percentage(self):
        """
        price_diff_percentage is equal to difference between price_now and 
        price_was.
        """
        supp_item = fake_supplier_item(fake_inventory_item())
        for diff in range(-9, 10):
            diff = Decimal(diff)
            price_was = random_price()
            price_now = price_was + diff
            diff_percentage = diff / price_was
            bp_change = BuyPriceChange(
                supplier_item=supp_item,
                price_was=price_was,
                price_now=price_now)
            self.assertEqual(bp_change.price_diff_percentage, diff_percentage)


class SellPriceChangeTests(PXITestCase):

    def test_price_differs(self):
        """
        price_differs is true when any of the price diffs are nonzero.
        """
        pr_item = fake_price_region_item(
            fake_inventory_item(), fake_price_rule())
        for index in range(6):
            price = random_price()
            self.assertNotEqual(price, Decimal(0))
            sp_change = SellPriceChange(
                price_region_item=pr_item,
                price_diffs=[Decimal("0.00") for _ in range(6)])
            sp_change.price_diffs[index] = price
            self.assertTrue(sp_change.price_differs)

    def test_price_0_differs(self):
        """
        price_0_differs is true only when the first price differs.
        """
        pr_item = fake_price_region_item(
            fake_inventory_item(), fake_price_rule())
        for index in range(6):
            price = random_price()
            self.assertNotEqual(price, Decimal(0))
            sp_change = SellPriceChange(
                price_region_item=pr_item,
                price_diffs=[Decimal("0.00") for _ in range(6)])
            sp_change.price_diffs[index] = price
            if index == 0:
                self.assertTrue(sp_change.price_0_differs)
            else:
                self.assertFalse(sp_change.price_0_differs)
