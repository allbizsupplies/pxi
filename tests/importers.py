
from datetime import datetime
from random import randint, choice as random_choice, seed
import string
import time
from unittest.mock import MagicMock, patch

from pxi.enum import ItemType, ItemCondition, PriceBasis
from pxi.importers import (
    import_contract_items,
    import_data,
    import_inventory_items,
    import_inventory_web_data_items,
    import_gtin_items,
    import_price_region_items,
    import_price_rules,
    import_supplier_items,
    import_supplier_pricelist_items,
    import_warehouse_stock_items,
    import_web_menu_items,
    import_web_menu_item_mappings,
    import_website_images_report)
from pxi.models import (
    ContractItem,
    InventoryItem,
    InventoryWebDataItem,
    GTINItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem,
    WebMenuItem)
from tests import DatabaseTestCase
from tests.fakes import (
    fake_contract_item,
    fake_gtin_item,
    fake_inv_web_data_item,
    fake_inventory_item,
    fake_price_region_item,
    fake_price_rule,
    fake_supplier_item,
    fake_warehouse_stock_item,
    fake_web_menu_item,
    random_datetime,
    random_item_code,
    random_price_factor,
    random_price_string,
    random_quantity,
    random_string)


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


def fake_inv_web_data_items_datagrid_row(values={}):
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


def fake_web_menu_items_row(values={}):
    return {
        "parent_name": values.get("parent_name", random_string(10)),
        "child_name": values.get("child_name", random_string(10))
    }


def fake_web_menu_items_mappings_row(values={}):
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
        "supp_conv_factor": values.get("supp_conv_factor", 1),
        "supp_eoq": values.get("supp_eoq", 1),
        "supp_sell_uom": values.get("supp_sell_uom", random_string(4)),
    }


def fake_website_images_report_row(values={}):
    return {
        "productcode": values.get("productcode", random_item_code()),
        "picture1": values.get("picture1", random_string(20)),
        "picture2": values.get("picture2"),
        "picture3": values.get("picture3"),
        "picture4": values.get("picture4"),
    }


def mock_model_imports():
    return [
        (
            InventoryItem,
            MagicMock(),
            "inventory_items_datagrid"
        ),
        (
            WarehouseStockItem,
            MagicMock(),
            "inventory_items_datagrid"
        ),
        (
            PriceRule,
            MagicMock(),
            "price_rules_datagrid"
        ),
        (
            PriceRegionItem,
            MagicMock(),
            "pricelist_datagrid"
        ),
        (
            ContractItem,
            MagicMock(),
            "contract_items_datagrid"
        ),
        (
            SupplierItem,
            MagicMock(),
            "supplier_items_datagrid"
        ),
        (
            InventoryWebDataItem,
            MagicMock(),
            "inventory_web_data_items_datagrid"
        ),
        (
            WebMenuItem,
            MagicMock(),
            "web_menu"
        ),
    ]


def mock_import_paths():
    return {
        "contract_items_datagrid": "path/import/contract_items.xlsx",
        "inventory_items_datagrid": "path/import/inventory_items.xlsx",
        "gtin_items_datagrid": "path/import/gtin_items.xlsx",
        "price_rules_datagrid": "path/import/price_rules.xlsx",
        "pricelist_datagrid": "path/import/pricelist.xlsx",
        "supplier_items_datagrid": "path/import/supplier_items.xlsx",
        "inventory_web_data_items_datagrid": "path/import/inventory_web_data_items.xlsx",
        "web_menu": "path/import/web_menu.xlsx",
    }


