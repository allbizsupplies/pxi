import csv
from decimal import Decimal

from pxi.models import SupplierItem


SPL_FIELDNAMES = [
    "supplier_code",
    "catalogue_part_no",
    "supp_item_code",
    "desc_line_1",
    "desc_line_2",
    "supp_uom",
    "supp_sell_uom",
    "supp_eoq",
    "supp_conv_factor",
    "supp_price_1",
    "supp_price_2",
    "supp_price_3",
    "supp_price_4",
    "gst",
    "barcode",
    "carton_size",
    "flc_page_no",
    "rrp",
    "major_category",
    "minor_category",
    "was_manufacturer_code",
    "item_code",
    "office_choice_code",
    "quantity_1_pronto_0",
    "quantity_2_pronto_1",
    "quantity_3_pronto_2",
    "quantity_4_pronto_3",
    "price_1_pronto_0",
    "price_2_pronto_1",
    "price_3_pronto_2",
    "price_4_pronto_3",
    "supp_priority",
    "supp_inner_uom",
    "supp_inner_barcode",
    "supp_inner_conversion_factor",
    "supp_outer_uom",
    "supp_outer_barcode",
    "supp_outer_conversion_factor",
    "unit_measurements",
    "unit_weight",
    "cartons_per_pallet",
    "eoq",
    "sell_uom",
    "is_consumable",
    "is_branded",
    "is_green",
    "created_on",
    "status",
    "product_class",
    "product_group",
    "legacy_item_code",
]


def update_supplier_items(supplier_pricelist_items, session):
    price_changes = []
    for item in supplier_pricelist_items:
        supplier_code = item["supplier_code"]
        item_code = item["supp_item_code"]
        buy_price = Decimal(item["supp_price_1"]).quantize(Decimal("0.01"))
        supplier_items = session.query(SupplierItem).filter(
            SupplierItem.code == supplier_code,
            SupplierItem.item_code == item_code,
        ).all()
        if len(supplier_items) == 0:
            continue
        for supplier_item in supplier_items:
            price_diff = supplier_item.buy_price - buy_price
            if abs(price_diff) > 0:
                supplier_item.buy_price = buy_price
                session.commit()
                price_changes.append({
                    "supplier_item": supplier_item,
                    "price_diff": price_diff,
                })
    return price_changes