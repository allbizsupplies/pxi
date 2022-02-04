from sqlalchemy.orm.session import Session
from typing import Dict, List

from pxi.models import InventoryWebDataItem, WebSortcode


MANUALLY_SORTED = 'man'


def update_product_menu(
        iwd_items: List[InventoryWebDataItem],
        web_sortcode_mappings: Dict[str, WebSortcode],
        session: Session):
    """
    Maps WebSortcodes to InventoryWebDataItems.

    Params:
        inv_web_data_items: List of InventoryWebDataItems to work on.
        web_sortcode_mappings: Map of PriceRules to WebSortcodes.
        session: The database session.

    Returns:
        List of updated InventoryWebDataItems.
    """
    updated_iwd_items: List[InventoryWebDataItem] = []
    for iwd_item in iwd_items:
        inv_item = iwd_item.inventory_item
        pr_item = inv_item.default_price_region_item
        rule_code = pr_item.price_rule.code
        web_sortcode = web_sortcode_mappings.get(rule_code)
        if web_sortcode and web_sortcode != MANUALLY_SORTED:
            iwd_item.web_sortcode = web_sortcode
            session.commit()
            updated_iwd_items.append(iwd_item)
    return updated_iwd_items
