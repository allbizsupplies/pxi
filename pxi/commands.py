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
        Calculates rounded prices for price region items assigned a price rule.
        """
        aliases = ["pc"]

        def execute(self, options):

            # Import all data related to price region items and contract items.
            import_data(self.db_session, self.config["paths"]["import"], [
                InventoryItem,
                WarehouseStockItem,
                PriceRule,
                PriceRegionItem,
                ContractItem,
            ], force_imports=options.get("force_imports", False))

            # Select all price region items that have a price rule and belong
            # to an active inventory item.
            # pylint:disable=no-member
            price_region_items = self.db_session.query(PriceRegionItem).join(
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
                price_region_items, self.db_session)
            updated_price_region_items = [
                price_change.price_region_item for price_change in price_changes
            ]
            updated_contract_items = recalculate_contract_prices(
                price_changes, self.db_session)

            def updated_default_price_regions():
                for price_change in price_changes:
                    price_region_item = price_change.price_region_item
                    in_default_price_region = price_region_item.code != ""
                    price_has_changed = price_change.price_diffs[0] < Decimal(
                        "0.005")
                    if in_default_price_region and price_has_changed:
                        yield price_region_item

            def ticketed_warehouse_stock_items():
                for price_region_item in updated_default_price_regions():
                    inventory_item = price_region_item.inventory_item
                    warehouse_stock_items = inventory_item.warehouse_stock_items
                    for warehouse_stock_item in warehouse_stock_items:
                        if warehouse_stock_item.on_hand > 0:
                            yield warehouse_stock_item
                        elif warehouse_stock_item.minimum > 0:
                            yield warehouse_stock_item
                        elif warehouse_stock_item.bin_location:
                            ignored_bin_locations = self.config["bin_locations"]["ignore"]
                            if warehouse_stock_item.bin_location not in ignored_bin_locations:
                                yield warehouse_stock_item

            export_paths = self.config["paths"]["export"]
            export_price_changes_report(
                export_paths["price_changes_report"], price_changes)
            export_pricelist(
                export_paths["pricelist"], updated_price_region_items)
            export_product_price_task(
                export_paths["product_price_task"], updated_price_region_items)
            export_contract_item_task(
                export_paths["contract_item_task"], updated_contract_items)
            export_tickets_list(
                export_paths["tickets_list"], ticketed_warehouse_stock_items())
            logging.info("")

    class download_spl(CommandBase):
        """
        Download supplier pricelist from remote server.
        """
        aliases = ["dspl"]

        def execute(self, options):
            config = self.config["ssh"]
            scp_client = get_scp_client(
                config["hostname"], config["username"], config["password"])
            scp_client.get(self.config["paths"]["remote"]["supplier_pricelist"],
                           self.config["paths"]["import"]["supplier_pricelist"])

    class upload_spl(CommandBase):
        """
        Upload supplier pricelist to remote server.
        """
        aliases = ["uspl"]

        def execute(self, options):
            config = self.config["ssh"]
            scp_client = get_scp_client(
                config["hostname"], config["username"], config["password"])
            scp_client.put(self.config["paths"]["export"]["supplier_pricelist"],
                           self.config["paths"]["remote"]["supplier_pricelist_import"])

    class upload_pricelist(CommandBase):
        """
        Upload pricelist to remote server.
        """
        aliases = ["upl"]

        def execute(self, options):
            config = self.config["ssh"]
            scp_client = get_scp_client(
                config["hostname"], config["username"], config["password"])
            scp_client.put(self.config["paths"]["export"]["pricelist"],
                           self.config["paths"]["remote"]["pricelist"])


def commands():
    """
    Generates a list of commands.
    """
    for attr_name in dir(Commands):
        attr = getattr(Commands, attr_name)
        if type(attr).__name__ == "type" and attr.__base__.__name__ == "CommandBase":
            yield attr


def get_command(command_name):
    """
    Fetch a command given its name or alias.
    """
    for command in commands():
        if command_name == command.__name__ or command_name in command.aliases:
            return command
