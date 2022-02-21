
import unittest

from tests.analysis import AnalysisTests
from tests.commands import CommandTests
from tests.dataclasses import BuyPriceChangeTests, SellPriceChangeTests
from tests.exporters import ExporterTests
from tests.image import ImageFetchingTests, ImageFormattingTests
from tests.importers import ImporterTests
from tests.price_calc import PriceCalcTests
from tests.spl_update import SPLUpdateTests
from tests.web_update import WebUpdateTests

testloader = unittest.TestLoader()

testcases = [
    AnalysisTests,
    BuyPriceChangeTests,
    CommandTests,
    ExporterTests,
    ImageFetchingTests,
    ImageFormattingTests,
    ImporterTests,
    PriceCalcTests,
    SellPriceChangeTests,
    SPLUpdateTests,
    WebUpdateTests,
]

testsuites = [
    testloader.loadTestsFromTestCase(testcase)
    for testcase in testcases
]

combined_suite = unittest.TestSuite(testsuites)

unittest.TextTestRunner(verbosity=2, buffer=True).run(combined_suite)
