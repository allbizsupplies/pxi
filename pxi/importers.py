import csv
from datetime import datetime
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


def get_inventory_items(db_session):
    """
    Builds a hashmap of all InventoryItems in the database, keyed by code.
    """
    return {inv_item.code: inv_item
            for inv_item in db_session.query(InventoryItem).all()}


def upserter(db_session, model, records):
    """
    Creates an upsert function for a given model and records.

    Params:
        db_session: The SQLAlchemy database session.
        model: The SQLAlchemy model.
        records: A dict containing all records.

    Returns:
        The upsert function.
    """
    def upsert(key, attributes):
        """
        Updates or inserts a record depending on whether or not it exists.

        Params:
            key: The key identifying the record.
            attributes: The record attributes required to update or add 
                the record.
        Returns:
            A boolean flag indicating whether the record was updated.
        """
        if key in records:
            record = records[key]
            for key, value in attributes.items():
                setattr(record, key, value)
            return True
        record = model(**attributes)
        db_session.add(record)
        records[key] = record
        return False

    return upsert


def import_contract_items(filepath, db_session):
    """
    Imports ContractItems from a datagrid into the database.

    Params:
        filepath: The path to the contract items datagrid.
        db_session: The database session.
    """
    inserted_count = 0  # The number of new records inserted.
    updated_count = 0   # The number of existing records updated.
    skipped_count = 0   # The number of rows skipped.

    # Get a hashmap of InventoryItems keyed by code.
    inv_items = get_inventory_items(db_session)

    # Create an upserter for ContractItem.
    upsert = upserter(db_session, ContractItem, {
        f"{con_item.code}--{con_item.inventory_item.code}": con_item
        for con_item in db_session.query(ContractItem).all()})

    # Update/insert rows as ContractItems where InventoryItem exists.
    for row in load_rows(filepath):
        inv_item_code = row["item_code"]
        if inv_item_code in inv_items:
            con_code = row["contract_no"]
            con_item_key = f"{con_code}--{inv_item_code}"
            updated = upsert(con_item_key, {
                "inventory_item": inv_items[inv_item_code],
                "code": con_code,
                "price_1": row["price_1"],
                "price_2": row["price_2"],
                "price_3": row["price_3"],
                "price_4": row["price_4"],
                "price_5": row["price_5"],
                "price_6": row["price_6"],
            })
            if updated:
                updated_count += 1
            else:
                inserted_count += 1
        else:
            skipped_count += 1

    # Commit the database queries and log the results.
    db_session.commit()
    logging.info(
        f"Import ContractItems: "
        f"{inserted_count} inserted, "
        f"{updated_count} updated, "
        f"{skipped_count} skipped.")


def import_inventory_items(filepath, db_session):
    """
    Imports InventoryItems from a datagrid into the database.

    Params:
        filepath: The path to the inventory items datagrid.
        db_session: The database session.
    """
    inserted_count = 0  # The number of new records inserted.
    updated_count = 0   # The number of existing records updated.

    # Create an upserter for InventoryItem.
    upsert = upserter(db_session, InventoryItem,
                      get_inventory_items(db_session))

    # Update/insert rows as InventoryItems.
    for row in load_rows(filepath):
        inv_item_code = row["item_code"]
        updated = upsert(inv_item_code, {
            "code": inv_item_code,
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
        })
        if updated:
            updated_count += 1
        else:
            inserted_count += 1

    # Commit the database queries and log the results.
    db_session.commit()
    logging.info(
        f"Import InventoryItems: "
        f"{inserted_count} inserted, "
        f"{updated_count} updated.")


