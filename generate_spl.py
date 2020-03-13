#!/usr/bin/env python3

from pxi.operations import operations
import sys

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

operations.generate_spl(
    inventory_items_datagrid="data/import/inventory_items.xlsx",
    supplier_items_datagrid="data/import/supplier_items.xlsx",
    supplier_pricelist="data/import/supplier_pricelist.csv",
    supplier_price_changes_report="data/export/supplier_price_changes_report.xlsx",
    updated_supplier_pricelist="data/export/supplier_pricelist.csv"
)
