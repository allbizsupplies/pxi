import csv
from datetime import date
from progressbar import progressbar

from pxi.datagrid import load_rows
from pxi.enum import (
    ItemType,
    ItemCondition,
    PriceBasis,
    TaxCode,
    WebStatus)
from pxi.models import (
    ContractItem,
    InventoryItem,
    GTINItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem,
    WebSortcode)
from pxi.spl_update import SPL_FIELDNAMES


def import_contract_items(filepath, db_session):
    print("Importing contract items...")
    count = 0
    for row in load_rows(filepath):
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["item_code"]
        ).scalar()
        if not inventory_item:
            continue
        contract_item = ContractItem(
            inventory_item=inventory_item,
            code=row["contract_no"],
            price_1=row["price_1"],
            price_2=row["price_2"],
            price_3=row["price_3"],
            price_4=row["price_4"],
            price_5=row["price_5"],
            price_6=row["price_6"],
        )
        db_session.add(contract_item)
        count += 1
    print("{} contract items imported.".format(count))


def import_inventory_items(filepath, db_session):
    print("Importing inventory items...")
    count = 0
    for row in progressbar(load_rows(filepath)):
        inventory_item = InventoryItem(
            code=row["item_code"],
            description_line_1=row["item_description"],
            description_line_2=row["description_2"],
            description_line_3=row["description_3"],
            uom=row["unit"],
            brand=row["brand_manuf"],
            apn=row["manuf_apn_no"],
            group=row["group"],
            created=row["creation_date"],
            item_type=ItemType(row["status"]),
            condition=ItemCondition(row["condition"]),
            replacement_cost=row["replacement_cost"],
            web_status=WebStatus(row["int_flag_sales_type"]),
            web_sortcode=row["internet_tree"]
        )
        db_session.add(inventory_item)
        count += 1
    print("{} inventory items imported.".format(count))


def import_price_region_items(filepath, db_session):
    print("Importing price region items...")
    count = 0
    for row in progressbar(load_rows(filepath)):
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["item_code"]
        ).scalar()
        if not inventory_item:
            continue
        price_rule = None
        if row["rule"]:
            price_rule = db_session.query(PriceRule).filter(
                PriceRule.code == row["rule"]
            ).scalar()
        price_region_item = PriceRegionItem(
            inventory_item=inventory_item,
            price_rule=price_rule,
            code=row["region"] if row["region"] else "",
            tax_code=TaxCode.TAXABLE if row["tax_rate"] else TaxCode.EXEMPT,
            quantity_1=row["pr_1_corpa_qty"],
            quantity_2=row["pr_2_corp_b_qty"],
            quantity_3=row["pr_3_corp_c_qty"],
            quantity_4=row["pr_4_bulk_qty"],
            price_0=row["w_sale_price"],
            price_1=row["pr_1_corpa"],
            price_2=row["pr_2_corp_b"],
            price_3=row["pr_3_corp_c"],
            price_4=row["pr_4_bulk"],
            rrp_excl_tax=row["retail_price"],
            rrp_incl_tax=row["rrp_inc_tax"]
        )
        db_session.add(price_region_item)
        count += 1
    print("{} price region items imported.".format(count))


def import_price_rules(filepath, db_session):
    print("Importing price rules...")
    count = 0
    for row in progressbar(load_rows(filepath)):
        price_rule = PriceRule(
            code=row["rule"],
            description=row["comments"],
            price_0_basis=PriceBasis(row["price0_based_on"]),
            price_1_basis=PriceBasis(row["price1_based_on"]),
            price_2_basis=PriceBasis(row["price2_based_on"]),
            price_3_basis=PriceBasis(row["price3_based_on"]),
            price_4_basis=PriceBasis(row["price4_based_on"]),
            rrp_excl_basis=PriceBasis(row["rec_retail_based_on"]),
            rrp_incl_basis=PriceBasis(row["rrp_inc_tax_based_on"]),
            price_0_factor=row["price0_factor"],
            price_1_factor=row["price1_factor"],
            price_2_factor=row["price2_factor"],
            price_3_factor=row["price3_factor"],
            price_4_factor=row["price4_factor"],
            rrp_excl_factor=row["rec_retail_factor"],
            rrp_incl_factor=row["rrp_inc_tax_factor"]
        )
        db_session.add(price_rule)
        count += 1
    print("{} price rules imported.".format(count))


