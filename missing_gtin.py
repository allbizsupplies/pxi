#!/usr/bin/env python3

from pxi.operations import operations
import sys

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

operations.missing_gtin(
    inventory_items_datagrid="data/import/inventory_items.xlsx",
    gtin_items_datagrid="data/import/gtin_items.xlsx",
    gtin_report="data/export/gtin_report.xlsx"
)
