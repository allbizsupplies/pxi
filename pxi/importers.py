import csv
from datetime import datetime
from hashlib import md5
import logging
import os
import time

from pxi.datagrid import load_rows
from pxi.enum import (
    ItemType,
    ItemCondition,
    PriceBasis,
    TaxCode,
    WebStatus)
from pxi.models import (
    ContractItem,
    File,
    InventoryItem,
    InventoryWebDataItem,
    GTINItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem,
    WebSortcode)
from pxi.spl_update import SPL_FIELDNAMES


def import_contract_items(filepath, db_session):
    insert_count = 0
    update_count = 0
    for row in load_rows(filepath):
        item_code = row["item_code"]
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == item_code
        ).scalar()
        if inventory_item:
            contract_code = row["contract_no"]
            attributes = {
                "inventory_item": inventory_item,
                "code": contract_code,
                "price_1": row["price_1"],
                "price_2": row["price_2"],
                "price_3": row["price_3"],
                "price_4": row["price_4"],
                "price_5": row["price_5"],
                "price_6": row["price_6"],
            }
            contract_item = db_session.query(ContractItem).filter(
                ContractItem.code == contract_code,
                ContractItem.inventory_item == inventory_item
            ).scalar()
            if contract_item:
                update(contract_item, attributes)
                update_count += 1
            else:
                db_session.add(ContractItem(**attributes))
                insert_count += 1
    db_session.commit()
    logging.info(
        f"Import ContractItem: {insert_count} inserted, {update_count} updated")


def import_inventory_items(filepath, db_session):
    insert_count = 0
    update_count = 0
    for row in load_rows(filepath):
        item_code = row["item_code"]
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == item_code
        ).scalar()
        attributes = {
            "code": row["item_code"],
            "description_line_1": row["item_description"],
            "description_line_2": row["description_2"],
            "description_line_3": row["description_3"],
            "uom": row["unit"],
            "brand": row["brand_manuf"],
            "apn": row["manuf_apn_no"],
            "group": row["group"],
            "created": row["creation_date"],
            "item_type": ItemType(row["status"]),
            "condition": ItemCondition(row["condition"]),
            "replacement_cost": row["replacement_cost"],
        }
        if inventory_item:
            update(inventory_item, attributes)
            update_count += 1
        else:
            db_session.add(InventoryItem(**attributes))
            insert_count += 1
    db_session.commit()
    logging.info(
        f"Import InventoryItem: {insert_count} inserted, {update_count} updated")


def import_inventory_web_data_items(filepath, db_session):
    insert_count = 0
    for row in load_rows(filepath):
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["stock_code"]
        ).scalar()
        web_sortcode = None
        if row["menu_name"] is not None:
            parent_name, child_name = row["menu_name"].split("/")
            web_sortcode = db_session.query(WebSortcode).filter(
                WebSortcode.parent_name == parent_name,
                WebSortcode.child_name == child_name
            ).scalar()
        if inventory_item:
            inventory_web_data_item = InventoryWebDataItem(
                description=row["description"],
                inventory_item=inventory_item,
                web_sortcode=web_sortcode
            )
            db_session.add(inventory_web_data_item)
            insert_count += 1
    db_session.commit()
    logging.info(
        f"Import InventoryWebDataItem: {insert_count} inserted.")


def import_price_region_items(filepath, db_session):
    insert_count = 0
    update_count = 0
    for row in load_rows(filepath):
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["item_code"]
        ).scalar()
        if inventory_item:
            price_region_code = row["region"] if row["region"] else ""
            price_rule = None
            if row["rule"]:
                price_rule = db_session.query(PriceRule).filter(
                    PriceRule.code == row["rule"]
                ).scalar()
            attributes = {
                "inventory_item": inventory_item,
                "price_rule": price_rule,
                "code": price_region_code,
                "tax_code": TaxCode.TAXABLE if row["tax_rate"] else TaxCode.EXEMPT,
                "quantity_1": row["pr_1_corpa_qty"],
                "quantity_2": row["pr_2_corp_b_qty"],
                "quantity_3": row["pr_3_corp_c_qty"],
                "quantity_4": row["pr_4_bulk_qty"],
                "price_0": row["w_sale_price"],
                "price_1": row["pr_1_corpa"],
                "price_2": row["pr_2_corp_b"],
                "price_3": row["pr_3_corp_c"],
                "price_4": row["pr_4_bulk"],
                "rrp_excl_tax": row["retail_price"],
                "rrp_incl_tax": row["rrp_inc_tax"]
            }
            price_region_item = db_session.query(PriceRegionItem).filter(
                PriceRegionItem.inventory_item == inventory_item,
                PriceRegionItem.code == price_region_code
            ).scalar()
            if price_region_item:
                update(price_region_item, attributes)
                update_count += 1
            else:
                db_session.add(PriceRegionItem(**attributes))
                insert_count += 1
    db_session.commit()
    logging.info(
        f"Import PriceRegionItem: {insert_count} inserted, {update_count} updated")


