from decimal import Decimal
from progressbar import progressbar
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pxi.enum import ItemCondition, ItemType, WebStatus
from pxi.exporters import (
    export_downloaded_images_report,
    export_contract_item_task,
    export_price_changes_report,
    export_pricelist,
    export_product_price_task,
    export_product_web_sortcode_task,
    export_supplier_price_changes_report,
    export_supplier_pricelist,
    export_tickets_list
)
from pxi.fetchers import get_fetchers
from pxi.image_resizer import resize_image
from pxi.importers import (
    import_contract_items,
    import_inventory_items,
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
    InventoryItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem
)
from pxi.price_calc import (
    recalculate_contract_prices,
    recalculate_sell_prices
)
from pxi.spl_update import update_supplier_items
from pxi.web_sort import add_web_sortcodes


IGNORED_PRICE_RULES = [
    "", "MR", "MRAL", "MRCP", "MRKI", "NA", "OU", "RRP", "SH"
]


def db_session():
    db = create_engine('sqlite://')
    Base.metadata.create_all(db)
    session = sessionmaker(bind=db)()
    return session


class operations:

    @staticmethod
    def fetch_images(
        inventory_items_datagrid="data/import/inventory_items.xlsx",
        supplier_items_datagrid="data/import/supplier_items.xlsx",
        website_images_report="data/import/website_images_report.xlsx",
        downloaded_images_report="data/export/downloaded_images_report.xlsx",
        images_dir="data/export/images"
    ):
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
        inventory_items_datagrid="data/import/inventory_items.xlsx",
        supplier_items_datagrid="data/import/supplier_items.xlsx",
        supplier_pricelist="data/import/supplier_pricelist.csv",
        supplier_price_changes_report="data/export/supplier_price_changes_report.xlsx",
        updated_supplier_pricelist="data/export/supplier_pricelist.csv"
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
    def web_sort(
        inventory_items_datagrid="data/import/inventory_items.xlsx",
        price_rules_datagrid="data/import/price_rules.xlsx",
        pricelist_datagrid="data/import/pricelist.xlsx",
        inventory_metadata="data/import/inventory_metadata.xlsx",
        product_web_sortcode_task="data/export/product_web_sortcode_task.txt"
    ):
        session = db_session()
        import_inventory_items(inventory_items_datagrid, session)
        import_price_rules(price_rules_datagrid, session)
        import_price_region_items(pricelist_datagrid, session)
        import_web_sortcodes(inventory_metadata, session)
        web_sortcode_mappings = import_web_sortcode_mappings(
            inventory_metadata)

        # pylint:disable=no-member
        price_region_items = session.query(PriceRegionItem).join(
            PriceRegionItem.inventory_item
        ).join(
            PriceRegionItem.price_rule
        ).filter(
            PriceRegionItem.price_rule_id.isnot(None),
            PriceRegionItem.code == "",
            InventoryItem.condition != ItemCondition.DISCONTINUED,
            InventoryItem.condition != ItemCondition.INACTIVE,
            InventoryItem.item_type != ItemType.CROSS_REFERENCE,
            InventoryItem.item_type != ItemType.LABOUR,
            InventoryItem.item_type != ItemType.INDENT_ITEM,
            InventoryItem.web_status == WebStatus.ACTIVE,
            InventoryItem.web_sortcode == None
        ).all()

        print("{} inventory items selected for web sorting.".format(
            len(price_region_items)
        ))

        print("Sorting inventory items...")
        updated_inventory_items = add_web_sortcodes(
            price_region_items, web_sortcode_mappings, session)

        print("{} inventory items have been updated with a web sortcode.".format(
            len(updated_inventory_items)
        ))

        print("Exporting product web sortcode task...")
        export_product_web_sortcode_task(
            product_web_sortcode_task, updated_inventory_items)
        print("Done.")
