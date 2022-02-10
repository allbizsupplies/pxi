# Generate and import supplier pricelist

Office Choice maintains supplier pricelists containing buy prices for most items available through Office Choice preferred suppliers, and these supplier pricelists can be imported into Pronto via its Supplier Catalogue.

PXI streamlines this process:

- Add rows to the SPL for products that are not in Office Choice's PIM system such as custom kit codes.
- Report on supplier price changes and quickly identify UOM errors.
- Limit the pricelist import to only those supplier prices that differ from the supplier records in Pronto.
- Upload the generated SPL to the Pronto server, to be imported.

## Download Office Choice supplier pricelist

Run `./pxi.py download-spl` to download the supplier pricelist provided by Office Choice.

## Generate new supplier pricelist

Run `./pxi.py generate-spl` to generate a new supplier pricelist.

## Upload new supplier pricelist.

Run `./pxi.py upload-spl` to upload the new supplier pricelist to the Pronto server.
