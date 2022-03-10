# Exporting datagrids from Pronto

Before using PXI you need to export several datagrids from Pronto and save then in Excel (`xlsx`) files. This guide explains how to export those files and where to save them.

## Export procedure for all datagrids

1. Open the datagrid by following the instructions for that particular datagrid.
2. Click **Export** (found under the Home tab on the ribbon)
3. Pronto will download a temporary file to your computer and automatically open it in Excel (or another spreadsheet program like LibreOffice).
4. Save the spreadsheet to the location specified in the instructions. Make sure to change the file format to Excel `xlsx`. (Pronto may have saved it as a `txt`, `csv` or `ods`.)

Each datagrid has a key. This is the name used to refer to the file in the configuration. For example, the kay for the inventory items datagrid is `inventory_items_datagrid`.

Example configuration for imported files. This tells PXI where to find the datagrids that you've downloaded

```yaml
paths:
  imports:
    contract_items_datagrid: "data/import/contract_items.xlsx" #
    inventory_items_datagrid: "data/import/inventory_items.xlsx"
    gtin_items_datagrid: "data/import/gtin_items.xlsx"
    price_rules_datagrid: "data/import/price_rules.xlsx"
    pricelist_datagrid: "data/import/pricelist.xlsx"
    supplier_items_datagrid: "data/import/supplier_items.xlsx"
    inventory_web_data_items_datagrid: "data/import/inventory_web_data_items.xlsx"
```

In this example the file paths are written using Unix-like paths, with forward slashes (`/`). These are the same as the backslashes (`\`) used in Windows file paths. These file paths are also relative which means that the path actually starts in the same folder as PXI.

For example, if you have installed pxi at `/home/brad/pxi`, then the inventory items datagrid is actually found at `/home/brad/pxi/data/import/inventory_items.xlsx`.

## Contract items datagrid

This file contains the items on all contracts.

Import path key: `contract_items_datagrid`

Default file location: `data/import/contract_items.xlsx`

Export instructions:

1. Open the datagrid "DI Contract Listing - All Contracts" (`ZUSR.E053`). (Accounts Receivable > Customer Pricing > Contract Management > Contract Management Reports > DI Contract Listing - All Contracts)
2. Export and save the datagrid.

## Inventory items datagrid

This file contains data for inventory items and warehouse stock items.

Import path key: `inventory_items_datagrid`

Default file location: `data/import/inventory_items.xlsx`

Export instructions:

1. Open the datagrid "DI Stock with Master Prices Warehouse etc" (`ZUSR.E039`). (Inventory > Inventory Reports > DI Stock with Master Prices Warehouse etc)
2. Enter your default warehouse code.
3. Export and save the datagrid. This export may take a long time.

## GTIN Items datagrid

This file contains data for GTIN items (barcodes and other alternative codes for products).

Import path key: `gitn_items_datagrid`

Default file location: `data/import/gitn_items.xlsx`

Export instructions:

1. Open the datagrid "DI Data for stock-unit-conversion (GTIN)". (Inventory > Inventory Reports > DI Data for stock-unit-conversion (GTIN))
2. Export and save the datagrid.

## Price rules datagrid

This file contains the price rules (price algorithms) used for price recalculation. This file usually only needs to be exported after making changes to price rules in Pronto, and that probably won't happen too often.

Import path key: `price_rules_datagrid`

Default file location: `data/import/price_rules.xlsx`

Export instructions:

1. Open the function "DI Price Algorithm Rules". (Inventory > Prices Control > Price List Processing > DI Price Algorithm Rules).
2. Export and save the datagrid.

## Pricelist datagrid

This file contains the pricelist for existing prices in Pronto. This datagrid needs to be prepared before it can be exported.

The pricelist is not the same as the actual price records for inventory items. The pricelist holds a copy of the prices for some or all of your inventory items, and is intended to be a place where you can import or change prices in bulk before applying them to the live price records. The downside is that the copying and exporting process is very slow.

Import path key: `pricelist_datagrid`

Default file location: `data/import/pricelist.xlsx`

Instructions to build the pricelist:

1. Open the function "Copy prices from Live" (`INV.M029`). (Inventory > Prices Control > Price List Processing > Copy prices from Live)
2. Use the filters to select a range of price records to be added to the pricelist. Each inventory item may have multiple price regions. To add all price regions for all inventory items, leave all of the filters on their default settings. The copy process may take a long time to complete.

Export instructions:

1. Open the datagrid "Manual Price Change" (`INV.M024`). (Inventory > Prices Control > Price List Processing > Manual Price Change).
2. Leave the filters empty in order to view all items on the pricelist. This can take a long time to open, especially if you copied all inventory items to the pricelist.
3. Export the datagrid. This may take a long time to export. Do not close the datagrid yet.
4. The datagrid will have an empty column in column A. Delete this column and save the datagrid.
5. Click **Select All** on the datagrid to mark all items. Click **Remove** to clear the pricelist.

## Supplier items datagrid

This file contains data for inventory item supplier records.

Import path key: `supplier_items_datagrid`

Default file location: `data/import/supplier_items.xlsx`

Export instructions:

1. Open the datagrid "DI Stock Supplier Priority". (Inventory > Inventory Reports > DI Stock Supplier Priority)
2. Export and save the datagrid.

## Inventory web data items datagrid

This file contains data for inventory item web category and online status.

Import path key: `inventory_web_data_items_datagrid`

Default file location: `data/import/inventory_web_data_items.xlsx`

1. Open the datagrid "Stock Code Web Data Review". (Web Site / eChoice - Integration)
2. Export the datagrid.
3. The datagrid will have an empty column in column A. Delete this column and save the datagrid.
