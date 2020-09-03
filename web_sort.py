#!/usr/bin/env python3

from pxi.operations import operations
import sys

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

operations.web_sort(
    inventory_items_datagrid="data/import/inventory_items.xlsx",
    inventory_metadata="data/import/inventory_metadata.xlsx",
    product_web_sortcode_task="data/export/product_web_sortcode_task.txt",
)
