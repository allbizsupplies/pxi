import asyncio
from datetime import datetime
from decimal import Decimal
import logging
from time import perf_counter

from pxi.database import get_session
from pxi.enum import ItemCondition, ItemType
from pxi.exporters import (
    export_contract_item_task,
    export_price_changes_report,
    export_pricelist,
    export_product_price_task,
    export_tickets_list,
)
from pxi.importers import import_data
from pxi.models import ContractItem, InventoryItem, PriceRegionItem, PriceRule, WarehouseStockItem
from pxi.price_calc import (
    recalculate_contract_prices,
    recalculate_sell_prices
)
from pxi.scp import get_scp_client


class CommandBase:
    """
    Base class for commands. stores config and is callable.
    """

    def __init__(self, config):
        self.config = config
        self.db_session = get_session(config["paths"]["database"])

    def __call__(self, **options):
        self.execute(options)


class Commands:
    """
    Namespace class containing executable commands.
    """

    class help(CommandBase):
        """
        Displays a list of commands.
        """
        aliases = ["h"]

        def execute(self, options):
            print()
            print("Available commands:")
            print()
            for command in commands():
                print(f"{command.__name__:<24}"
                      f"{command.__doc__.strip()}")
            print()

    class price_calc(CommandBase):
        """
        Calculates rounded prices for PriceRegionItems assigned a PriceRule.
        """
        aliases = ["pc"]

        def execute(self, options):

            # Import all data related to PriceRegionItems and ContractItems.
            import_data(self.db_session, self.config["paths"]["import"], [
                InventoryItem,
                WarehouseStockItem,
                PriceRule,
                PriceRegionItem,
                ContractItem,
            ], force_imports=options.get("force_imports", False))

            # Select all PriceRegionItems that have a PriceRule and belong
            # to an active InventoryItem.
            # pylint:disable=no-member
            pr_items = self.db_session.query(PriceRegionItem).join(
                PriceRegionItem.inventory_item
            ).join(
                PriceRegionItem.price_rule
            ).filter(
                PriceRegionItem.price_rule_id.isnot(None),
                ~PriceRule.code.in_(self.config["price_rules"]["ignore"]),
                InventoryItem.condition != ItemCondition.DISCONTINUED,
                InventoryItem.condition != ItemCondition.INACTIVE,
                InventoryItem.item_type != ItemType.CROSS_REFERENCE,
                InventoryItem.item_type != ItemType.LABOUR,
                InventoryItem.item_type != ItemType.INDENT_ITEM
            ).all()
            price_changes = recalculate_sell_prices(
                pr_items, self.db_session)
            updated_pr_items = [
                price_change.price_region_item
                for price_change in price_changes
            ]
            updated_con_items = recalculate_contract_prices(
                price_changes, self.db_session)

            # Select all PriceRegionItems in the default price region, where
            # the retail price has changed.
            updated_default_pr_items = []
            for price_change in price_changes:
                price_region_item = price_change.price_region_item
                in_def_price_region = price_region_item.in_default_price_region
                price_has_changed = price_change.price_0_differs
                if in_def_price_region and price_has_changed:
                    updated_default_pr_items.append(price_region_item)

            # Select all WarehouseStockItems that belong to an InventoryItem
            # with an updated default PriceRegionItem, and meet one of the
            # following criteria:
            # - The warehouse has stock on hand for this item.
            # - The warehouse has a minimum order quantity for this item.
            # - The warehouse has a BIN location for this item and the BIN is
            #   not on the ignore list.
            ticketed_whse_stock_items = []
            for price_region_item in updated_default_pr_items:
                inv_item = price_region_item.inventory_item
                whse_stock_items = inv_item.warehouse_stock_items
                for whse_stock_item in whse_stock_items:
                    if whse_stock_item.on_hand > 0:
                        ticketed_whse_stock_items.append(
                            whse_stock_item)
                    elif whse_stock_item.minimum > 0:
                        ticketed_whse_stock_items.append(
                            whse_stock_item)
                    elif whse_stock_item.bin_location:
                        ignored_bins = self.config["bin_locations"]["ignore"]
                        if whse_stock_item.bin_location not in ignored_bins:
                            ticketed_whse_stock_items.append(
                                whse_stock_item)

            # Export reports and data files:
            # - Price changes report
            # - Pronto-format pricelist
            # - Taskrunner data files for these tasks:
            #   - update_product_price
            #   - update_contract_item
            # - Tickets list (a plain text list of item codes)
            export_paths = self.config["paths"]["export"]
            export_price_changes_report(
                export_paths["price_changes_report"],
                price_changes)
            export_pricelist(
                export_paths["pricelist"],
                updated_pr_items)
            export_product_price_task(
                export_paths["product_price_task"],
                updated_pr_items)
            export_contract_item_task(
                export_paths["contract_item_task"],
                updated_con_items)
            export_tickets_list(
                export_paths["tickets_list"],
                ticketed_whse_stock_items)

            # Log results.
            logging.info(
                f"PriceRegionItems updated: "
                f"{len(price_changes)}")
            logging.info(
                f"ContractItems updated: "
                f"{len(updated_con_items)}")

    class download_spl(CommandBase):
        """
        Download supplier pricelist from remote server.
        """
        aliases = ["dspl"]

        def execute(self, options):
            # Download the file using SCP.
            config = self.config["ssh"]
            src = self.config["paths"]["remote"]["supplier_pricelist"]
            dest = self.config["paths"]["import"]["supplier_pricelist"]
            scp_client = get_scp_client(
                config["hostname"],
                config["username"],
                config["password"])
            scp_client.get(src, dest)

            # Log results.
            logging.info(f"Downloaded SPL to {dest}")

    class upload_spl(CommandBase):
        """
        Upload supplier pricelist to remote server.
        """
        aliases = ["uspl"]

        def execute(self, options):
            # Upload the file using SCP.
            config = self.config["ssh"]
            src = self.config["paths"]["export"]["supplier_pricelist"]
            dest = self.config["paths"]["remote"]["supplier_pricelist_import"]
            scp_client = get_scp_client(
                config["hostname"],
                config["username"],
                config["password"])
            scp_client.put(src, dest)

            # Log results.
            logging.info(f"Uploaded SPL to {config['hostname']}:{dest}")

    class upload_pricelist(CommandBase):
        """
        Upload pricelist to remote server.
        """
        aliases = ["upl"]

        def execute(self, options):
            # Upload the file using SCP.
            config = self.config["ssh"]
            src = self.config["paths"]["export"]["pricelist"]
            dest = self.config["paths"]["remote"]["pricelist"]
            scp_client = get_scp_client(
                config["hostname"],
                config["username"],
                config["password"])
            scp_client.put(src, dest)

            # Log results.
            logging.info(f"Uploaded pricelist to {config['hostname']}:{dest}")


def commands():
    """
    Generates a list of commands.
    """
    for attr_name in dir(Commands):
        # Yield attribute if it is a subclass of CommandBase.
        attr = getattr(Commands, attr_name)
        is_class = type(attr).__name__ == "type"
        if is_class and attr.__base__.__name__ == "CommandBase":
            yield attr


def get_command(command_name):
    """
    Fetch a command given its name or alias.
    """
    # Accept hyphens in place of underscores.
    command_name = command_name.replace("-", "_")

    # Search for command by both class name and aliases attribute.
    for command in commands():
        if command_name == command.__name__ or command_name in command.aliases:
            return command
