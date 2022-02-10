# Commands

PXI is a console application. It doesn't have a GUI (graphical user interface) which means you need to open a console (terminal/command prompt) to give it commands.

## Open a terminal in Windows

You can use either cmd.exe or PowerShell to run commands.

1. Open the PXI folder in Windows Explorer (the file explorer).
2. Hold Shift and right-click, then select **Open command prompt here**. (Alternatively you may instead see the option **Open PowerShell window here**, which also works.)

## Executing commands

The following commands are available:

| Commmand           | Description                                                 |
| :----------------- | :---------------------------------------------------------- |
| `download_spl`     | Download suppler pricelist.                                 |
| `fetch_images`     | Download web-ready images for products that don't have one. |
| `generate_spl`     | Generate supplier pricelist.                                |
| `missing_gtin`     | Identify items missing a unit barcode.                      |
| `price_calc`       | Recalculate prices, generate CSV pricelist.                 |
| `upload_pricelist` | Upload CSV pricelist.                                       |
| `upload_spl`       | Upload generated supplier pricelist.                        |
| `web_update`       | Sort products into web categories.                          |

To execute a command, enter `pxi.py <command-name>`

On Windows:

```
> .\pxi.py price_calc
```

You can use hyphens instead of underscores:

```
> .\pxi.py price-calc
```

To see a list of commands, enter `.\pxi.py help`
