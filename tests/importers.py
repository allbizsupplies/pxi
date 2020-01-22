
from pxi.importers import (
    import_contract_items,
    import_inventory_items,
    import_price_region_items,
    import_price_rules,
    import_warehouse_stock_items
)
from pxi.models import (
    ContractItem,
    InventoryItem,
    PriceRegionItem,
    PriceRule,
    WarehouseStockItem)
from tests import DatabaseTestCase

class ImporterTests(DatabaseTestCase):

    def test_import_contract_items(self):
        """Import Contract Items from Pronto datagrid."""
        expected_item_count = 10
        import_inventory_items("tests/fixtures/inventory_items.xlsx", self.session)
        import_contract_items("tests/fixtures/contract_items.xlsx", self.session)
        contract_items = self.session.query(ContractItem).all()
        self.assertEqual(len(contract_items), expected_item_count)

    def test_import_inventory_items(self):
        """Import Inventory Items from Pronto datagrid."""
        expected_item_count = 10
        import_inventory_items("tests/fixtures/inventory_items.xlsx", self.session)
        inventory_items = self.session.query(InventoryItem).all()
        self.assertEqual(len(inventory_items), expected_item_count)

    def test_import_warehouse_stock_items(self):
        """Import Warehouse Stock Items from Pronto datagrid."""
        expected_item_count = 10
        datagrid_filepath = "tests/fixtures/inventory_items.xlsx"
        import_inventory_items(datagrid_filepath, self.session)
        import_warehouse_stock_items(datagrid_filepath, self.session)
        warehouse_stock_items = self.session.query(WarehouseStockItem).all()
        self.assertEqual(len(warehouse_stock_items), expected_item_count)

    def test_import_price_rules(self):
        """Import Price Rules from Pronto datagrid."""
        expected_item_count = 10
        import_price_rules("tests/fixtures/price_rules.xlsx", self.session)
        price_rules = self.session.query(PriceRule).all()
        self.assertEqual(len(price_rules), expected_item_count)

    def test_import_price_regions(self):
        """Import Price Regions from Pronto datagrid."""
        expected_item_count = 10
        import_inventory_items("tests/fixtures/inventory_items.xlsx", self.session)
        import_price_rules("tests/fixtures/price_rules.xlsx", self.session)
        import_price_region_items("tests/fixtures/pricelist.xlsx", self.session)
        price_region_items = self.session.query(PriceRegionItem).all()
        self.assertEqual(len(price_region_items), expected_item_count)
