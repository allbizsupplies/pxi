import csv
from datetime import date
from decimal import Decimal
import os
import pathlib
import random

from pxi.enum import WebStatus
from pxi.exporters import (
    export_downloaded_images_report,
    export_price_changes_report,
    export_pricelist,
    export_product_price_task,
    export_product_web_sortcode_task,
    export_contract_item_task,
    export_supplier_pricelist,
    export_supplier_price_changes_report,
    export_tickets_list)
from pxi.price_calc import recalculate_sell_prices
from pxi.report import ReportReader
from pxi.spl_update import SPL_FIELDNAMES
from tests import DatabaseTestCase
from tests.fixtures.models import (
    random_contract,
    random_inventory_item,
    random_pricelist,
    random_string,
    random_supplier_item,
    random_warehouse_stock_item,
    random_web_sortcode)


class ExporterTests(DatabaseTestCase):

    def setUp(self):
        super().setUp()
        pathlib.Path("tmp").mkdir(parents=True, exist_ok=True)

    def test_export_price_changes_report(self):
        """Export price updates to XLSX report."""
        report_filepath = "tmp/test_price_changes_report.xlsx"
        item_count = 5
        price_region_items = random_pricelist(items=item_count)
        price_changes = recalculate_sell_prices(
            price_region_items, self.session)
        export_price_changes_report(report_filepath, price_changes)
        report_reader = ReportReader(report_filepath)
        fieldnames = [
            "item_code", "region", "brand", "apn", "description", "price_rule",
        ] + [
            "price_{}_was".format(i) for i in range(5)
        ] + [
            "price_{}_now".format(i) for i in range(5)
        ] + [
            "price_{}_diff".format(i) for i in range(5)
        ] + [
            "price_{}_diff_%".format(i) for i in range(5)
        ] + [
            "quantity_{}".format(i) for i in range(1, 5)
        ]
        for fieldname in fieldnames:
            self.assertIn(fieldname, report_reader.fieldnames)
        data = report_reader.load()
        self.assertEqual(item_count, len(data))
        os.remove(report_filepath)

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
                "0",
                "",
                expected_date,
                "",
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
        """Export contract item task to file."""
        task_filepath = "tmp/test_contract_item_task.txt"
        item_count = 5
        contract_items = random_contract(items=item_count)
        export_contract_item_task(task_filepath, contract_items)
        file = open(task_filepath)
        csv_reader = csv.DictReader(file, dialect="excel-tab")
        expected_fieldnames = ["contract", "item_code"]
        for i in range(1, 7):
            expected_fieldnames.append("price_{}".format(i))
        self.assertListEqual(csv_reader.fieldnames, expected_fieldnames)
        file.close()
        # TODO validate values in rows.
        os.remove(task_filepath)

    def test_export_tickets_list(self):
        """Export tickets list to file."""
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

    def test_export_supplier_pricelist(self):
        """Export supplier pricelist to file."""
        supplier_pricelist_filepath = "tmp/test_supplier_pricelist.csv"
        item_count = 5
        supplier_items = []
        for i in range(item_count):
            inventory_item = random_inventory_item()
            # pylint:disable=no-member
            self.session.add(inventory_item)
            supplier_item = random_supplier_item(inventory_item)
            # pylint:disable=no-member
            self.session.add(supplier_item)
            supplier_items.append(supplier_item)
        export_supplier_pricelist(supplier_pricelist_filepath, supplier_items)
        file = open(supplier_pricelist_filepath)
        supplier_pricelist_reader = csv.DictReader(file, SPL_FIELDNAMES)
        supplier_pricelist_items = list(supplier_pricelist_reader)
        for i, supplier_pricelist_item in enumerate(supplier_pricelist_items):
            supplier_item = supplier_items[i]
            expected_item_values = {
                "supplier_code": supplier_item.code,
                "supp_item_code": supplier_item.item_code,
                "item_code": supplier_item.inventory_item.code,
                "supp_price_1": str(supplier_item.buy_price),
            }
            for key, expected_value in expected_item_values.items():
                value = supplier_pricelist_item[key]
                self.assertEqual(expected_value, value, "'{}' != '{}' for key: {}".format(
                    expected_value, value, key
                ))
        file.close()
        os.remove(supplier_pricelist_filepath)

    def test_export_supplier_price_changes_report(self):
        """Export supplier price updates to XLSX report."""
        report_filepath = "tmp/test_supplier_price_changes_report.xlsx"
        item_count = 5
        price_changes = []
        # pylint:disable=unused-variable
        for i in range(item_count):
            inventory_item = random_inventory_item()
            # pylint:disable=no-member
            self.session.add(inventory_item)
            supplier_item = random_supplier_item(inventory_item)
            # pylint:disable=no-member
            self.session.add(supplier_item)
            price_was = supplier_item.buy_price
            price_diff = price_was * Decimal(random.randint(-10, 10)) / 100
            price_diff_percentage = Decimal(1)
            if price_was != Decimal(0):
                price_diff_percentage = price_diff / price_was
            price_now = price_was + price_diff
            price_changes.append({
                "supplier_item": supplier_item,
                # Create price difference between +/- 10%.
                "price_was": price_was,
                "price_now": price_now,
                "price_diff": price_diff,
                "price_diff_percentage": price_diff_percentage,
            })
        uom_errors = []
        export_supplier_price_changes_report(
            report_filepath, price_changes, uom_errors)
        report_reader = ReportReader(report_filepath)
        fieldnames = [
            "item_code", "supplier", "brand", "apn", "description",
            "price_was", "price_now", "price_diff", "price_diff_%",
        ]
        for fieldname in fieldnames:
            self.assertIn(fieldname, report_reader.fieldnames)
        data = report_reader.load()
        self.assertEqual(item_count, len(data))
        os.remove(report_filepath)

    def test_export_downloaded_images_report(self):
        """Export downloaded images report to file."""
        report_filepath = "tmp/test_export_downloaded_images_report.xlsx"
        images = []
        item_count = 5
        for i in range(item_count):
            inventory_item = random_inventory_item()
            filename = "{}.jpg".format(inventory_item.code) if i > 0 else None
            images.append({
                "inventory_item": inventory_item,
                "source": random_string(3),
                "filename": filename
            })
        export_downloaded_images_report(report_filepath, images)
        # TODO validate values in rows.
        os.remove(report_filepath)

    def test_export_product_web_sortcode_task(self):
        """Export product price update task to file."""
        task_filepath = "tmp/test_product_web_sortcode_task.txt"
        item_count = 5

        def inventory_item_with_web_sortcode():
            inventory_item = random_inventory_item()
            inventory_item.web_sortcode = random_string(4)
            inventory_item.web_status = WebStatus.ACTIVE
            # pylint:disable=no-member
            self.session.commit()
            return inventory_item
        # pylint:disable=unused-variable
        inventory_items = [
            inventory_item_with_web_sortcode() for i in range(item_count)]

        export_product_web_sortcode_task(task_filepath, inventory_items)
        file = open(task_filepath)
        csv_reader = csv.DictReader(file, dialect="excel-tab")
        expected_fieldnames = ["item_code", "web_active", "web_sortcode"]
        self.assertListEqual(csv_reader.fieldnames, expected_fieldnames)
        file.close()
        # TODO validate values in rows.
        os.remove(task_filepath)
