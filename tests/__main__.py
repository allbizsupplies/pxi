
import unittest

from tests.exporters import ExporterTests
from tests.importers import ImporterTests
from tests.operations import OperationTests
from tests.price_calc import PriceCalcTests
from tests.spl_update import SPLUpdateTests

testloader = unittest.TestLoader()

testcases = [
    PriceCalcTests,
    ImporterTests,
    ExporterTests,
    OperationTests,
    SPLUpdateTests,
]

testsuites = [
    testloader.loadTestsFromTestCase(testcase)
    for testcase in testcases
]

combined_suite = unittest.TestSuite(testsuites)

unittest.TextTestRunner(verbosity=2, buffer=True).run(combined_suite)
