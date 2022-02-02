from decimal import Decimal
from sqlalchemy import or_

from pxi.models import SupplierItem, InventoryItem
from pxi.data import BuyPriceChange


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


def update_supplier_items(spl_items, db_session):
    """
    Updates price on SupplierItems and reports on price changes and UOM errors.
    """
    price_changes = []  # The list of price changes.
    updated_supp_item_keys = set()  # The supp items that have been updated.

    # Update SupplierItem prices and validate UOM and conversion factor.
    for spl_item in spl_items:
        supp_items = db_session.query(SupplierItem).filter(
            SupplierItem.code == spl_item.supp_code,
            SupplierItem.item_code == spl_item.supp_item_code,
        ).all()

        # Calculate price changes.
        for supp_item in supp_items:
            price_change = BuyPriceChange(
                supp_item,
                Decimal(supp_item.buy_price),
                spl_item.supp_price)
            if price_change.price_diff_abs > 0:
                key = f"{supp_item.code}--{supp_item.item_code}"
                if key not in updated_supp_item_keys:
                    updated_supp_item_keys.add(key)
                    supp_item.buy_price = str(spl_item.supp_price)
                    db_session.commit()
                    price_changes.append(price_change)

    return price_changes
