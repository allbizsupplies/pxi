#!/usr/bin/env python3

from pxi.operations import operations
import sys

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

operations.price_calc(
    inventory_items_datagrid="data/import/inventory_items.xlsx",
    price_rules_datagrid="data/import/price_rules.xlsx",
    pricelist_datagrid="data/import/pricelist.xlsx",
    contract_items_datagrid="data/import/contract_items.xlsx",
    price_changes_report="data/export/price_changes_report.xlsx",
    pricelist="data/export/pricelist.csv",
    product_price_task="data/export/product_price_task.txt",
    contract_item_task="data/export/contract_item_task.txt",
    tickets_list="data/export/tickets_list.txt"
)