def import_inventory_web_data_items(filepath, db_session):
    """
    Imports InventoryWebDataItems from a datagrid into the database.

    Params:
        filepath: The path to the inventory web data items datagrid.
        db_session: The database session.
    """
    inserted_count = 0  # The number of new records inserted.
    updated_count = 0   # The number of existing records updated.
    skipped_count = 0   # The number of rows skipped.

    # Get a hashmap of InventoryItems keyed by code.
    inv_items = get_inventory_items(db_session)

    # Get a hashmap of WebSortcodes keyed by name.
    web_sortcodes = {
        web_sortcode.name: web_sortcode
        for web_sortcode in db_session.query(WebSortcode).all()}

    # Create an upserter for InventoryWebDataItems.
    upsert = upserter(db_session, InventoryWebDataItem, {
        iwd_item.inventory_item.code: iwd_item
        for iwd_item in db_session.query(InventoryWebDataItem).all()})

    # Update/insert rows as InventoryWebDataItems where InventoryItem exists.
    for row in load_rows(filepath):
        inv_item_code = row["stock_code"]
        web_sortcode_name = row["menu_name"]
        has_valid_web_sortcode = web_sortcode_name is None \
            or web_sortcode_name in web_sortcodes
        if inv_item_code in inv_items and has_valid_web_sortcode:
            web_sortcode = None
            if web_sortcode_name:
                web_sortcode = web_sortcodes[web_sortcode_name]
            updated = upsert(inv_item_code, {
                "inventory_item": inv_items[inv_item_code],
                "web_sortcode": web_sortcode,
                "description": row["description"],
            })
            if updated:
                updated_count += 1
            else:
                inserted_count += 1
        else:
            skipped_count += 1

    # Commit the database queries and log the results.
    db_session.commit()
    logging.info(
        f"Import InventoryWebDataItems: "
        f"{inserted_count} inserted, "
        f"{updated_count} updated, "
        f"{skipped_count} skipped.")


def import_price_region_items(filepath, db_session):
    """
    Imports PriceRegionItems from a datagrid into the database.

    Params:
        filepath: The path to the price region items datagrid.
        db_session: The database session.
    """
    inserted_count = 0  # The number of new records inserted.
    updated_count = 0   # The number of existing records updated.
    skipped_count = 0   # The number of rows skipped.

    # Get a hashmap of InventoryItems keyed by code.
    inv_items = get_inventory_items(db_session)

    # Build a hashmap of PriceRules keyed by code.
    price_rules = {
        price_rule.code: price_rule
        for price_rule in db_session.query(PriceRule).all()}

    # Create an upserter for PriceRegionItem.
    upsert = upserter(db_session, PriceRegionItem, {
        f"{pr_item.code}--{pr_item.inventory_item.code}": pr_item
        for pr_item in db_session.query(PriceRegionItem).all()})

    # Update/insert rows as PriceRegionItems where InventoryItem exists.
    for row in load_rows(filepath):
        inv_item_code = row["item_code"]
        price_rule_code = row["rule"]
        has_valid_price_rule = price_rule_code is None \
            or price_rule_code in price_rules
        if inv_item_code in inv_items and has_valid_price_rule:
            price_region_code = row["region"] if row["region"] else ""
            price_rule = None
            if price_rule_code:
                price_rule = price_rules[price_rule_code]
            pr_item_key = f"{price_region_code}--{inv_item_code}"
            updated = upsert(pr_item_key, {
                "inventory_item": inv_items[inv_item_code],
                "price_rule": price_rule,
                "code": price_region_code,
                "tax_code": TaxCode.TAXABLE
                if row["tax_rate"] else TaxCode.EXEMPT,
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
            })
            if updated:
                updated_count += 1
            else:
                inserted_count += 1
        else:
            skipped_count += 1

    # Commit the database queries and log the results.
    db_session.commit()
    logging.info(
        f"Import PriceRegionItems: "
        f"{inserted_count} inserted, "
        f"{updated_count} updated, "
        f"{skipped_count} skipped.")


def import_price_rules(filepath, db_session):
    """
    Imports PriceRules from a datagrid into the database.

    Params:
        filepath: The path to the price rules datagrid.
        db_session: The database session.
    """
    inserted_count = 0  # The number of new records inserted.
    updated_count = 0   # The number of existing records updated.

    upsert = upserter(db_session, PriceRule, {
        price_rule.code: price_rule
        for price_rule in db_session.query(PriceRule).all()})

    # Update/insert rows as PriceRules.
    for row in load_rows(filepath):
        price_rule_code = row["rule"]
        updated = upsert(price_rule_code, {
            "code": price_rule_code,
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
        })
        if updated:
            updated_count += 1
        else:
            inserted_count += 1

    # Commit the database queries and log the results.
    db_session.commit()
    logging.info(
        f"Import PriceRules: "
        f"{inserted_count} inserted, "
        f"{updated_count} updated.")


