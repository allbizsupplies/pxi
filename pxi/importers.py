import csv
from datetime import date

from pxi.datagrid import load_rows
from pxi.enum import (
    ItemType,
    ItemCondition,
    PriceBasis,
    TaxCode)
from pxi.models import (
    ContractItem,
    InventoryItem,
    GTINItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem)
from pxi.spl_update import SPL_FIELDNAMES


def import_contract_items(filepath, db_session):
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
    return count


def import_inventory_items(filepath, db_session):
    count = 0
    for row in load_rows(filepath):
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
            replacement_cost=row["replacement_cost"]
        )
        db_session.add(inventory_item)
        count += 1
    return count


def import_price_region_items(filepath, db_session):
    count = 0
    for row in load_rows(filepath):
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
    return count


def import_price_rules(filepath, db_session):
    count = 0
    for row in load_rows(filepath):
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
    return count


def import_warehouse_stock_items(filepath, db_session):
    count = 0
    for row in load_rows(filepath):
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
    return count


def import_supplier_items(filepath, db_session):
    count = 0
    for row in load_rows(filepath):
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
    return count

def import_gtin_items(filepath, db_session):
    count = 0
    for row in load_rows(filepath):
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
    return count


def import_supplier_pricelist_items(filepath):
    file = open(filepath, "r", encoding="iso8859-14")
    imported_item_codes = {}
    supplier_pricelist_reader = csv.DictReader(file, SPL_FIELDNAMES)
    supplier_pricelist_items = []
    duplicate_supplier_pricelist_items = []
    for row in supplier_pricelist_reader:
        item_code = row["item_code"]
        supplier_code = row["supplier_code"]
        if item_code not in imported_item_codes.keys():
            imported_item_codes[item_code] = []    
        if supplier_code not in imported_item_codes[item_code]:
            supplier_pricelist_items.append(row)
            imported_item_codes[item_code].append(supplier_code)
        else:
            duplicate_supplier_pricelist_items.append(row)
    if len(duplicate_supplier_pricelist_items) > 0:
        print("  Warning: Skipped {} duplicate records".format(len(duplicate_supplier_pricelist_items)))
    return supplier_pricelist_items
