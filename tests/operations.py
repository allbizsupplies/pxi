import pathlib
import os

from pxi.operations import operations
from tests import DatabaseTestCase


class OperationTests(DatabaseTestCase):

    def setUp(self):
        super().setUp()
        pathlib.Path("tmp").mkdir(parents=True, exist_ok=True)

    def test_price_calc(self):
        price_changes_report = "tmp/price_changes_report.xlsx"
        pricelist = "tmp/pricelist.csv"
        product_price_task = "tmp/product_price_task.txt"
        contract_item_task = "tmp/contract_item_task.txt"
        tickets_list = "tmp/tickets_list.txt"
        operations.price_calc(
            inventory_items_datagrid="tests/fixtures/inventory_items.xlsx",
            price_rules_datagrid="tests/fixtures/price_rules.xlsx",
            pricelist_datagrid="tests/fixtures/pricelist.xlsx",
            contract_items_datagrid="tests/fixtures/contract_items.xlsx",
            price_changes_report=price_changes_report,
            pricelist=pricelist,
            product_price_task=product_price_task,
            contract_item_task=contract_item_task,
            tickets_list=tickets_list
        )
        os.remove(price_changes_report)
        os.remove(pricelist)
        os.remove(product_price_task)
        os.remove(contract_item_task)
        os.remove(tickets_list)

    def test_generate_spl(self):
        supplier_price_changes_report = "tmp/supplier_price_changes_report.xlsx"
        updated_supplier_pricelist = "tmp/supplier_pricelist.csv"
        operations.generate_spl(
            inventory_items_datagrid="tests/fixtures/inventory_items.xlsx",
            supplier_items_datagrid="tests/fixtures/supplier_items.xlsx",
            supplier_pricelist="tests/fixtures/supplier_pricelist.csv",
            supplier_price_changes_report=supplier_price_changes_report,
            updated_supplier_pricelist=updated_supplier_pricelist
        )
        os.remove(supplier_price_changes_report)
        os.remove(updated_supplier_pricelist)

    def test_web_sort(self):
        product_web_sortcode_task = "tmp/product_web_sortcode_task.txt"
        operations.web_sort(
            inventory_items_datagrid="tests/fixtures/inventory_items.xlsx",
            price_rules_datagrid="tests/fixtures/price_rules.xlsx",
            pricelist_datagrid="tests/fixtures/pricelist.xlsx",
            inventory_metadata="tests/fixtures/inventory_metadata.xlsx",
            product_web_sortcode_task=product_web_sortcode_task
        )
        # os.remove(product_web_sortcode_task)
