
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pxi.enum import ItemType
from pxi.exporters import (
    export_contract_item_task,
    export_price_changes_report,
    export_pricelist,
    export_product_price_task,
    export_tickets_list
)
from pxi.importers import (
    import_contract_items,
    import_inventory_items,
    import_price_region_items,
    import_price_rules,
    import_warehouse_stock_items
)
from pxi.models import (
    Base,
    InventoryItem,
    PriceRegionItem,
    PriceRule
)
from pxi.price_calc import (
    recalculate_contract_prices,
    recalculate_sell_prices
)


def db_session():
    db = create_engine('sqlite://')
    Base.metadata.create_all(db)
    session = sessionmaker(bind=db)()
    return session


class operations:
        
    @staticmethod
    def price_calc(
        inventory_items_datagrid="data/import/inventory_items.xlsx",
        price_rules_datagrid="data/import/price_rules.xlsx",
        pricelist_datagrid="data/import/pricelist.xlsx",
        contract_items_datagrid="data/import/contract_items.xlsx",
        price_changes_report="data/export/price_changes_report.xlsx",
        pricelist="data/export/pricelist.csv",
        product_price_task="data/export/product_price_task.txt",
        contract_item_task="data/export/contract_item_task.txt",
        tickets_list="data/export/tickets_list.txt"
    ):
        session = db_session()
        print("Importing inventory items...")
        import_inventory_items(inventory_items_datagrid, session)
        print("Importing warehouse stock items...")
        import_warehouse_stock_items(inventory_items_datagrid, session)
        print("Importing price rules...")
        import_price_rules(price_rules_datagrid, session)
        print("Importing price region items...")
        import_price_region_items(pricelist_datagrid, session)
        print("Importing contract items...")
        import_contract_items(contract_items_datagrid, session)

        price_region_items = session.query(PriceRegionItem).join(
            PriceRegionItem.inventory_item
        ).join(
            PriceRegionItem.price_rule
        ).filter(
            PriceRegionItem.price_rule_id.isnot(None),
            ~PriceRule.code.in_([
                "", "MR", "MRAL", "MRCP", "MRKI", "NA", "OU"
            ]),
            InventoryItem.item_type != ItemType.CROSS_REFERENCE,
            InventoryItem.item_type != ItemType.LABOUR,
            InventoryItem.item_type != ItemType.INDENT_ITEM
        ).all()
        
        print("Recalculating sell prices...")
        price_changes = recalculate_sell_prices(price_region_items, session)
        updated_price_region_items = [
            price_change.price_region_item for price_change in price_changes
        ]
        print("Recalculating contract prices...")
        updated_contract_items = recalculate_contract_prices(
            price_changes, session)

        def updated_default_price_regions():
            for price_change in price_changes:
                price_region_item = price_change.price_region_item
                if price_region_item.code == "":
                    yield price_region_item

        def warehouse_stock_items_needing_tickets():
            for price_region_item in updated_default_price_regions():
                inventory_item = price_region_item.inventory_item
                warehouse_stock_items = inventory_item.warehouse_stock_items
                for warehouse_stock_item in warehouse_stock_items:
                    if warehouse_stock_item.on_hand > 0:
                        yield warehouse_stock_item
                    elif warehouse_stock_item.minimum > 0:
                        yield warehouse_stock_item
                    elif warehouse_stock_item.bin_location:
                        yield warehouse_stock_item

        print("Exporting price changes report...")
        export_price_changes_report(price_changes_report, price_changes)
        print("Exporting pricelist...")
        export_pricelist(pricelist, updated_price_region_items)
        print("Exporting product price task...")
        export_product_price_task(product_price_task, updated_price_region_items)
        print("Exporting contract item task...")
        export_contract_item_task(contract_item_task, updated_contract_items)
        print("Exporting tickets list...")
        export_tickets_list(tickets_list, warehouse_stock_items_needing_tickets())
        print("Done.")
