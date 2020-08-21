from decimal import Decimal
import random

from pxi.models import SupplierItem
from pxi.spl_update import update_supplier_items
from tests import DatabaseTestCase
from tests.fixtures.models import (
    random_supplier_item,
    random_inventory_item)


class SPLUpdateTests(DatabaseTestCase):

    def test_update_supplier_items(self):
        """Apply supplier pricelist prices to supplier items."""
        item_count = 10
        supplier_items = []
        for i in range(item_count):
            inventory_item = random_inventory_item()
            self.session.add(inventory_item)
            supplier_item = random_supplier_item(inventory_item)
            self.session.add(supplier_item)
            supplier_items.append(supplier_item)

        def random_supplier_pricelist_item(supplier_item):
            supplier_code = supplier_item.code
            item_code = supplier_item.item_code
            # Mock a price increase by multiplying the existing buy price.
            buy_price = supplier_item.buy_price * \
                Decimal(random.randint(200, 400)) / 100
            return {
                "supplier_code": supplier_code,
                "supp_item_code": item_code,
                "supp_price_1": buy_price,
            }
        supplier_pricelist_items = [random_supplier_pricelist_item(item)
                                    for item in supplier_items]

        price_changes = update_supplier_items(
            supplier_pricelist_items, self.session)
        self.assertEqual(10, len(price_changes))