def import_price_rules(filepath, db_session):
    insert_count = 0
    update_count = 0
    for row in load_rows(filepath):
        rule_code = row["rule"]
        price_rule = db_session.query(PriceRule).filter(
            PriceRule.code == rule_code
        ).scalar()
        attributes = {
            "code": rule_code,
            "description": row["comments"],
            "price_0_basis": PriceBasis(row["price0_based_on"]),
            "price_1_basis": PriceBasis(row["price1_based_on"]),
            "price_2_basis": PriceBasis(row["price2_based_on"]),
            "price_3_basis": PriceBasis(row["price3_based_on"]),
            "price_4_basis": PriceBasis(row["price4_based_on"]),
            "rrp_excl_basis": PriceBasis(row["rec_retail_based_on"]),
            "rrp_incl_basis": PriceBasis(row["rrp_inc_tax_based_on"]),
            "price_0_factor": row["price0_factor"],
            "price_1_factor": row["price1_factor"],
            "price_2_factor": row["price2_factor"],
            "price_3_factor": row["price3_factor"],
            "price_4_factor": row["price4_factor"],
            "rrp_excl_factor": row["rec_retail_factor"],
            "rrp_incl_factor": row["rrp_inc_tax_factor"]
        }
        if price_rule:
            update(price_rule, attributes)
            update_count += 1
        else:
            price_rule = PriceRule(**attributes)
            db_session.add(price_rule)
        insert_count += 1
    db_session.commit()
    logging.info(
        f"Import PriceRule: {insert_count} inserted, {update_count} updated")


def import_warehouse_stock_items(filepath, db_session):
    insert_count = 0
    update_count = 0
    for row in load_rows(filepath):
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["item_code"]
        ).scalar()
        if inventory_item:
            warehouse_stock_item = db_session.query(WarehouseStockItem).filter(
                WarehouseStockItem.inventory_item == inventory_item,
                WarehouseStockItem.code == row["whse"]
            ).scalar()
            attributes = {
                "inventory_item": inventory_item,
                "code": row["whse"],
                "minimum": row["minimum_stock"],
                "maximum": row["maximum_stock"],
                "on_hand": row["on_hand"],
                "bin_location": row["bin_loc"],
                "bulk_location": row["bulk_loc"],
            }
            if warehouse_stock_item:
                update(warehouse_stock_item, attributes)
                update_count += 1
            else:
                warehouse_stock_item = WarehouseStockItem(**attributes)
                db_session.add(warehouse_stock_item)
                insert_count += 1
    db_session.commit()
    logging.info(
        f"Import WarehouseStockItem: {insert_count} inserted, {update_count} updated")


def import_supplier_items(filepath, db_session):
    insert_count = 0
    update_count = 0
    for row in load_rows(filepath):
        if not row["supplier_item"]:
            continue
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["item_code"]
        ).scalar()
        supplier_code = row["supplier"]
        if inventory_item:
            attributes = {
                "inventory_item": inventory_item,
                "code": supplier_code,
                "item_code": row["supplier_item"],
                "priority": row["priority"],
                "uom": row["unit"],
                "conv_factor": row["conv_factor"],
                "pack_quantity": row["pack_qty"],
                "moq": row["eoq"],
                "buy_price": row["current_buy_price"],
            }
            supplier_item = db_session.query(SupplierItem).filter(
                SupplierItem.code == supplier_code,
                SupplierItem.inventory_item == inventory_item
            ).scalar()
            if supplier_item:
                update(supplier_item, attributes)
                update_count += 1
            else:
                db_session.add(SupplierItem(**attributes))
                insert_count += 1
    db_session.commit()
    logging.info(
        f"Import SupplierItem: {insert_count} inserted, {update_count} updated")


def import_gtin_items(filepath, db_session):
    insert_count = 0
    update_count = 0
    gtin_item_uids = []
    for row in load_rows(filepath):
        gtin_code = row["gtin"]
        if not gtin_code:
            continue
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["item_code"]
        ).scalar()
        if inventory_item:
            # Ignore duplicate rows.
            uid = f"{inventory_item.code}--{row['gtin']}"
            if uid not in gtin_item_uids:
                gtin_item_uids.append(uid)
                gtin_item = db_session.query(GTINItem).filter(
                    GTINItem.inventory_item == inventory_item,
                    GTINItem.code == gtin_code
                ).scalar()
                attributes = {
                    "inventory_item": inventory_item,
                    "code": row["gtin"],
                    "uom": row["uom"],
                    "conv_factor": row["conversion"]
                }
                if gtin_item:
                    update(gtin_item, attributes)
                    update_count += 1
                else:
                    db_session.add(GTINItem(**attributes))
                    insert_count += 1
    db_session.commit()
    logging.info(
        f"Import GTINItem: {insert_count} inserted, {update_count} updated")


