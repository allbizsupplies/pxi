import random

from pxi.enum import WebStatus
from pxi.web_update import update_product_menu
from tests import DatabaseTestCase
from tests.fixtures.models import (
    random_inventory_item,
    random_inventory_web_data_item,
    random_price_rule,
    random_price_region_item,
    random_web_sortcode)


class WebUpdateTests(DatabaseTestCase):

    def test_update_product_menu(self):
        """Map price rules to web sortcodes."""
        item_count = 10
        inventory_items = []
        web_sortcode_mappings = {}

        # pylint:disable=unused-variable
        for i in range(item_count):
            inventory_item = random_inventory_item()
            # pylint:disable=no-member
            self.db_session.add(inventory_item)
            web_sortcode = random_web_sortcode()
            # pylint:disable=no-member
            self.db_session.add(web_sortcode)
            price_rule = random_price_rule()
            # pylint:disable=no-member
            self.db_session.add(price_rule)
            price_region_item = random_price_region_item(
                inventory_item, price_rule)
            # pylint:disable=no-member
            self.db_session.add(price_region_item)
            web_sortcode_mappings[price_rule.code] = web_sortcode
            inventory_web_data_item = random_inventory_web_data_item(inventory_item, web_sortcode)
            # pylint:disable=no-member
            self.db_session.add(inventory_web_data_item)
            # pylint:disable=no-member
            self.db_session.commit()
            inventory_items.append(inventory_item)

        updated_inventory_items = update_product_menu(
            inventory_items, web_sortcode_mappings, self.db_session)
        self.assertEqual(10, len(updated_inventory_items))

        web_sortcodes = web_sortcode_mappings.values()
        for inventory_item in updated_inventory_items:
            self.assertIn(inventory_item.inventory_web_data_item.web_sortcode, web_sortcodes)