def import_warehouse_stock_items(filepath, db_session):
    """
    Imports WarehouseStockItems from a datagrid into the database.

    Params:
        filepath: The path to the inventory items datagrid.
        db_session: The database session.
    """
    inserted_count = 0  # The number of new records inserted.
    updated_count = 0   # The number of existing records updated.
    skipped_count = 0   # The number of rows skipped.

    # Get a hashmap of InventoryItems keyed by code.
    inv_items = get_inventory_items(db_session)

    # Create upserter for WarehouseStockItem.
    upsert = upserter(db_session, WarehouseStockItem, {
        f"{ws_item.code}--{ws_item.inventory_item.code}": ws_item
        for ws_item in db_session.query(WarehouseStockItem).all()})

    # Update/insert rows as WarehouseStockItems where InventoryItem exists.
    for row in load_rows(filepath):
        inv_item_code = row["item_code"]
        whse_code = row["whse"]
        if inv_item_code in inv_items:
            ws_item_key = f"{whse_code}--{inv_item_code}"
            updated = upsert(ws_item_key, {
                "inventory_item": inv_items[inv_item_code],
                "code": row["whse"],
                "minimum": row["minimum_stock"],
                "maximum": row["maximum_stock"],
                "on_hand": row["on_hand"],
                "bin_location": row["bin_loc"],
                "bulk_location": row["bulk_loc"],
            })
            if updated:
                updated_count += 1
            else:
                inserted_count += 1
        else:
            skipped_count += 1

    # Commit the database queries and log the results.
    db_session.commit()
    logging.info(
        f"Import WarehouseStockItems: "
        f"{inserted_count} inserted, "
        f"{updated_count} updated, "
        f"{skipped_count} skipped.")


def import_supplier_items(filepath, db_session):
    """
    Imports SupplierItems from a datagrid into the database.

    Params:
        filepath: The path to the supplier items datagrid.
        db_session: The database session.
    """
    inserted_count = 0  # The number of new records inserted.
    updated_count = 0   # The number of existing records updated.
    skipped_count = 0   # The number of rows skipped.

    # Get a hashmap of InventoryItems keyed by code.
    inv_items = get_inventory_items(db_session)

    # Create upserter for SupplierItem.
    upsert = upserter(db_session, WarehouseStockItem, {
        f"{supp_item.code}--{supp_item.inventory_item.code}": supp_item
        for supp_item in db_session.query(SupplierItem).all()})

    # Update/insert rows as SupplierItems where InventoryItem exists.
    for row in load_rows(filepath):
        inv_item_code = row["item_code"]
        supplier_code = row["supplier"]
        if inv_item_code in inv_items and supplier_code:
            key = f"{supplier_code}--{inv_item_code}"
            updated = upsert(key, {
                "inventory_item": inv_items[inv_item_code],
                "code": supplier_code,
                "item_code": row["supplier_item"],
                "priority": row["priority"],
                "uom": row["unit"],
                "conv_factor": row["conv_factor"],
                "pack_quantity": row["pack_qty"],
                "moq": row["eoq"],
                "buy_price": row["current_buy_price"],
            })
            if updated:
                updated_count += 1
            else:
                inserted_count += 1
        else:
            skipped_count += 1

    # Commit the database queries and log the results.
    db_session.commit()
    logging.info(
        f"Import SupplierItems: "
        f"{inserted_count} inserted, "
        f"{updated_count} updated, "
        f"{skipped_count} skipped.")


