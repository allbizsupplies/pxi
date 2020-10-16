
from pxi.importers import (
    import_contract_items,
    import_images_report,
    import_inventory_items,
    import_gtin_items,
    import_price_region_items,
    import_price_rules,
    import_supplier_items,
    import_supplier_pricelist_items,
    import_warehouse_stock_items,
    import_web_sortcodes,
    import_web_sortcode_mappings
)
from pxi.models import (
    ContractItem,
    InventoryItem,
    GTINItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem,
    WebSortcode)
from tests import DatabaseTestCase


class ImporterTests(DatabaseTestCase):

    def test_import_contract_items(self):
        """Import Contract Items from Pronto datagrid."""
        expected_item_count = 10
        import_inventory_items(
            "tests/fixtures/inventory_items.xlsx", self.session)
        import_contract_items(
            "tests/fixtures/contract_items.xlsx", self.session)
        # pylint:disable=no-member
        contract_items = self.session.query(ContractItem).all()
        self.assertEqual(len(contract_items), expected_item_count)

    def test_import_inventory_items(self):
        """Import Inventory Items from Pronto datagrid."""
        expected_item_count = 10
        import_inventory_items(
            "tests/fixtures/inventory_items.xlsx", self.session)
        # pylint:disable=no-member
        inventory_items = self.session.query(InventoryItem).all()
        self.assertEqual(len(inventory_items), expected_item_count)

    def test_import_warehouse_stock_items(self):
        """Import Warehouse Stock Items from Pronto datagrid."""
        expected_item_count = 10
        datagrid_filepath = "tests/fixtures/inventory_items.xlsx"
        import_inventory_items(datagrid_filepath, self.session)
        import_warehouse_stock_items(datagrid_filepath, self.session)
        # pylint:disable=no-member
        warehouse_stock_items = self.session.query(WarehouseStockItem).all()
        self.assertEqual(len(warehouse_stock_items), expected_item_count)

    def test_import_price_rules(self):
        """Import Price Rules from Pronto datagrid."""
        expected_item_count = 10
        import_price_rules("tests/fixtures/price_rules.xlsx", self.session)
        # pylint:disable=no-member
        price_rules = self.session.query(PriceRule).all()
        self.assertEqual(len(price_rules), expected_item_count)

    def test_import_price_regions(self):
        """Import Price Regions from Pronto datagrid."""
        expected_item_count = 10
        import_inventory_items(
            "tests/fixtures/inventory_items.xlsx", self.session)
        import_price_rules("tests/fixtures/price_rules.xlsx", self.session)
        import_price_region_items(
            "tests/fixtures/pricelist.xlsx", self.session)
        # pylint:disable=no-member
        price_region_items = self.session.query(PriceRegionItem).all()
        self.assertEqual(len(price_region_items), expected_item_count)

    def test_import_supplier_items(self):
        """Import Supplier Items from Pronto datagrid."""
        expected_item_count = 10
        datagrid_filepath = "tests/fixtures/supplier_items.xlsx"
        import_inventory_items(
            "tests/fixtures/inventory_items.xlsx", self.session)
        import_supplier_items(datagrid_filepath, self.session)
        # pylint:disable=no-member
        supplier_items = self.session.query(SupplierItem).all()
        self.assertEqual(len(supplier_items), expected_item_count)

    def test_import_supplier_pricelist_items(self):
        """Import Supplier Pricelist Items from CSV."""
        expected_item_count = 10
        supplier_pricelist_items = import_supplier_pricelist_items(
            "tests/fixtures/supplier_pricelist.csv")
        self.assertEqual(len(supplier_pricelist_items), expected_item_count)

    def test_import_gtin_items(self):
        """Import GTIN Items from Pronto datagrid."""
        expected_item_count = 10
        datagrid_filepath = "tests/fixtures/gtin_items.xlsx"
        import_inventory_items(
            "tests/fixtures/inventory_items.xlsx", self.session)
        import_gtin_items(datagrid_filepath, self.session)
        # pylint:disable=no-member
        gtin_items = self.session.query(GTINItem).all()
        self.assertEqual(len(gtin_items), expected_item_count)

    def test_import_web_sortcodes(self):
        """Import web sortcodes from metadata spreadsheet."""
        expected_item_count = 99
        import_web_sortcodes(
            "tests/fixtures/inventory_metadata.xlsx",
            self.session
        )
        # pylint:disable=no-member
        web_sortcodes = self.session.query(WebSortcode).all()
        self.assertEqual(len(web_sortcodes), expected_item_count)

    def test_import_web_sortcode_mappings(self):
        """Import web sortcodes from metadata spreadsheet."""
        expected_item_count = 10
        web_sortcode_mappings = import_web_sortcode_mappings(
            "tests/fixtures/inventory_metadata.xlsx",
        )
        # pylint:disable=no-member
        self.assertEqual(len(web_sortcode_mappings), expected_item_count)

    def test_import_images_report(self):
        """Import product image information from report."""
        expected_item_count = 6
        images_data = import_images_report(
            "tests/fixtures/images_report.xlsx",
        )
        # pylint:disable=no-member
        self.assertEqual(len(images_data), expected_item_count)