class ImporterTests(DatabaseTestCase):

    @patch("pxi.importers.file_has_changed")
    def test_import_data_for_all_models(self, mock_file_has_changed):
        """
        Imports data for all models.
        """
        import_paths = mock_import_paths()
        mock_file_has_changed.return_value = True

        model_imports = mock_model_imports()
        with patch("pxi.importers.MODEL_IMPORTS", model_imports):
            import_data(self.db_session, import_paths)

        # Importer checks file has changed before each import.
        self.assertEqual(mock_file_has_changed.call_count, len(import_paths))
        for _, import_function, import_path_key in model_imports:
            import_path = import_paths[import_path_key]
            import_function.assert_called_once_with(
                import_path, self.db_session)

    def test_force_import_data_for_all_models(self):
        """
        Imports all models without checking that files have changed.
        """
        import_paths = mock_import_paths()

        model_imports = mock_model_imports()
        with patch("pxi.importers.MODEL_IMPORTS", model_imports):
            import_data(self.db_session, import_paths, force_imports=True)

        for _, import_function, import_path_key in model_imports:
            import_path = import_paths[import_path_key]
            import_function.assert_called_once_with(
                import_path, self.db_session)

    @patch("pxi.importers.file_has_changed")
    def test_import_data_for_single_model(self, mock_file_has_changed):
        """
        Imports data for all models.
        """
        import_paths = mock_import_paths()
        mock_file_has_changed.return_value = True

        model_imports = mock_model_imports()
        with patch("pxi.importers.MODEL_IMPORTS", model_imports):
            import_data(self.db_session, import_paths, [
                InventoryItem
            ])

        # Importer checks file has changed before each import.
        model, import_function, import_path_key = model_imports[0]
        self.assertEqual(model, InventoryItem)
        import_path = import_paths[import_path_key]
        mock_file_has_changed.assert_called_once_with(
            import_path, self.db_session)
        import_function.assert_called_once_with(import_path, self.db_session)

    @patch("pxi.importers.load_rows")
    def test_import_inventory_items(self, mock_load_rows):
        """
        Imports InventoryItems from Pronto datagrid.
        """

        # Seed the database with two InventoryItems and then mock an import
        # for another two, but where the first imported row has the same item
        # code as the first seeded item.
        filepath = random_string(20)
        seeded_inv_items = [
            fake_inventory_item(),
            fake_inventory_item(),
        ]
        self.seed(seeded_inv_items)
        rows = [
            fake_inventory_items_datagrid_row({
                "item_code": seeded_inv_items[0].code
            }),
            fake_inventory_items_datagrid_row(),
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        import_inventory_items(filepath, self.db_session)

        # Expect to insert 2 items, update 1, leaving a total of 3
        # InventoryItems in the database.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        inventory_items = self.db_session.query(InventoryItem).all()
        self.assertEqual(len(inventory_items), 3)

    @patch("pxi.importers.load_rows")
    def test_import_contract_items(self, mock_load_rows):
        """
        Import ContractItems from Pronto datagrid.
        """

        # Seed the database with two InventoryItems and two ContractItems, then
        # mock an import for another three ContractItems, but where the first
        # imported row has the same item code and contract code as the first
        # seeded ContractItem, and the last imported row doesn't have a
        # matching InventoryItem.
        filepath = random_string(20)
        seeded_inv_items = [
            fake_inventory_item(),
            fake_inventory_item(),
        ]
        seeded_con_items = [
            fake_contract_item(seeded_inv_items[0]),
            fake_contract_item(seeded_inv_items[1]),
        ]
        self.seed(seeded_inv_items + seeded_con_items)
        rows = [
            fake_contract_items_datagrid_row({
                "item_code": seeded_inv_items[0].code,
                "contract_no": seeded_con_items[0].code,
            }),
            fake_contract_items_datagrid_row({
                "item_code": seeded_inv_items[1].code,
            }),
            fake_contract_items_datagrid_row()
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        import_contract_items(filepath, self.db_session)

        # Expect to insert 2 items, update 1, leaving a total of 3
        # ContractItems in the database.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        contract_items = self.db_session.query(ContractItem).all()
        self.assertEqual(len(contract_items), 3)

    @patch("pxi.importers.load_rows")
    def test_import_warehouse_stock_items(self, mock_load_rows):
        """
        Import WarehouseStockItems from Pronto datagrid.
        """

        # Seed the database with two InventoryItems and two WarehouseStockItems,
        # then mock an import for another two WarehouseStockItems, but where the
        # first imported row has the same item code and warehouse code as the
        # first seeded WarehouseStockItem, and the last imported row doesn't
        # have a matching InventoryItem.
        filepath = random_string(20)
        seeded_inv_items = [
            fake_inventory_item(),
            fake_inventory_item(),
        ]
        seeded_whse_stock_items = [
            fake_warehouse_stock_item(seeded_inv_items[0]),
            fake_warehouse_stock_item(seeded_inv_items[1]),
        ]
        self.seed(seeded_inv_items + seeded_whse_stock_items)
        rows = [
            fake_inventory_items_datagrid_row({
                "item_code": seeded_inv_items[0].code,
                "whse": seeded_whse_stock_items[0].code,
            }),
            fake_inventory_items_datagrid_row({
                "item_code": seeded_inv_items[1].code,
            }),
            fake_inventory_items_datagrid_row(),
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        import_warehouse_stock_items(filepath, self.db_session)

        # Expect to insert 2 items, update 1, leaving a total of 3
        # WarehouseStockItems in the database.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        whse_stock_items = self.db_session.query(WarehouseStockItem).all()
        self.assertEqual(len(whse_stock_items), 3)

    @patch("pxi.importers.load_rows")
    def test_import_price_rules(self, mock_load_rows):
        """
        Import PriceRules from Pronto datagrid.
        """

        # Seed the database with two PriceRules and then mock an import
        # for another two, but where the first imported row has the same rule
        # code as the first seeded item.
        filepath = random_string(20)
        seeded_price_rules = [
            fake_price_rule(),
            fake_price_rule(),
        ]
        self.seed(seeded_price_rules)
        rows = [
            fake_price_rules_datagrid_row({
                "rule": seeded_price_rules[0].code
            }),
            fake_price_rules_datagrid_row(),
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        import_price_rules(filepath, self.db_session)

        # Expect to insert 2 items, update 1, leaving a total of 3 PriceRules
        # in the database.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        price_rules = self.db_session.query(PriceRule).all()
        self.assertEqual(len(price_rules), 3)

    @patch("pxi.importers.load_rows")
    def test_import_price_region_items(self, mock_load_rows):
        """
        Import PriceRegionItems from Pronto datagrid.
        """

        # Seed the database with two InventoryItems, two PriceRules and two
        # PriceRegionItems, then mock an import for another two
        # PriceRegionItems, but where the first imported row has the same
        # item code, price rule and price region code as the first seeded
        # PriceRegionItem, and the last row doesn't have a matching
        # InventoryItem.
        filepath = random_string(20)
        seeded_inv_items = [
            fake_inventory_item(),
            fake_inventory_item(),
        ]
        seeded_price_rules = [
            fake_price_rule(),
            fake_price_rule(),
        ]
        seeded_price_region_items = [
            fake_price_region_item(seeded_inv_items[0], seeded_price_rules[0]),
            fake_price_region_item(seeded_inv_items[1], seeded_price_rules[1]),
        ]
        self.seed(
            seeded_inv_items + seeded_price_rules + seeded_price_region_items)
        rows = [
            fake_price_region_items_datagrid_row({
                "item_code": seeded_inv_items[0].code,
                "rule": seeded_price_rules[0].code,
                "region": seeded_price_region_items[0].code,
            }),
            fake_price_region_items_datagrid_row({
                "item_code": seeded_inv_items[1].code,
                "rule": seeded_price_rules[1].code,
            }),
            fake_price_region_items_datagrid_row(),
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        import_price_region_items(filepath, self.db_session)

        # Expect to insert 2 items, update 1, leaving a total of 3
        # PriceRegionItems in the database.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        price_region_items = self.db_session.query(PriceRegionItem).all()
        self.assertEqual(len(price_region_items), 3)

    @patch("pxi.importers.load_rows")
    def test_import_supplier_items(self, mock_load_rows):
        """
        Import SupplierItems from Pronto datagrid.
        """

        # Seed the database with two InventoryItems and two SupplierItems,
        # then mock an import for another two SupplierItems, but where the
        # first imported row has the same item code and supplier code as the
        # first seeded SupplierItem, and the last row doesn't have a matching
        # InventoryItem.
        filepath = random_string(20)
        seeded_inv_items = [
            fake_inventory_item(),
            fake_inventory_item(),
        ]
        seeded_supp_items = [
            fake_supplier_item(seeded_inv_items[0]),
            fake_supplier_item(seeded_inv_items[1]),
        ]
        self.seed(seeded_inv_items + seeded_supp_items)
        rows = [
            fake_supplier_items_datagrid_row({
                "item_code": seeded_inv_items[0].code,
                "supplier": seeded_supp_items[0].code,
            }),
            fake_supplier_items_datagrid_row({
                "item_code": seeded_inv_items[1].code,
            }),
            fake_supplier_items_datagrid_row()
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        import_supplier_items(filepath, self.db_session)

        # Expect to insert 2 items, update 1, leaving a total of 3
        # SupplierItems in the database.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        supplier_items = self.db_session.query(SupplierItem).all()
        self.assertEqual(len(supplier_items), 3)

    @patch("pxi.importers.load_rows")
    def test_import_gtin_items(self, mock_load_rows):
        """
        Import GTINItems from Pronto datagrid.
        """

        # Seed the database with two InventoryItems and two GTINItems, then
        # mock an import for another two GTINItems, but where the first
        # imported row has the same item code, GTIN and UOM as the first
        # seeded GTINItem, and the last row doesn't have a matching
        # InventoryItem.
        filepath = random_string(20)
        seeded_inv_items = [
            fake_inventory_item(),
            fake_inventory_item(),
        ]
        seeded_gtin_items = [
            fake_gtin_item(seeded_inv_items[0]),
            fake_gtin_item(seeded_inv_items[1]),
        ]
        self.seed(seeded_inv_items + seeded_gtin_items)
        rows = [
            fake_gtin_items_datagrid_row({
                "item_code": seeded_inv_items[0].code,
                "gtin": seeded_gtin_items[0].code,
                "uom": seeded_gtin_items[0].uom,
            }),
            fake_gtin_items_datagrid_row({
                "item_code": seeded_inv_items[1].code,
            }),
            fake_gtin_items_datagrid_row(),
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        import_gtin_items(filepath, self.db_session)

        # Expect to insert 2 items, update 1, leaving a total of 3 GTINItems
        # in the database.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        gtin_items = self.db_session.query(GTINItem).all()
        self.assertEqual(len(gtin_items), 3)

    @patch("pxi.importers.load_spl_rows")
    def test_import_supplier_pricelist_items(self, mock_load_spl_rows):
        """
        Import Supplier Pricelist Items from CSV.
        """

        # Mock an import for four SPL items, but make the first and third items
        # share the same item code and supplier code, and make the first and
        # last items share the same item code but not the same supplier code.
        filepath = random_string(20)
        fake_item_code = random_item_code()
        fake_supp_code = random_string(3)
        rows = [
            fake_supplier_pricelist_row({
                "item_code": fake_item_code,
                "supplier_code": fake_supp_code,
            }),
            fake_supplier_pricelist_row(),
            fake_supplier_pricelist_row({
                "item_code": fake_item_code,
                "supplier_code": fake_supp_code,
            }),
            fake_supplier_pricelist_row({
                "item_code": fake_item_code,
            }),
        ]
        mock_load_spl_rows.return_value = rows

        # Run the import.
        spl_items = import_supplier_pricelist_items(filepath)

        # Expect to return only three out of the four items.
        mock_load_spl_rows.assert_called_with(filepath)
        self.assertEqual(len(spl_items), 3)

    @patch("pxi.importers.load_rows")
    def test_import_web_menu_items(self, mock_load_rows):
        """
        Import WebMenuItems from metadata spreadsheet.
        """

        # Seed the database with two WebMenuItems and then mock an import
        # for another two, but where the first imported row has the same menu
        # name as first seeded menu item.
        filepath = random_string(20)
        seeded_web_menu_items = [
            fake_web_menu_item(),
            fake_web_menu_item(),
        ]
        self.seed(seeded_web_menu_items)
        rows = [
            fake_web_menu_items_row({
                "parent_name": seeded_web_menu_items[0].parent_name,
                "child_name": seeded_web_menu_items[0].child_name,
            }),
            fake_web_menu_items_row(),
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        import_web_menu_items(filepath, self.db_session)

        # Expect to insert 2 items, update 1, leaving a total of 3
        # WebMenuItems in the database.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        web_menu_items = self.db_session.query(WebMenuItem).all()
        self.assertEqual(len(web_menu_items), 3)

    @patch("pxi.importers.load_rows")
    def test_import_inventory_web_data_items(self, mock_load_rows):
        """
        Import InventoryWebDataItems from Pronto datagrids.
        """

        # Seed the database with three InventoryItems, three WebMenuItems and
        # two InventoryWebDataItems, then mock an import for another two
        # InventoryWebDataItems, but where the first imported row has the same
        # item code, as the first seeded InventoryWebDataItem, and the last
        # row doesn't have a matching InventoryItem.
        filepath = random_string(20)
        seeded_inv_items = [
            fake_inventory_item(),
            fake_inventory_item(),
            fake_inventory_item(),
        ]
        seeded_web_menu_items = [
            fake_web_menu_item(),
            fake_web_menu_item(),
            fake_web_menu_item(),
        ]
        seeded_inv_web_data_items = [
            fake_inv_web_data_item(
                seeded_inv_items[0],
                seeded_web_menu_items[0]),
            fake_inv_web_data_item(
                seeded_inv_items[1],
                seeded_web_menu_items[1]),
        ]
        self.seed(
            seeded_inv_items + seeded_web_menu_items + seeded_inv_web_data_items)
        rows = [
            fake_inv_web_data_items_datagrid_row({
                "stock_code": seeded_inv_items[0].code,
                "menu_name": seeded_web_menu_items[0].name,
            }),
            fake_inv_web_data_items_datagrid_row({
                "stock_code": seeded_inv_items[2].code,
                "menu_name": seeded_web_menu_items[2].name,
            }),
            fake_inv_web_data_items_datagrid_row(),
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        import_inventory_web_data_items(filepath, self.db_session)

        # Expect to insert 2 items, update 1, leaving a total of 3
        # InventoryWebDataItems in the database.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        inv_web_data_items = self.db_session.query(
            InventoryWebDataItem).all()
        self.assertEqual(len(inv_web_data_items), 3)

    @patch("pxi.importers.load_rows")
    def test_import_web_menu_item_mappings(self, mock_load_rows):
        """
        Import WebMenuItem mappings from metadata spreadsheet.
        """

        # Seed the database with one WebMenuItem, and mock an import for two
        # WebMenuItem mapping, but where the second row doesn't have a
        # matching WebMenuItem.
        filepath = random_string(20)
        seeded_web_menu_items = [
            fake_web_menu_item(),
        ]
        self.seed(seeded_web_menu_items)
        rows = [
            fake_web_menu_items_mappings_row({
                "menu_name": seeded_web_menu_items[0].name
            }),
            fake_web_menu_items_mappings_row(),
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        web_menu_item_mappings = import_web_menu_item_mappings(
            filepath,
            self.db_session)

        # Expect to import both WebMenuItem mappings.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        web_menu_items = self.db_session.query(WebMenuItem).all()
        self.assertEqual(len(web_menu_item_mappings), 2)

    @patch("pxi.importers.load_rows")
    def test_import_website_images_report(self, mock_load_rows):
        """
        Import product image information from report.
        """

        # Seed the database with one InventoryItem, and mock an import of two
        # image data record, where the second row doesn't have a matching
        # InventoryItem.
        filepath = random_string(20)
        image_filename = random_string(20)
        inv_item = fake_inventory_item()
        self.seed([inv_item])
        rows = [
            fake_website_images_report_row({
                "productcode": inv_item.code,
                "picture1": image_filename,
            }),
        ]
        mock_load_rows.return_value = rows

        # Run the import.
        images_data = import_website_images_report(
            filepath, self.db_session)

        # Expect to import one image data record.
        mock_load_rows.assert_called_with(filepath)
        # pylint:disable=no-member
        self.assertEqual(len(images_data), 1)
        self.assertEqual(images_data[0], (inv_item, image_filename))
