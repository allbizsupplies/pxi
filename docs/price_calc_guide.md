# Recalculate and import pricelist

While Pronto has a built-in price recalculation function, PXI makes it easier to control the price update:

- See which prices have changed and by how much.
- Diagnose price recalculation errors.
- Calculate updates to contracts to match changes in retail prices.
- Print a list of updated shelf tickets only for products that are on the shelf.
- Adjust GST-inclusive prices to a rounded or charm price (e.g. $29.95 or $200.00).
- Upload the generated CSV pricelist to the Pronto server.

## Recalculate pricelist

Before running a price calculation we need to export some datagrids from Pronto and save them as Excel files.

- Inventory Items datagrid
- Price Rules datagrid
- Pricelist datagrid

See the guide on [exporting datagrids from Pronto](datagrid_export_guide.md) for instructions on exporting these files.

To perform the price recalculations, run this command: `./pxi.py price-calc`. This will import the inventory and pricing data from the datagrids, perform the price calculations, and create several files.

| File                    | Default location                        | Description                                                                                           |
| :---------------------- | :-------------------------------------- | :---------------------------------------------------------------------------------------------------- |
| Price Changes Report    | `data/export/price_changes_report.xlsx` | Price changes report, showing price changes and recommended contract price updates.                   |
| Pronto CSV pricelist    | `data/export/pricelist.csv`             | A pricelist containing only updated prices which can be imported into Pronto.                         |
| Tickets list            | `data/export/tickets_list.txt`          | A plain text list of item codes which can be pasted into the Shelf Putaway Labels function in Pronto. |
| Product Price Task Data | `data/export/product_price_task.txt`    | Data for running `product_price update` using `allbizsupplies/taskrunner`                             |
| Contract Item Task Data | `data/export/contract_item_task.txt`    | Data for running `contract_item update` using `allbizsupplies/taskrunner`                             |

## Import pricelist into Pronto.

Once you've created a new CSV pricelist using `./pxi.py price-calc`, you can upload this file to your user's home folder on the Pronto server.

Run this command: `./pxi.py upload-pricelist` to upload the CSV pricelist to the Pronto server.

## Price Recalculation process.

The price calculator uses Pronto's price rules (price algorithms) to calculate prices. Most commonly, these price rules will apply a price factor to the product's replacement cost, but a different price factor and basis can be used for each price level in the price rule.

Here's an example of a typical price rule:

| Basis | Factor | Price equals     |
| :---- | :----- | :--------------- |
| C     | 2.00   | Repl cost × 2    |
| C     | 1.75   | Repl cost × 1.75 |
| C     | 1.50   | Repl cost × 1.50 |
| C     | 1.30   | Repl cost × 1.30 |
| C     | 1.25   | Repl cost × 1.25 |

If a product has a price rule set on its price record, then the price calculator calculates a new set of prices based on that rule. These new prices often come to odd amounts, such as $35.02, which look untidy, so the price calculator feeds each of these prices through another function which adjusts the price to come to a nice round number, and optionally adds/subtracts a small amount to produce a charm price.

There are the rules for price adjustments:

| Price range          | Adjustment                                                                                                 |
| :------------------- | :--------------------------------------------------------------------------------------------------------- |
| Prices below $1.00   | Round to the nearest cent.                                                                                 |
| Prices below $25.00  | Round to the nearest multiple of five cents                                                                |
| Prices below $99.00  | Round to the nearest five cents, and make a charm price if price is close to a multiple of $1.00           |
| Prices below $199.00 | Round to the nearest dollar, and make a charm price if price is close to a multiple of ten dollars         |
| Prices above $199.00 | Round to the nearest ten dollars, and make a charm price if price is close to a multiple of ten dollars.\* |

**Charm prices** take advantage of left digit bias, the tendency to measure a price based mostly on the left-most digit. For example, $2.95 is very close to $3, but the buyer is think of this price as closer to $2.

For prices below $99.00, the charm price is five cents below a whole dollar amount. For example, $30.02 will be rounded to $30.00 and then adjusted to $29.95.

For prices above $99.00, the charm price is one dollar below a multiple of ten dollars. For example, $151.12 will be rounded to $150.00 and then adjusted to $149.00. In addition, prices close to a multiple of $100.00 are adjusted further, so $306.00 will become $299.00.
