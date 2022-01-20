
from datetime import datetime
from random import randint, choice as random_choice
import string
import time
from unittest.mock import patch

from pxi.enum import ItemType, ItemCondition, PriceBasis
from pxi.importers import (
    import_contract_items,
    import_inventory_items,
    import_inventory_web_data_items,
    import_gtin_items,
    import_price_region_items,
    import_price_rules,
    import_supplier_items,
    import_supplier_pricelist_items,
    import_warehouse_stock_items,
    import_web_sortcodes,
    import_web_sortcode_mappings,
    import_website_images_report
)
from pxi.models import (
    ContractItem,
    InventoryItem,
    InventoryWebDataItem,
    GTINItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem,
    WebSortcode)
from tests import DatabaseTestCase
from tests.fakes import (
    fake_inventory_item,
    random_datetime,
    random_item_code,
    random_price_factor,
    random_price_string,
    random_quantity,
    random_string
)


def fake_inventory_items_datagrid_row(values={}):
    return {
        "item_code": values.get("item_code", random_item_code()),
        "item_description": values.get("item_description", random_string(30)),
        "description_2": values.get("description_2", random_string(30)),
        "description_3": values.get("description_3", random_string(30)),
        "unit": values.get("unit", random_string(4)),
        "brand_manuf": values.get("brand_manuf", random_string(3)),
        "manuf_apn_no": values.get("manuf_apn_no", random_string(20)),
        "group": values.get("group", random_string(4)),
        "creation_date": values.get("creation_date", random_datetime()),
        "status": values.get("status", ItemType.STOCKED_ITEM.value),
        "condition": values.get("condition", ItemCondition.NONE.value),
        "replacement_cost": values.get(
            "replacement_cost", random_price_string()),
        "whse": values.get("whse", random_string(3)),
        "minimum_stock": values.get("minimum_stock", randint(0, 100)),
        "maximum_stock": values.get("maximum_stock", 0),
        "on_hand": values.get("on_hand", randint(0, 100)),
        "bin_loc": values.get("bin_loc", random_string(8)),
        "bulk_loc": values.get("bulk_loc", random_string(8)),
    }


def fake_inventory_items_datagrid_rows(count):
    return [fake_inventory_items_datagrid_row() for _ in range(count)]


def fake_contract_items_datagrid_row(values={}):
    return {
        "item_code": values.get("item_code", random_string(6)),
        "contract_no": values.get("contract_no", random_string(6)),
        "price_1": values.get("price_1", random_price_string()),
        "price_2": values.get("price_2", random_price_string()),
        "price_3": values.get("price_3", random_price_string()),
        "price_4": values.get("price_4", random_price_string()),
        "price_5": values.get("price_5", random_price_string()),
        "price_6": values.get("price_6", random_price_string()),
    }


def fake_price_region_items_datagrid_row(values={}):
    return {
        "item_code": values.get("item_code", random_item_code()),
        "region": values.get("region", random_string(2)),
        "rule": values.get("rule", random_string(4)),
        "tax_rate": values.get("tax_rate", "10.0000%"),
        "pr_1_corpa_qty": values.get("pr_1_corpa_qty", random_quantity()),
        "pr_2_corp_b_qty": values.get("pr_2_corp_b_qty", random_quantity()),
        "pr_3_corp_c_qty": values.get("pr_3_corp_c_qty", random_quantity()),
        "pr_4_bulk_qty": values.get("pr_4_bulk_qty", random_quantity()),
        "w_sale_price": values.get("w_sale_price", random_price_string()),
        "pr_1_corpa": values.get("pr_1_corpa", random_price_string()),
        "pr_2_corp_b": values.get("pr_2_corp_b", random_price_string()),
        "pr_3_corp_c": values.get("pr_3_corp_c", random_price_string()),
        "pr_4_bulk": values.get("pr_4_bulk", random_price_string()),
        "retail_price": values.get("retail_price", "0.00"),
        "rrp_inc_tax": values.get("rrp_inc_tax", "0.00"),
    }


def fake_supplier_items_datagrid_row(values={}):
    return {
        "item_code": values.get("item_code", random_item_code()),
        "supplier": values.get("supplier", random_string(3)),
        "supplier_item": values.get("supplier_item", random_string(20)),
        "priority": values.get("priority", randint(1, 9)),
        "unit": values.get("unit", random_string(4)),
        "conv_factor": values.get("conv_factor", 1),
        "pack_qty": values.get("pack_qty", 1),
        "eoq": values.get("eoq", 1),
        "current_buy_price": values.get("current_buy_price", random_price_string()),
    }