def load_spl_rows(filepath):
    with open(filepath, "r", encoding="iso8859-14") as file:
        return csv.DictReader(file, SPL_FIELDNAMES)


def import_supplier_pricelist_items(filepath):
    overridden_supplier_items_count = 0
    invalid_record_count = 0
    supplier_pricelist_items = {}
    # Collect supplier pricelist items. If an item has the same item code
    # and supplier code as a previous item then it will override it.
    for row in load_spl_rows(filepath):
        item_code = row["item_code"]
        supplier_code = row["supplier_code"]
        uom = row["supp_uom"]
        if uom == "":
            invalid_record_count += 1
            continue
        if item_code not in supplier_pricelist_items.keys():
            supplier_pricelist_items[item_code] = {}
        if supplier_code in supplier_pricelist_items[item_code].keys():
            overridden_supplier_items_count += 1
        supplier_pricelist_items[item_code][supplier_code] = row

    # Flatten the list of items.
    supplier_pricelist_items_flattened = []
    for rows in supplier_pricelist_items.values():
        for row in rows.values():
            supplier_pricelist_items_flattened.append(row)

    logging.info(
        f"Import SPL records: "
        f"{len(supplier_pricelist_items_flattened)} inserted, "
        f"{invalid_record_count} skipped, "
        f"{overridden_supplier_items_count} overridden.")
    return supplier_pricelist_items_flattened


def import_web_sortcodes(filepath, db_session, worksheet_name="sortcodes"):
    count = 0
    for row in load_rows(filepath, worksheet_name):
        web_sortcode = WebSortcode(
            parent_name=row["parent_name"].strip(),
            child_name=row["child_name"].strip(),
        )
        db_session.add(web_sortcode)
        count += 1

    logging.info(
        f"Import WebSortcode: "
        f"{count} inserted.")


def import_web_sortcode_mappings(filepath, db_session, worksheet_name="rules"):
    web_sortcode_mappings = {}
    for row in load_rows(filepath, worksheet_name):
        rule_code = row["rule_code"]
        menu_name = row["menu_name"]
        if menu_name and menu_name != "man":
            parent_name, child_name = menu_name.split("/")
            web_sortcode = db_session.query(WebSortcode).filter(
                WebSortcode.parent_name == parent_name,
                WebSortcode.child_name == child_name,
            ).scalar()
            web_sortcode_mappings[rule_code] = web_sortcode
        else:
            web_sortcode_mappings[rule_code] = menu_name

    logging.info(
        f"Import web sortcode mappings: "
        f"{len(web_sortcode_mappings)} inserted.")
    return web_sortcode_mappings


def import_website_images_report(filepath, db_session):
    def get_image(row):
        for i in range(1, 5):
            filename = row[f"picture{i}"]
            if filename:
                return filename

    images_data = []
    for row in load_rows(filepath):
        item_code = str(row["productcode"])
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == item_code
        ).scalar()
        if not inventory_item:
            continue
        images_data.append({
            "inventory_item": inventory_item,
            "filename": get_image(row)
        })

    logging.info(
        f"Import website image data: "
        f"{len(images_data)} inserted.")
    return images_data


# import functions and files for each model.
# Each item in the list is a tuplc containing the following values:
# - The model class.
# - The import function.
# - The name of the import file in the config.
MODEL_IMPORTS = [
    (
        InventoryItem,
        import_inventory_items,
        "inventory_items_datagrid"
    ),
    (
        WarehouseStockItem,
        import_warehouse_stock_items,
        "inventory_items_datagrid"
    ),
    (
        PriceRule,
        import_price_rules,
        "price_rules_datagrid"
    ),
    (
        PriceRegionItem,
        import_price_region_items,
        "pricelist_datagrid"
    ),
    (
        ContractItem,
        import_contract_items,
        "contract_items_datagrid"
    ),
]


def update(record, attributes):
    for key, value in attributes.items():
        setattr(record, key, value)


def import_data(db_session, paths, models=None, force_imports=False):
    import_all_models = models is None

    def file_has_changed(path):
        file = db_session.query(File).filter(
            File.path == path
        ).scalar()
        modified = datetime.fromtimestamp(os.path.getmtime(path))
        if file is None:
            file = File(
                path=path,
                modified=modified)
            db_session.add(file)
        if file.modified < modified:
            file.modified = modified
            return True

    for model, function, path_key in MODEL_IMPORTS:
        path = paths[path_key]
        if import_all_models or model in models:
            if force_imports or file_has_changed(path):
                function(path, db_session)
