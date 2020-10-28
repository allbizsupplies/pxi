#!/usr/bin/env python3

from pxi.operations import operations
import sys

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

operations.fetch_images(
    inventory_items_datagrid="data/import/inventory_items.xlsx",
    supplier_items_datagrid="data/import/supplier_items.xlsx",
    website_images_report="data/import/website_images_report.xlsx",
    downloaded_images_report="data/export/downloaded_images_report.xlsx",
    images_dir="data/export/images"
)
