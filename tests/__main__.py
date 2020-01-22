
import unittest

from tests.exporters import ExporterTests
from tests.importers import ImporterTests
from tests.price_calc import PriceCalcTests

testloader = unittest.TestLoader()

testcases = [
    PriceCalcTests,
    ImporterTests,
    ExporterTests,
]

testsuites = [
    testloader.loadTestsFromTestCase(testcase)
    for testcase in testcases
]

combined_suite = unittest.TestSuite(testsuites)

unittest.TextTestRunner(verbosity=2).run(combined_suite)
