from progressbar import progressbar

from pxi.models import WebSortcode


def add_web_sortcodes(price_region_items, web_sortcode_mappings, session):
    updated_inventory_items = []
    for price_region_item in price_region_items:
        rule_code = price_region_item.price_rule.code
        inventory_item = price_region_item.inventory_item
        try:
            web_sortcode = web_sortcode_mappings[rule_code]
            if web_sortcode != "man" and web_sortcode is not None:
                inventory_item.web_sortcode = web_sortcode
                session.commit()
                updated_inventory_items.append(inventory_item)
        except KeyError:
            pass
    return updated_inventory_items