def import_gtin_items(filepath, db_session):
    """
    Imports GTINItems from a datagrid into the database.

    Params:
        filepath: The path to the gtin items datagrid.
        db_session: The database session.
    """
    inserted_count = 0  # The number of new records inserted.
    updated_count = 0   # The number of existing records updated.
    skipped_count = 0   # The number of rows skipped.

    # Get a hashmap of InventoryItems keyed by code.
    inv_items = get_inventory_items(db_session)

    # Create an upserter for GTINItem.
    upsert = upserter(db_session, GTINItem, {
        f"{gtin_item.code}--{gtin_item.inventory_item.code}": gtin_item
        for gtin_item in db_session.query(GTINItem).all()})

    # Update/insert rows as GTINItems where InventoryItem exists, and skip
    # duplicate rows.
    seen_keys = []  # List of keys already seen in datagrid.
    for row in load_rows(filepath):
        inv_item_code = row["item_code"]
        gtin_code = row["gtin"]
        if inv_item_code in inv_items and gtin_code:
            key = f"{inv_item_code}--{gtin_code}"
            # Ignore duplicate rows.
            if key not in seen_keys:
                seen_keys.append(key)
                updated = upsert(key, {
                    "inventory_item": inv_items[inv_item_code],
                    "code": row["gtin"],
                    "uom": row["uom"],
                    "conv_factor": row["conversion"]
                })
                if updated:
                    updated_count += 1
                else:
                    inserted_count += 1
            else:
                skipped_count += 1
        else:
            skipped_count += 1

    # Commit the database queries and log the results.
    db_session.commit()
    logging.info(
        f"Import GTINItems: "
        f"{inserted_count} inserted, "
        f"{updated_count} updated, "
        f"{skipped_count} skipped.")


def load_spl_rows(filepath):
    """
    Loads the rows from a supplier pricelist file.

    Params:
        filepath: The path to the supplier pricelist file.

    Returns:
        The DictReader for the supplier pricelist file.
    """
    with open(filepath, "r", encoding="iso8859-14") as file:
        return csv.DictReader(file, SPL_FIELDNAMES)


def import_supplier_pricelist_items(filepath):
    """
    Imports supplier pricelist items from file.

    Params:
        filepath: The path to the supplier pricelist file.

    Returns:
        The list of SPL items.
    """
    overridden_record_count = 0  # The number of records overridden.
    invalid_record_count = 0     # The number of invalid records.
    spl_items = {}  # Hashmap of SPL items keyed by item code and supp code.

    # Collect supplier pricelist items. If an item has the same item code
    # and supplier code as a previous item then the new item will take its
    # place. The previous item is counted as an overridden record.
    for row in load_spl_rows(filepath):
        item_code = row["item_code"]
        supplier_code = row["supplier_code"]
        uom = row["supp_uom"]
        if uom == "":
            invalid_record_count += 1
            continue
        if item_code not in spl_items.keys():
            spl_items[item_code] = {}
        if supplier_code in spl_items[item_code].keys():
            overridden_record_count += 1
        spl_items[item_code][supplier_code] = row

    # Log the results and return the collected SPL items as a flattened list.
    spl_items_flattened = []
    for rows in spl_items.values():
        for row in rows.values():
            spl_items_flattened.append(row)
    logging.info(
        f"Import SPL records: "
        f"{len(spl_items_flattened)} inserted, "
        f"{invalid_record_count} skipped, "
        f"{overridden_record_count} overridden.")
    return spl_items_flattened


def import_web_sortcodes(filepath, db_session, worksheet_name="sortcodes"):
    """
    Import WebSortcodes from datagrid.

    Params:
        filepath: The path to the gtin items datagrid.
    """
    import_count = 0
    skipped_count = 0
    for row in load_rows(filepath, worksheet_name):
        web_sortcode = db_session.query(WebSortcode).filter(
            WebSortcode.parent_name == row["parent_name"],
            WebSortcode.child_name == row["child_name"],
        ).scalar()
        if not web_sortcode:
            db_session.add(WebSortcode(
                parent_name=row["parent_name"].strip(),
                child_name=row["child_name"].strip(),
            ))
            import_count += 1
        else:
            skipped_count += 1

    # Commit the database queries and log the results.
    db_session.commit()
    logging.info(
        f"Import WebSortcodes: "
        f"{import_count} inserted, "
        f"{skipped_count} skipped.")


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

    # Log the results and return the list of mappings.
    logging.info(
        f"Import WebSortcode mappings: "
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

    # Log the results and return the list of images.
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
