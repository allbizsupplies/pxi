import pathlib
import os

from pxi.operations import operations
from tests import DatabaseTestCase

class OperationTests(DatabaseTestCase):

    def setUp(self):
        super().setUp()
        pathlib.Path("tmp").mkdir(parents=True, exist_ok=True)

    def test_price_calc(self):
        price_changes_report="tmp/price_changes_report.xlsx"
        pricelist="tmp/pricelist.csv"
        product_price_task="tmp/product_price_task.txt"
        contract_item_task="tmp/contract_item_task.txt"
        tickets_list="tmp/tickets_list.txt"
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