def import_warehouse_stock_items(filepath, db_session):
    print("Importing warehouse stock items...")
    count = 0
    for row in progressbar(load_rows(filepath)):
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["item_code"]
        ).scalar()
        warehouse_stock_item = WarehouseStockItem(
            inventory_item=inventory_item,
            code=row["whse"],
            minimum=row["minimum_stock"],
            maximum=row["maximum_stock"],
            on_hand=row["on_hand"],
            bin_location=row["bin_loc"],
            bulk_location=row["bulk_loc"]
        )
        db_session.add(warehouse_stock_item)
        count += 1
    print("{} warehouse stock items imported.".format(count))


def import_supplier_items(filepath, db_session):
    print("Importing supplier items...")
    count = 0
    for row in progressbar(load_rows(filepath)):
        if not row["supplier_item"]:
            continue
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["item_code"]
        ).scalar()
        if not inventory_item:
            continue
        supplier_item = SupplierItem(
            inventory_item=inventory_item,
            code=row["supplier"],
            item_code=row["supplier_item"],
            priority=row["priority"],
            uom=row["unit"],
            conv_factor=row["conv_factor"],
            pack_quantity=row["pack_qty"],
            moq=row["eoq"],
            buy_price=row["current_buy_price"],
        )
        db_session.add(supplier_item)
        count += 1
    print("{} supplier items imported.".format(count))


def import_gtin_items(filepath, db_session):
    print("Importing GTIN items...")
    count = 0
    for row in progressbar(load_rows(filepath)):
        inventory_item = db_session.query(InventoryItem).filter(
            InventoryItem.code == row["item_code"]
        ).scalar()
        if not inventory_item:
            continue
        gtin_item = GTINItem(
            inventory_item=inventory_item,
            code=row["gtin"],
            uom=row["uom"],
            conv_factor=row["conversion"]
        )
        db_session.add(gtin_item)
        count += 1
    print("{} GTIN items imported.".format(count))


def import_supplier_pricelist_items(filepath):
    print("Importing supplier pricelist items...")
    file = open(filepath, "r", encoding="iso8859-14")
    supplier_pricelist_reader = csv.DictReader(file, SPL_FIELDNAMES)
    supplier_pricelist_items = {}
    overridden_supplier_items_count = 0
    invalid_record_count = 0
    # Collect supplier pricelist items. If an item has the same item code
    # and supplier code as a previous item then it will override it.
    for row in supplier_pricelist_reader:
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
    file.close()
    # Flatten the list of items.
    supplier_pricelist_items_flattened = []
    for rows in supplier_pricelist_items.values():
        for row in rows.values():
            supplier_pricelist_items_flattened.append(row)
    # Report warnings.
    if invalid_record_count > 0:
        print("  Warning: {} invalid records were skipped.".format(
            invalid_record_count))
    if overridden_supplier_items_count > 0:
        print("  Warning: {} records were overridden.".format(
            overridden_supplier_items_count))
    print("{} supplier pricelist items imported.".format(len(
        supplier_pricelist_items
    )))
    return supplier_pricelist_items_flattened


def import_web_sortcodes(filepath, db_session, worksheet_name="sortcodes"):
    print("Importing web sortcodes...")
    count = 0
    for row in progressbar(load_rows(filepath, worksheet_name)):
        web_sortcode = WebSortcode(
            code=row["sortcode"],
            name=row["description"],
        )
        db_session.add(web_sortcode)
        count += 1
    print("{} web sortcodes imported.".format(count))


def import_web_sortcode_mappings(filepath, worksheet_name="rules"):
    print("Importing web sortcode mappings...")
    web_sortcode_mappings = {}
    for row in progressbar(load_rows(filepath, worksheet_name)):
        rule_code = row["rule_code"]
        web_sortcode_mappings[rule_code] = str(row["sortcode"])
    print("{} web sortcode mappings imported.".format(
        len(web_sortcode_mappings)
    ))
    return web_sortcode_mappings


def import_website_images_report(filepath, db_session):
    print("Importing website images report...")

    def get_image(row):
        for i in range(1, 5):
            filename = row["picture{}".format(i)]
            if filename:
                return filename

    images_data = []
    for row in progressbar(load_rows(filepath)):
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
    print("website image data imported for {} items.".format(
        len(images_data)
    ))
    return images_data
