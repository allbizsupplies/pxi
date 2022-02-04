
import unittest

from tests.analysis import AnalysisTests
from tests.commands import CommandTests
from tests.exporters import ExporterTests
from tests.image import ImageTests
from tests.importers import ImporterTests
from tests.price_calc import PriceCalcTests
from tests.spl_update import SPLUpdateTests
from tests.web_update import WebUpdateTests

testloader = unittest.TestLoader()

testcases = [
    AnalysisTests,
    CommandTests,
    ExporterTests,
    ImageTests,
    ImporterTests,
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
