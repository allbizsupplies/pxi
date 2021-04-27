#!/usr/bin/env python3

from pxi.operations import operations
import sys

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

operations.web_update(
    inventory_items_datagrid="data/import/inventory_items.xlsx",
    inventory_web_data_items_datagrid="data/import/inventory_web_data_items.xlsx",
    price_rules_datagrid="data/import/price_rules.xlsx",
    pricelist_datagrid="data/import/pricelist.xlsx",
    inventory_metadata="data/import/inventory_metadata.xlsx",
    web_product_menu_data="data/export/web_product_menu_data.csv",
    web_data_updates_report="data/export/web_data_updates_report.xlsx"
)
