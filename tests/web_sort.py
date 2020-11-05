import random

from pxi.enum import WebStatus
from pxi.web_sort import add_web_sortcodes
from tests import DatabaseTestCase
from tests.fixtures.models import (
    random_inventory_item,
    random_price_rule,
    random_price_region_item,
    random_web_sortcode)


class WebSortTests(DatabaseTestCase):

    def test_update_web_sortcodes(self):
        """Map price rules to web sortcodes."""
        item_count = 10
        price_rules = []
        price_region_items = []
        web_sortcode_mappings = {}

        # pylint:disable=unused-variable
        for i in range(item_count):
            inventory_item = random_inventory_item()
            inventory_item.web_status = WebStatus.ACTIVE
            # pylint:disable=no-member
            self.session.add(inventory_item)
            web_sortcode = random_web_sortcode()
            # pylint:disable=no-member
            self.session.add(web_sortcode)
            price_rule = random_price_rule()
            # pylint:disable=no-member
            self.session.add(price_rule)
            price_rules.append(price_rule)
            price_region_item = random_price_region_item(
                inventory_item, price_rule)
            # pylint:disable=no-member
            self.session.add(price_region_item)
            price_region_items.append(price_region_item)
            web_sortcode_mappings[price_rule.code] = web_sortcode.code
            # pylint:disable=no-member
            self.session.commit()

        updated_inventory_items, skipped_inventory_items = add_web_sortcodes(
            price_region_items, web_sortcode_mappings, self.session)
        self.assertEqual(10, len(updated_inventory_items))

        web_sortcodes = web_sortcode_mappings.values()
        for inventory_item in updated_inventory_items:
            self.assertIn(inventory_item.web_sortcode, web_sortcodes)
