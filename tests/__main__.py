
import unittest

from tests.analysis import AnalysisTests
from tests.commands import CommandTests
from tests.config import ConfigTests
from tests.dataclasses import BuyPriceChangeTests, SellPriceChangeTests
from tests.datagrid import DatagridTests
from tests.exporters import ExporterTests
from tests.image import ImageFetchingTests, ImageFormattingTests
from tests.importers import ImporterTests
from tests.price_calc import PriceCalcTests
from tests.report import (
    ReportFieldTests,
    NumberFieldTests,
    StringFieldTests,
    ReportWriterTests)
from tests.scp import SCPClientTests
from tests.spl_update import SPLUpdateTests
from tests.web_update import WebUpdateTests

testloader = unittest.TestLoader()

testcases = [
    AnalysisTests,
    BuyPriceChangeTests,
    CommandTests,
    ConfigTests,
    DatagridTests,
    ExporterTests,
    ImageFetchingTests,
    ImageFormattingTests,
    ImporterTests,
    NumberFieldTests,
    PriceCalcTests,
    ReportFieldTests,
    ReportWriterTests,
    SCPClientTests,
    SellPriceChangeTests,
    SPLUpdateTests,
    StringFieldTests,
    WebUpdateTests,
]

testsuites = [
    testloader.loadTestsFromTestCase(testcase)
    for testcase in testcases
]

combined_suite = unittest.TestSuite(testsuites)

unittest.TextTestRunner(verbosity=2, buffer=True).run(combined_suite)
