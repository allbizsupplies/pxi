
import unittest

from tests.exporters import ExporterTests
from tests.importers import ImporterTests
from tests.fetchers import FetcherTests
from tests.operations import OperationTests
from tests.price_calc import PriceCalcTests
from tests.spl_update import SPLUpdateTests
from tests.web_update import WebUpdateTests

testloader = unittest.TestLoader()

testcases = [
    FetcherTests,
    ImporterTests,
    ExporterTests,
    OperationTests,
    PriceCalcTests,
    SPLUpdateTests,
    WebUpdateTests,
]

testsuites = [
    testloader.loadTestsFromTestCase(testcase)
    for testcase in testcases
]

combined_suite = unittest.TestSuite(testsuites)

unittest.TextTestRunner(verbosity=2, buffer=True).run(combined_suite)
