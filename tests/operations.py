import pathlib
import os

from pxi.operations import operations
from tests import DatabaseTestCase


def delete_temporary_file(filepath):
    try:
        os.remove(filepath)
    except PermissionError:
        return


class OperationTests(DatabaseTestCase):

    def setUp(self):
        super().setUp()
        pathlib.Path("tmp").mkdir(parents=True, exist_ok=True)
        
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
        delete_temporary_file(supplier_price_changes_report)
        delete_temporary_file(updated_supplier_pricelist)

    def test_missing_gtin(self):
        gtin_report = "tmp/test_gtin_report.xlsx"
        operations.missing_gtin(
            inventory_items_datagrid="tests/fixtures/inventory_items.xlsx",
            gtin_items_datagrid="tests/fixtures/gtin_items.xlsx",
            gtin_report=gtin_report
        )
        # delete_temporary_file(gtin_report)

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
        delete_temporary_file(price_changes_report)
        delete_temporary_file(pricelist)
        delete_temporary_file(product_price_task)
        delete_temporary_file(contract_item_task)
        delete_temporary_file(tickets_list)

    def test_web_update(self):
        web_product_menu_data = "tmp/test_web_update__web_product_menu_data.txt"
        web_data_updates_report = "tmp/test_web_update__web_data_updates_report.xlsx"
        operations.web_update(
            inventory_items_datagrid="tests/fixtures/inventory_items.xlsx",
            inventory_web_data_items_datagrid="tests/fixtures/inventory_web_data_items.xlsx",
            price_rules_datagrid="tests/fixtures/price_rules.xlsx",
            pricelist_datagrid="tests/fixtures/pricelist.xlsx",
            inventory_metadata="tests/fixtures/inventory_metadata.xlsx",
            web_product_menu_data=web_product_menu_data,
            web_data_updates_report=web_data_updates_report
        )
        delete_temporary_file(web_product_menu_data)
        delete_temporary_file(web_data_updates_report)
