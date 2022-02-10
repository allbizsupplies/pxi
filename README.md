# PXI - Pronto Xi utilities for Office Choice dealers.

## System requirements

- Python 3.10 or later.
- the following Python packages:
  - openpyxl
  - paramiko
  - pillow
  - progressbar2
  - python-dotenv
  - pyyaml
  - requests
  - selenium
  - scp
  - sqlalchemy

## Installation

1. Clone or download this repository to your computer.
2. Create the configuration file. See the [configuration guide](docs/configuration_guide.md).
3. Install Python 3.10 or later.
4. Install the required Python packages by running `python -m pip install -r requirements` from the installation directory.

## Recalculate and import pricelist

[Read the guide](docs/price_calc_guide.md)

While Pronto has a built-in price recalculation function, PXI makes it easier to control the price update:

- See which prices have changed and by how much.
- Report on price changes and diagnose price recalculation errors.
- Calculate updates to contracts to match changes in retail prices.
- Print a list of updated shelf tickets only for products that are on the shelf.
- Adjust GST-inclusive prices to a rounded or charm price (e.g. $29.95 or $200.00).
- Upload the generated CSV pricelist to the Pronto server, to be imported.

## Generate and import supplier pricelist

Office Choice maintains supplier pricelists containing buy prices for most items available through Office Choice preferred suppliers, and these supplier pricelists can be imported into Pronto via its Supplier Catalogue.

PXI speeds up the SPL update process:

[Read the guide](docs/generate_spl_guide.md)

- Add rows to the SPL for products that are not in Office Choice's PIM system such as custom kit codes.
- Report on supplier price changes and quickly identify UOM errors.
- Limit the pricelist import to only those supplier prices that differ from the supplier records in Pronto.
- Upload the generated SPL to the Pronto server, to be imported.

## Fetch missing web images for inventory items

[Read the guide](docs/fetch_images_guide.md)

Office Choice provides product images for all inventory items that are in the OC managed rango but does not necessarily provide product images for items in the rest of OC PIM, and provides no images for items not in PIM. Normally the process of finding and preparing missing product images is a manual process: a staff member has to search for and download each image from the web.

PXI automates the process of finding, downloading and processing images from a list of suppliers. The files can then be sent to Office Choice to be imported into the online store.

## Report on missing unit barcodes for inventory items.

[Read the guide](docs/missing_gtin_guide.md)

PXI automates the process of reporting products that do not have a barcode for an individual inventory item. It also reports which of these products are in store, which makes it relatively easy to identify which barcodes can be added immediately by staff in-store.
