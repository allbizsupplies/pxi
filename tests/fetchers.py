from unittest.mock import MagicMock
import os

from pxi.fetchers import get_fetcher, get_fetchers, ACO, CSS, GNS, SAT
from pxi.models import InventoryItem
from tests import DatabaseTestCase
from tests.fixtures.models import (
    random_inventory_item,
    random_string,
    random_supplier_item)


FETCHER_CLASSES = [
    ACO, CSS, GNS, SAT
]


class FetcherTests(DatabaseTestCase):

    def test_get_fetchers(self):
        for fetcher_class in FETCHER_CLASSES:
            fetcher = get_fetcher(fetcher_class.__name__)
            self.assertIsInstance(fetcher, fetcher_class)

    def test_fetch_url(self):
        """Fetch image URLs."""
        inventory_item = random_inventory_item()
        # pylint:disable=no-member
        for fetcher_class in FETCHER_CLASSES:
            supplier_item = random_supplier_item(inventory_item)
            supplier_item.code = fetcher_class.__name__
            # pylint:disable=no-member

        fetchers = get_fetchers(inventory_item)
        for fetcher in fetchers:
            url = fetcher.get_image_url(inventory_item)
            self.assertIsInstance(url, str)

    def test_download_image(self):
        """Download image"""
        sku = "107001"
        inventory_item = random_inventory_item()
        supplier_item = random_supplier_item(inventory_item)
        supplier_item.code = "ACO"
        supplier_item.item_code = sku
        expected_filepath = os.path.join(
            "tmp", "{}.jpg".format(inventory_item.code))
        fetchers = get_fetchers(inventory_item)
        for fetcher in fetchers:
            filepath = fetcher.download_image(inventory_item, "tmp")
            self.assertTrue(os.path.exists(filepath))
            self.assertEqual(expected_filepath, filepath)
            os.remove(filepath)