def fake_gtin_items_datagrid_row(values={}):
    return {
        "item_code": values.get("item_code", random_item_code()),
        "gtin": values.get("gtin", random_item_code()),
        "uom": values.get("uom", random_string(4)),
        "conversion": values.get("conversion", 1),
    }


def fake_web_data_items_datagrid_row(values={}):
    return {
        "stock_code": values.get("stock_code"),
        "menu_name": values.get(
            "menu_name", f"{random_string(12)}/{random_string(12)}"),
        "description": values.get("description"),
    }


def fake_price_rules_datagrid_row(values={}):
    return {
        "rule": values.get("rule", random_string(4)),
        "comments": values.get("comments", random_string(20)),
        "price0_based_on": values.get(
            "price0_based_on", PriceBasis.REPLACEMENT_COST.value),
        "price1_based_on": values.get(
            "price1_based_on", PriceBasis.REPLACEMENT_COST.value),
        "price2_based_on": values.get(
            "price2_based_on", PriceBasis.REPLACEMENT_COST.value),
        "price3_based_on": values.get(
            "price3_based_on", PriceBasis.REPLACEMENT_COST.value),
        "price4_based_on": values.get(
            "price4_based_on", PriceBasis.REPLACEMENT_COST.value),
        "rec_retail_based_on": values.get(
            "rec_retail_based_on", PriceBasis.RRP_EXCL_TAX),
        "rrp_inc_tax_based_on": values.get(
            "rrp_inc_tax_based_on", PriceBasis.RRP_INCL_TAX),
        "price0_factor": values.get("price0_factor", random_price_factor()),
        "price1_factor": values.get("price1_factor", random_price_factor()),
        "price2_factor": values.get("price2_factor", random_price_factor()),
        "price3_factor": values.get("price3_factor", random_price_factor()),
        "price4_factor": values.get("price4_factor", random_price_factor()),
        "rec_retail_factor": values.get("rec_retail_factor", 0),
        "rrp_inc_tax_factor": values.get("rrp_inc_tax_factor", 0),
    }


def fake_price_rules_datagrid_rows(count):
    return [fake_price_rules_datagrid_row() for _ in range(count)]


def fake_web_sortcodes_row(values={}):
    return {
        "parent_name": values.get("parent_name", random_string(10)),
        "child_name": values.get("child_name", random_string(10))
    }


def fake_web_sortcodes_rows(count):
    return [fake_web_sortcodes_row() for _ in range(count)]


def fake_web_sortcodes_mappings_row(values={}):
    return {
        "rule_code": values.get("rule_code", random_string(4)),
        "menu_name": values.get(
            "menu_name", f"{random_string(10)}/{random_string(10)}"),
    }


def fake_supplier_pricelist_row(values={}):
    return {
        "item_code": values.get("item_code", random_item_code()),
        "supplier_code": values.get("supplier_code", random_string(3)),
        "supp_item_code": values.get("supp_item_code", random_item_code()),
        "supp_uom": values.get("supp_uom", random_string(4)),
        "supp_price_1": values.get("supp_price_1", random_price_string()),
    }


def fake_supplier_pricelist_rows(count):
    return [fake_supplier_pricelist_row() for _ in range(count)]


def fake_website_images_report_row(values={}):
    return {
        "productcode": values.get("productcode", random_item_code()),
        "picture1": values.get("picture1", random_price_string()),
        "picture2": values.get("picture2"),
        "picture3": values.get("picture3"),
        "picture4": values.get("picture4"),
    }


