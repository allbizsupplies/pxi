from decimal import Decimal
from sqlalchemy import or_
from progressbar import progressbar

from pxi.models import SupplierItem, InventoryItem


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
    uom_errors = []
    for item in progressbar(supplier_pricelist_items):
        supplier_code = item["supplier_code"]
        item_code = item["item_code"]
        supp_item_code = item["supp_item_code"]
        buy_price = Decimal(item["supp_price_1"]).quantize(Decimal("0.01"))
        supplier_items = session.query(SupplierItem).join(
            SupplierItem.inventory_item
        ).filter(
            SupplierItem.code == supplier_code,
            or_(
                SupplierItem.item_code == supp_item_code,
                InventoryItem.code == item_code
            ),
        ).all()
        if len(supplier_items) == 0:
            continue
        for supplier_item in supplier_items:
            # Calculate price change.
            price_diff = buy_price - supplier_item.buy_price
            if abs(price_diff) > 0:
                price_now = buy_price
                price_was = supplier_item.buy_price
                price_diff_percentage = 1
                if price_was:
                    price_diff_percentage = price_diff / price_was
                supplier_item.buy_price = buy_price
                session.commit()
                price_changes.append({
                    "supplier_item": supplier_item,
                    "price_was": price_was,
                    "price_now": price_now,
                    "price_diff": price_diff,
                    "price_diff_percentage": price_diff_percentage,
                })
            # Validate UOM.
            uom_matches = item["supp_uom"] == supplier_item.uom
            conv_factor_matches = Decimal(
                item["supp_conv_factor"]) == Decimal(supplier_item.conv_factor)
            item_code_matches = item_code == supplier_item.inventory_item.code
            if not uom_matches:
                expected = item["supp_uom"]
                actual = supplier_item.uom
                uom_errors.append({
                    "message": "UOM doesn't match.",
                    "spl_item_code": item_code,
                    "expected": expected,
                    "actual": actual,
                    "supplier_item": supplier_item,
                })
            elif item_code_matches and not conv_factor_matches:
                expected = Decimal(item["supp_conv_factor"])
                actual = Decimal(supplier_item.conv_factor)
                uom_errors.append({
                    "message": "Item code matches but CF does not.",
                    "spl_item_code": item_code,
                    "expected": expected,
                    "actual": actual,
                    "supplier_item": supplier_item,
                })
            elif not item_code_matches and conv_factor_matches:
                expected = item_code
                actual = supplier_item.inventory_item.code
                uom_errors.append({
                    "message": "CF matches but item code does not.",
                    "spl_item_code": item_code,
                    "expected": expected,
                    "actual": actual,
                    "supplier_item": supplier_item,
                })

    return price_changes, uom_errors
