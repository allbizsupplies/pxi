from progressbar import progressbar

from pxi.models import WebSortcode


def update_product_menu(inventory_items, web_sortcode_mappings, session):
    updated_inventory_items = []
    for inventory_item in inventory_items:
        price_region_item = inventory_item.default_price_region_item
        rule_code = price_region_item.price_rule.code
        inventory_web_data_item = inventory_item.inventory_web_data_item
        try:
            web_sortcode = web_sortcode_mappings[rule_code]
            if web_sortcode and web_sortcode != "man":
                inventory_web_data_item.web_sortcode = web_sortcode
                session.commit()
                updated_inventory_items.append(inventory_item)
        except KeyError:
            pass
    return updated_inventory_items
