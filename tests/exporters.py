import csv
from datetime import date
import os
import pathlib


from pxi.exporters import (
    export_price_changes_report,
    export_pricelist,
    export_product_price_task,
    export_contract_item_task,
    export_tickets_list)
from pxi.price_calc import recalculate_sell_prices
from pxi.report import ReportReader
from tests import DatabaseTestCase
from tests.fixtures.models import (
    random_contract,
    random_inventory_item,
    random_pricelist,
    random_warehouse_stock_item
)


class ExporterTests(DatabaseTestCase):

    def setUp(self):
        super().setUp()
        pathlib.Path("tmp").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        super().tearDown()

    def test_export_price_changes_report(self):
        """Export price updates to XLSX report."""
        report_filepath = "tmp/test_report.xlsx"
        item_count = 5
        price_region_items = random_pricelist(items=item_count)
        price_changes = recalculate_sell_prices(price_region_items)
        export_price_changes_report(report_filepath, price_changes)
        report_reader = ReportReader(report_filepath)
        fieldnames = [
            "item_code", "brand", "apn", "description", "price_rule",
        ] + [
            "price_{}_was".format(i) for i in range(5)
        ] + [
            "price_{}_now".format(i) for i in range(5)
        ] + [
            "price_{}_diff".format(i) for i in range(5)
        ] + [
            "quantity_{}".format(i) for i in range(1, 5)
        ]
        for fieldname in fieldnames:
            self.assertIn(fieldname, report_reader.fieldnames)
        data = report_reader.load()
        self.assertEqual(item_count, len(data))
        # TODO assert that row data matches some expected values.
        # TODO expect contract items worksheet as well.
        for row in data:
            for value in row.values():
                self.assertIsNotNone(value)
        os.remove("tmp/test_report.xlsx")

    def test_export_pricelist(self):
        """Export price region items to Pronto pricelist import file."""
        pricelist_filepath = "tmp/test_pricelist.csv"
        item_count = 5
        price_region_items = random_pricelist(items=item_count)
        export_pricelist(pricelist_filepath, price_region_items)
        file = open(pricelist_filepath)
        rows = list(csv.reader(file))
        file.close()
        expected_date = date.today().strftime("%d-%b-%Y")
        for i, data in enumerate(rows):
            price_region_item = price_region_items[i]
            inventory_item = price_region_item.inventory_item
            expected_data = [
                inventory_item.code,
                price_region_item.code,
                str(price_region_item.price_0),
                str(price_region_item.quantity_1),
                str(price_region_item.quantity_2),
                str(price_region_item.quantity_3),
                str(price_region_item.quantity_4),
                str(price_region_item.price_1),
                str(price_region_item.price_2),
                str(price_region_item.price_3),
                str(price_region_item.price_4),
                str(price_region_item.rrp_excl_tax),
                str(price_region_item.rrp_incl_tax),
                "",
                expected_date,
                "",
            ]
            self.assertListEqual(data, expected_data)
        os.remove(pricelist_filepath)

    def test_export_product_price_task(self):
        """Export product price update task to file."""
        task_filepath = "tmp/test_product_price_task.txt"
        item_count = 5
        price_region_items = random_pricelist(items=item_count)
        export_product_price_task(task_filepath, price_region_items)
        file = open(task_filepath)
        csv_reader = csv.DictReader(file, dialect="excel-tab")
        expected_fieldnames = ["item_code", "region"] + [
            "price_{}".format(i) for i in range(5)]
        self.assertListEqual(csv_reader.fieldnames, expected_fieldnames)
        file.close()
        # TODO validate values in rows.
        os.remove(task_filepath)

    def test_export_contract_item_task(self):
        """Export product price update task to file."""
        task_filepath = "tmp/test_contract_item_task.txt"
        item_count = 5
        contract_items = random_contract(items=item_count)
        export_contract_item_task(task_filepath, contract_items)
        file = open(task_filepath)
        csv_reader = csv.DictReader(file, dialect="excel-tab")
        expected_fieldnames = ["contract", "item_code"]
        for i in range(1, 7):
            expected_fieldnames.append("price_{}".format(i))
            expected_fieldnames.append("quantity_{}".format(i))
        self.assertListEqual(csv_reader.fieldnames, expected_fieldnames)
        file.close()
        # TODO validate values in rows.
        os.remove(task_filepath)

    def test_export_tickets_list(self):
        """Export product price update task to file."""
        tickets_list_filepath = "tmp/test_tickets_list.txt"
        item_count = 5
        warehouse_stock_items = []
        for i in range(item_count):
            inventory_item = random_inventory_item()
            warehouse_stock_item = random_warehouse_stock_item(inventory_item)
            warehouse_stock_items.append(warehouse_stock_item)
        export_tickets_list(tickets_list_filepath, warehouse_stock_items)
        file = open(tickets_list_filepath)
        item_codes = [row[0] for row in list(csv.reader(file))]
        file.close()
        for i, item_code in enumerate(item_codes):
            expected_item_code = warehouse_stock_items[i].inventory_item.code
            self.assertEqual(item_code, expected_item_code)
        os.remove(tickets_list_filepath)