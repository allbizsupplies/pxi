from decimal import Decimal
from progressbar import progressbar
from sqlalchemy import create_engine, not_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pxi.enum import ItemCondition, ItemType, WebStatus
from pxi.exporters import (
    export_downloaded_images_report,
    export_contract_item_task,
    export_gtin_report,
    export_price_changes_report,
    export_pricelist,
    export_product_price_task,
    export_supplier_price_changes_report,
    export_supplier_pricelist,
    export_tickets_list,
    export_web_data_updates_report,
    export_web_product_menu_data
)
from pxi.fetchers import get_fetchers
from pxi.image_resizer import resize_image
from pxi.importers import (
    import_contract_items,
    import_gtin_items,
    import_inventory_items, import_inventory_web_data_items,
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
    Base,
    GTINItem,
    InventoryItem, InventoryWebDataItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem,
    WebSortcode
)
from pxi.price_calc import (
    recalculate_contract_prices,
    recalculate_sell_prices
)
from pxi.spl_update import update_supplier_items
from pxi.web_update import update_product_menu


IGNORED_PRICE_RULES = [
    "", "MR", "MRAL", "MRCP", "MRKI", "NA", "OU", "RRP", "SH"
]

BRANDS_WITHOUT_GTIN = [
    "ALL", "ELA", "EUR", "FNX", "LAL", "WES", "YSD"
]


def db_session():
    db = create_engine('sqlite://')
    Base.metadata.create_all(db)
    session = sessionmaker(bind=db)()
    return session


