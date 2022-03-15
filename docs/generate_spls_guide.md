# Generate and import supplier pricelist

Office Choice maintains supplier pricelists containing buy prices for most items available through Office Choice preferred suppliers, and these supplier pricelists can be imported into Pronto via its Supplier Catalogue.

PXI streamlines this process:

- Add rows to the SPL for products that are not in Office Choice's PIM system such as custom kit codes.
- Report on supplier price changes and quickly identify UOM errors.
- Limit the pricelist import to only those supplier prices that differ from the supplier records in Pronto.
- Upload the generated SPL to the Pronto server, to be imported.

## Download Office Choice supplier pricelist

Run `./pxi.py download-spl` to download the supplier pricelist provided by Office Choice.

## Generate new supplier pricelists

Run `./pxi.py generate-spls` to generate new supplier pricelists.

## Upload new supplier pricelists

Run `./pxi.py upload-spls` to upload the new supplier pricelists to the Pronto server.

## List uploaded supplier pricelists

Run `./pxi.py list-uploaded-spls` to list the supplier pricelists that are on the Pronto server.
