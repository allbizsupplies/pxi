from decimal import Decimal

from pxi.analysis import (
    extract_terms,
    compare_terms,
    calculate_similarity,
    DIRECT_HIT_MULTIPLIER,
    HIT_MULTIPLIER,
    MISS_MULTIPLIER
)
from tests import DatabaseTestCase
from tests.fixtures.models import random_inventory_item


class AnalysisTests(DatabaseTestCase):

    def test_extract_terms(self):
        fixtures = [
            ("Item 1 of 5", ["item", "1", "5"]),
            ("Item  2", ["item", "2"]),
            ("Item 3 50 x 60 cm", ["item", "3", "50", "60", "cm"]),
            ("Item 4 50x60cm", ["item", "4", "50x60cm"]),
            ("Item 5 and 6", ["item", "5", "6"]),
        ]

        for string, expected_result in fixtures:
            self.assertEqual(expected_result, extract_terms(string))

    def test_compare_terms(self):
        subject = ["A", "B", "C"]

        fixtures = [
            (["A", "B"], {"hits": 2, "direct_hits": 2, "misses": 1}),
            (["A", "C", "B"], {"hits": 3, "direct_hits": 1, "misses": 0}),
            (["A", "B", "C", "D"], {"hits": 3, "direct_hits": 3, "misses": 1}),
        ]

        for inputs, expected_result in fixtures:
            self.assertEqual(expected_result, compare_terms(subject, inputs))

    def test_calculate_similarity(self):
        inputs = [
            {"hits": 2, "direct_hits": 2, "misses": 1},
            {"hits": 3, "direct_hits": 1, "misses": 0},
            {"hits": 3, "direct_hits": 3, "misses": 1},
        ]

        for input in inputs:
            expected_result = input["hits"] * HIT_MULTIPLIER \
                + input["direct_hits"] * DIRECT_HIT_MULTIPLIER \
                - input["misses"] * MISS_MULTIPLIER
            result = calculate_similarity(
                input["hits"], input["direct_hits"], input["misses"])
            self.assertEqual(expected_result, result)