class ImporterTests(DatabaseTestCase):

    @patch("pxi.importers.load_rows")
    def test_import_inventory_items(self, mock_load_rows):
        """
        Imports inventory items from Pronto datagrid.
        """

        # Seed the database with two InventoryItems and then mock an import
        # for another 10, but where the first imported row has the same item
        # code as the first seeded item.
        seeded_inv_items = [
            fake_inventory_item(),
            fake_inventory_item(),
        ]
        self.seed(seeded_inv_items)
        fake_inv_items_datagrid_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_inventory_items_datagrid_rows(imported_items_count)
        rows[0]["item_code"] = seeded_inv_items[0].code

        # Run the import.
        mock_load_rows.return_value = rows
        import_inventory_items(
            fake_inv_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_inv_items_datagrid_filepath)

        # Expect to insert 9 items, update 1, leaving a total of 11
        # InventoryItems in the database.
        # pylint:disable=no-member
        inventory_items = self.session.query(InventoryItem).all()
        expected_items_count = 1 + imported_items_count
        self.assertEqual(len(inventory_items), expected_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_contract_items(self, mock_load_rows):
        """
        Import Contract Items from Pronto datagrid.
        """
        fake_inv_items_datagrid_filepath = random_string(20)
        fake_con_items_datagrid_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_inventory_items_datagrid_rows(imported_items_count)
        mock_load_rows.return_value = rows
        import_inventory_items(
            fake_inv_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_inv_items_datagrid_filepath)
        item_codes = [row["item_code"] for row in rows]
        rows = [fake_contract_items_datagrid_row({
            "item_code": item_code,
        }) for item_code in item_codes]
        mock_load_rows.return_value = rows
        import_contract_items(
            fake_con_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_con_items_datagrid_filepath)
        self.assertEqual(mock_load_rows.call_count, 2)
        # pylint:disable=no-member
        contract_items = self.session.query(ContractItem).all()
        self.assertEqual(len(contract_items), imported_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_warehouse_stock_items(self, mock_load_rows):
        """
        Import Warehouse Stock Items from Pronto datagrid.
        """
        fake_inv_items_datagrid_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_inventory_items_datagrid_rows(imported_items_count)
        mock_load_rows.return_value = rows
        import_inventory_items(
            fake_inv_items_datagrid_filepath,
            self.session)
        import_warehouse_stock_items(
            fake_inv_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_inv_items_datagrid_filepath)
        self.assertEqual(mock_load_rows.call_count, 2)
        # pylint:disable=no-member
        warehouse_stock_items = self.session.query(WarehouseStockItem).all()
        self.assertEqual(len(warehouse_stock_items), imported_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_price_rules(self, mock_load_rows):
        """
        Import Price Rules from Pronto datagrid.
        """
        fake_price_rules_datagrid_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_price_rules_datagrid_rows(imported_items_count)
        mock_load_rows.return_value = rows
        import_price_rules(fake_price_rules_datagrid_filepath, self.session)
        mock_load_rows.assert_called_with(fake_price_rules_datagrid_filepath)
        # pylint:disable=no-member
        price_rules = self.session.query(PriceRule).all()
        self.assertEqual(len(price_rules), imported_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_price_regions(self, mock_load_rows):
        """
        Import Price Regions from Pronto datagrid.
        """
        fake_inv_items_datagrid_filepath = random_string(20)
        fake_pr_items_datagrid_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_inventory_items_datagrid_rows(imported_items_count)
        mock_load_rows.return_value = rows
        import_inventory_items(
            fake_inv_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_inv_items_datagrid_filepath)
        item_codes = [row["item_code"] for row in rows]
        rows = [fake_price_region_items_datagrid_row({
            "item_code": item_code,
        }) for item_code in item_codes]
        mock_load_rows.return_value = rows
        import_price_region_items(
            fake_pr_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_pr_items_datagrid_filepath)
        self.assertEqual(mock_load_rows.call_count, 2)
        # pylint:disable=no-member
        price_region_items = self.session.query(PriceRegionItem).all()
        self.assertEqual(len(price_region_items), imported_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_supplier_items(self, mock_load_rows):
        """
        Import Supplier Items from Pronto datagrid.
        """
        fake_inv_items_datagrid_filepath = random_string(20)
        fake_supp_items_datagrid_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_inventory_items_datagrid_rows(imported_items_count)
        mock_load_rows.return_value = rows
        import_inventory_items(
            fake_inv_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_inv_items_datagrid_filepath)
        item_codes = [row["item_code"] for row in rows]
        rows = [fake_supplier_items_datagrid_row({
            "item_code": item_code,
        }) for item_code in item_codes]
        mock_load_rows.return_value = rows
        import_supplier_items(
            fake_supp_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_supp_items_datagrid_filepath)
        self.assertEqual(mock_load_rows.call_count, 2)
        # pylint:disable=no-member
        supplier_items = self.session.query(SupplierItem).all()
        self.assertEqual(len(supplier_items), imported_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_gtin_items(self, mock_load_rows):
        """
        Import GTIN Items from Pronto datagrid.
        """
        fake_inv_items_datagrid_filepath = random_string(20)
        fake_gtin_items_datagrid_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_inventory_items_datagrid_rows(imported_items_count)
        mock_load_rows.return_value = rows
        import_inventory_items(
            fake_inv_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_inv_items_datagrid_filepath)
        item_codes = [row["item_code"] for row in rows]
        rows = [fake_gtin_items_datagrid_row({
            "item_code": item_code,
        }) for item_code in item_codes]
        mock_load_rows.return_value = rows
        import_gtin_items(
            fake_gtin_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_gtin_items_datagrid_filepath)
        self.assertEqual(mock_load_rows.call_count, 2)
        # pylint:disable=no-member
        gtin_items = self.session.query(GTINItem).all()
        self.assertEqual(len(gtin_items), imported_items_count)

    @patch("pxi.importers.load_spl_rows")
    def test_import_supplier_pricelist_items(self, mock_load_rows):
        """
        Import Supplier Pricelist Items from CSV.
        """
        fake_supplier_pricelist_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_supplier_pricelist_rows(10)
        mock_load_rows.return_value = rows
        supplier_pricelist_items = import_supplier_pricelist_items(
            fake_supplier_pricelist_filepath)
        mock_load_rows.assert_called_with(fake_supplier_pricelist_filepath)
        self.assertEqual(len(supplier_pricelist_items), imported_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_web_sortcodes(self, mock_load_rows):
        """
        Import web sortcodes from metadata spreadsheet.
        """
        fake_web_sortcodes_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_web_sortcodes_rows(10)
        mock_load_rows.return_value = rows
        import_web_sortcodes(
            fake_web_sortcodes_filepath,
            self.session)
        mock_load_rows.assert_called_with(
            fake_web_sortcodes_filepath,
            "sortcodes")
        # pylint:disable=no-member
        web_sortcodes = self.session.query(WebSortcode).all()
        self.assertEqual(len(web_sortcodes), imported_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_inventory_web_data_items(self, mock_load_rows):
        """
        Import Inventory Web Data Items from Pronto datagrids.
        """
        fake_inv_items_datagrid_filepath = random_string(20)
        fake_web_sortcodes_filepath = random_string(20)
        fake_web_data_items_datagrid_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_web_sortcodes_rows(10)
        mock_load_rows.return_value = rows
        import_web_sortcodes(
            fake_web_sortcodes_filepath,
            self.session)
        mock_load_rows.assert_called_with(
            fake_web_sortcodes_filepath,
            "sortcodes")
        menu_names = [
            f"{row['parent_name']}/{row['child_name']}" for row in rows]
        rows = fake_inventory_items_datagrid_rows(imported_items_count)
        mock_load_rows.return_value = rows
        import_inventory_items(
            fake_inv_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_inv_items_datagrid_filepath)
        item_codes = [row["item_code"] for row in rows]
        rows = [fake_web_data_items_datagrid_row({
            "stock_code": item_codes[i],
            "menu_name": menu_names[i],
        }) for i in range(imported_items_count)]
        mock_load_rows.return_value = rows
        import_inventory_web_data_items(
            fake_web_data_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(
            fake_web_data_items_datagrid_filepath)
        self.assertEqual(mock_load_rows.call_count, 3)
        # pylint:disable=no-member
        inventory_web_data_items = self.session.query(
            InventoryWebDataItem).all()
        self.assertEqual(len(inventory_web_data_items), imported_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_web_sortcode_mappings(self, mock_load_rows):
        """
        Import web sortcodes from metadata spreadsheet.
        """
        fake_web_sortcodes_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_web_sortcodes_rows(10)
        mock_load_rows.return_value = rows
        import_web_sortcodes(
            fake_web_sortcodes_filepath,
            self.session)
        mock_load_rows.assert_called_with(
            fake_web_sortcodes_filepath,
            "sortcodes")
        menu_names = [
            f"{row['parent_name']}/{row['child_name']}" for row in rows]
        rows = [fake_web_sortcodes_mappings_row({
            "menu_name": menu_name
        }) for menu_name in menu_names]
        mock_load_rows.return_value = rows
        web_sortcode_mappings = import_web_sortcode_mappings(
            fake_web_sortcodes_filepath,
            self.session)
        mock_load_rows.assert_called_with(
            fake_web_sortcodes_filepath,
            "rules")
        self.assertEqual(mock_load_rows.call_count, 2)
        # pylint:disable=no-member
        web_sortcodes = self.session.query(WebSortcode).all()
        self.assertEqual(len(web_sortcodes), imported_items_count)
        self.assertEqual(len(web_sortcode_mappings), imported_items_count)

    @patch("pxi.importers.load_rows")
    def test_import_website_images_report(self, mock_load_rows):
        """
        Import product image information from report.
        """
        fake_inv_items_datagrid_filepath = random_string(20)
        fake_website_images_report_filepath = random_string(20)
        imported_items_count = 10
        rows = fake_inventory_items_datagrid_rows(imported_items_count)
        mock_load_rows.return_value = rows
        import_inventory_items(
            fake_inv_items_datagrid_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_inv_items_datagrid_filepath)
        item_codes = [row["item_code"] for row in rows]
        rows = [fake_website_images_report_row({
            "productcode": item_code,
        }) for item_code in item_codes]
        mock_load_rows.return_value = rows
        images_data = import_website_images_report(
            fake_website_images_report_filepath,
            self.session)
        mock_load_rows.assert_called_with(fake_website_images_report_filepath)
        # pylint:disable=no-member
        self.assertEqual(len(images_data), imported_items_count)
