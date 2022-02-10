from decimal import Decimal
from random import randint
from pxi.models import SupplierItem

from pxi.spl_update import update_supplier_items
from tests import DatabaseTestCase
from tests.fakes import (
    fake_inventory_item,
    fake_supplier_item,
    fake_supplier_pricelist_item,
    random_item_code,
    random_string,
    random_uom)


class SPLUpdateTests(DatabaseTestCase):

    def test_update_supplier_items(self):
        """
        Updates price on SupplierItems, returns PriceChanges and UOMErrors.
        """
        inv_item = fake_inventory_item()
        supp_items = [
            fake_supplier_item(inv_item),
            fake_supplier_item(inv_item),
            fake_supplier_item(inv_item),
            fake_supplier_item(inv_item),
        ]
        self.seed([inv_item] + supp_items)
        spl_items = [
            # Valid SupplierPricelistItem.
            fake_supplier_pricelist_item(supp_items[0], {
                "supp_price": Decimal(supp_items[0].buy_price) * Decimal(2),
            }),
            # Duplicate SupplierPricelistItem.
            fake_supplier_pricelist_item(supp_items[0], {
                "supp_price": Decimal(supp_items[0].buy_price) * Decimal(3),
            }),
            # SupplierPricelistItem that doesn't match any SupplierItem.
            fake_supplier_pricelist_item(fake_supplier_item(inv_item)),
        ]

        price_changes = update_supplier_items(
            spl_items, self.db_session)

        self.assertEqual(len(price_changes), len(spl_items) - 2)