class operations:

    @staticmethod
    def fetch_images(
            inventory_items_datagrid,
            supplier_items_datagrid,
            website_images_report,
            downloaded_images_report,
            images_dir):
        session = db_session()
        import_inventory_items(inventory_items_datagrid, session)
        import_supplier_items(supplier_items_datagrid, session)
        website_images = import_website_images_report(
            website_images_report, session)

        inventory_items = []
        for website_image in website_images:
            if website_image["filename"] is None:
                inventory_items.append(website_image["inventory_item"])

        print("Selected {} items missing website image.".format(
            len(inventory_items)))

        def download_image(fetchers, inventory_item):
            for fetcher in fetchers:
                image_filepath = fetcher.download_image(
                    inventory_item, images_dir)
                if image_filepath:
                    return {
                        "inventory_item": inventory_item,
                        "source": fetcher.__class__.__name__,
                        "filename": image_filepath
                    }

        def fetch_image(inventory_item):
            fetchers = get_fetchers(inventory_item)
            if len(fetchers) > 0:
                image_data = download_image(fetchers, inventory_item)
                if image_data:
                    return image_data

        print("Fetching images...")
        downloaded_images = []
        missing_images = []
        for inventory_item in progressbar(inventory_items):
            image = fetch_image(inventory_item)
            if image:
                downloaded_images.append(image)
            else:
                missing_images.append(inventory_item)
        print("{} images have been downloaded.".format(len(downloaded_images)))
        print("{} inventory items are missing images.".format(len(missing_images)))

        print("Processing images...")
        for image in progressbar(downloaded_images):
            resize_image(image["filename"], 1000, 1000)

        print("Exporting downloaded images report...")
        export_downloaded_images_report(
            downloaded_images_report, downloaded_images, missing_images)
        print("Done.")

    @staticmethod
    def generate_spl(
        inventory_items_datagrid,
        supplier_items_datagrid,
        supplier_pricelist,
        supplier_price_changes_report,
        updated_supplier_pricelist
    ):
        session = db_session()
        import_inventory_items(inventory_items_datagrid, session)
        import_supplier_items(supplier_items_datagrid, session)
        supplier_pricelist_items = import_supplier_pricelist_items(
            supplier_pricelist)

        print("Updating supplier prices...")
        supplier_price_changes, uom_errors = update_supplier_items(
            supplier_pricelist_items, session)
        updated_supplier_items = [
            price_change["supplier_item"] for price_change in supplier_price_changes
        ]
        print("{} supplier items have been updated.".format(
            len(updated_supplier_items)
        ))
        if len(uom_errors) > 0:
            print("{} supplier items have UOM errors.".format(
                len(uom_errors)
            ))

        print("Exporting supplier price changes report...")
        export_supplier_price_changes_report(
            supplier_price_changes_report, supplier_price_changes, uom_errors)
        print("Exporting supplier pricelist...")
        export_supplier_pricelist(
            updated_supplier_pricelist, updated_supplier_items)
        print("Done.")

    @staticmethod
    def price_calc(
        inventory_items_datagrid,
        price_rules_datagrid,
        pricelist_datagrid,
        contract_items_datagrid,
        price_changes_report,
        pricelist,
        product_price_task,
        contract_item_task,
        tickets_list
    ):
        session = db_session()
        import_inventory_items(inventory_items_datagrid, session)
        import_warehouse_stock_items(inventory_items_datagrid, session)
        import_price_rules(price_rules_datagrid, session)
        import_price_region_items(pricelist_datagrid, session)
        import_contract_items(contract_items_datagrid, session)

        # pylint:disable=no-member
        price_region_items = session.query(PriceRegionItem).join(
            PriceRegionItem.inventory_item
        ).join(
            PriceRegionItem.price_rule
        ).filter(
            PriceRegionItem.price_rule_id.isnot(None),
            ~PriceRule.code.in_(IGNORED_PRICE_RULES),
            InventoryItem.condition != ItemCondition.DISCONTINUED,
            InventoryItem.condition != ItemCondition.INACTIVE,
            InventoryItem.item_type != ItemType.CROSS_REFERENCE,
            InventoryItem.item_type != ItemType.LABOUR,
            InventoryItem.item_type != ItemType.INDENT_ITEM
        ).all()

        print("{} price region items selected for price calculation.".format(
            len(price_region_items)
        ))

        print("Recalculating sell prices...")
        price_changes = recalculate_sell_prices(price_region_items, session)
        updated_price_region_items = [
            price_change.price_region_item for price_change in price_changes
        ]
        print("{} price region items have been updated.".format(
            len(updated_price_region_items)
        ))
        print("Recalculating contract prices...")
        updated_contract_items = recalculate_contract_prices(
            price_changes, session)
        print("{} contract items have been updated.".format(
            len(updated_contract_items)
        ))

        def updated_default_price_regions():
            for price_change in price_changes:
                price_region_item = price_change.price_region_item
                # Ignore items without a price rule.
                if price_region_item.code != "":
                    continue
                # Ignore items that have an unchanged level 0 price.
                if price_change.price_diffs[0] < Decimal("0.005"):
                    continue
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
                        if warehouse_stock_item.bin_location not in ["OWNUSE"]:
                            yield warehouse_stock_item

        print("Exporting price changes report...")
        export_price_changes_report(price_changes_report, price_changes)
        print("Exporting pricelist...")
        export_pricelist(pricelist, updated_price_region_items)
        print("Exporting product price task...")
        export_product_price_task(
            product_price_task, updated_price_region_items)
        print("Exporting contract item task...")
        export_contract_item_task(contract_item_task, updated_contract_items)
        print("Exporting tickets list...")
        export_tickets_list(
            tickets_list, warehouse_stock_items_needing_tickets())
        print("Done.")

    @staticmethod
    def web_update(
        inventory_items_datagrid,
        inventory_web_data_items_datagrid,
        price_rules_datagrid,
        pricelist_datagrid,
        inventory_metadata,
        web_product_menu_data,
        web_data_updates_report
    ):
        session = db_session()
        import_inventory_items(inventory_items_datagrid, session)
        import_price_rules(price_rules_datagrid, session)
        import_price_region_items(pricelist_datagrid, session)
        import_web_sortcodes(inventory_metadata, session)
        import_inventory_web_data_items(
            inventory_web_data_items_datagrid, session)
        web_sortcode_mappings = import_web_sortcode_mappings(
            inventory_metadata,
            session)

        # pylint:disable=no-member
        inventory_items = session.query(InventoryItem).join(
            InventoryItem.inventory_web_data_item
        ).join(
            InventoryItem.price_region_items
        ).filter(
            PriceRegionItem.price_rule_id.isnot(None),
            PriceRegionItem.code == "",
            InventoryWebDataItem.web_sortcode == None,
            InventoryItem.condition != ItemCondition.DISCONTINUED,
            InventoryItem.condition != ItemCondition.INACTIVE,
            InventoryItem.item_type != ItemType.CROSS_REFERENCE,
            InventoryItem.item_type != ItemType.LABOUR,
            InventoryItem.item_type != ItemType.INDENT_ITEM,
        ).all()
        print("{} inventory items selected for web sorting.".format(
            len(inventory_items)
        ))

        print("Updating web menu for inventory items...")
        updated_inventory_items = update_product_menu(
            inventory_items, web_sortcode_mappings, session)

        print("{} inventory items have been updated with a web sortcode.".format(
            len(updated_inventory_items)
        ))

        print("Exporting product web sortcode task...")
        export_web_product_menu_data(
            web_product_menu_data, updated_inventory_items)
        print("Exporting product web sortcode report...")
        export_web_data_updates_report(
            web_data_updates_report,
            updated_inventory_items)
        print("Done.")

    @staticmethod
    def missing_gtin(
        inventory_items_datagrid,
        gtin_items_datagrid,
        gtin_report
    ):
        session = db_session()
        import_inventory_items(inventory_items_datagrid, session)
        import_warehouse_stock_items(inventory_items_datagrid, session)
        import_gtin_items(gtin_items_datagrid, session)

        print("Selecting inventory items without unit GTIN...")
        # pylint:disable=no-member
        inventory_items = session.query(InventoryItem).join(
            InventoryItem.gtin_items
        ).filter(
            ~InventoryItem.brand.in_(BRANDS_WITHOUT_GTIN),
            InventoryItem.condition != ItemCondition.DISCONTINUED,
            InventoryItem.condition != ItemCondition.INACTIVE,
            InventoryItem.item_type != ItemType.CROSS_REFERENCE,
            InventoryItem.item_type != ItemType.LABOUR,
            InventoryItem.item_type != ItemType.INDENT_ITEM,
        ).all()

        def missing_gtin(inventory_item):
            for gtin_item in inventory_item.gtin_items:
                if gtin_item.is_unit_barcode:
                    return False
            return True

        inventory_items_missing_gtin = []
        for inventory_item in progressbar(inventory_items):
            if missing_gtin(inventory_item):
                inventory_items_missing_gtin.append(inventory_item)

        print("{} inventory items have been selected.".format(
            len(inventory_items_missing_gtin)
        ))

        print("Selecting inventory items with stock on hand...")
        inventory_items_on_hand = []
        for inventory_item in progressbar(inventory_items_missing_gtin):
            for warehouse_stock_item in inventory_item.warehouse_stock_items:
                if warehouse_stock_item.on_hand > 0:
                    inventory_items_on_hand.append(inventory_item)
                    continue

        print("{} of these inventory items are on hand.".format(
            len(inventory_items_on_hand)
        ))

        print("Exporting missing GTIN report...")
        export_gtin_report(
            gtin_report, inventory_items_missing_gtin, inventory_items_on_hand)
        print("Done.")
