import random

from pxi.enum import WebStatus
from pxi.models import PriceRegionItem
from pxi.web_update import update_product_menu
from tests import DatabaseTestCase
from tests.fakes import (
    fake_inv_web_data_item,
    fake_inventory_item,
    fake_price_region_item,
    fake_price_rule,
    fake_web_menu_item)


class WebUpdateTests(DatabaseTestCase):

    def test_update_product_menu(self):
        """
        Maps price rules to WebMenuItems.
        """
        inv_item = fake_inventory_item()
        web_menu_item = fake_web_menu_item()
        price_rule = fake_price_rule()
        price_region_item = fake_price_region_item(inv_item, price_rule, {
            "code": PriceRegionItem.DEFAULT_REGION_CODE
        })
        web_menu_item_mappings = {
            price_rule.code: web_menu_item,
        }
        inv_web_data_item = fake_inv_web_data_item(inv_item, None)
        self.seed([
            inv_item,
            web_menu_item,
            price_rule,
            price_region_item
        ])

        inv_web_data_items = update_product_menu(
            [inv_web_data_item], web_menu_item_mappings, self.db_session)

        self.assertEqual(len(inv_web_data_items), 1)
        inv_web_data_item = inv_web_data_items[0]
        self.assertEqual(inv_web_data_item.inventory_item, inv_item)
        self.assertEqual(inv_web_data_item.web_menu_item, web_menu_item)
