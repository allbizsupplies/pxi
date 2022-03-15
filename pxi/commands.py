import asyncio
from datetime import datetime
from decimal import Decimal
from distutils.command.upload import upload
import logging
import os
from pathlib import Path
import re
from typing import Dict, List
import requests
from time import perf_counter

from pxi.config import Config
from pxi.database import get_session
from pxi.dataclasses import BuyPriceChange
from pxi.enum import ItemCondition, ItemType
from pxi.exporters import (
    export_contract_item_task,
    export_downloaded_images_report,
    export_gtin_report,
    export_price_changes_report,
    export_pricelist,
    export_product_price_task,
    export_supplier_price_changes_report,
    export_supplier_pricelist,
    export_tickets_list,
    export_web_data_updates_report,
    export_web_product_menu_data,
    remove_exported_supplier_pricelists)
from pxi.image import fetch_images
from pxi.importers import (
    import_data,
    import_supplier_pricelist_items,
    import_web_menu_item_mappings,
    import_missing_images_report)
from pxi.models import (
    ContractItem,
    GTINItem,
    InventoryItem,
    InventoryWebDataItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem,
    WebMenuItem)
from pxi.price_calc import (
    recalculate_contract_prices,
    recalculate_sell_prices)
from pxi.remote import upload_files, download_files, find_files
from pxi.spl_update import update_supplier_items
from pxi.web_update import update_product_menu


class CommandBase:
    """
    Base class for commands. stores config and is callable.
    """

    def __init__(self, config: Config):
        self.config = config
        self.db_session = get_session(":memory:")

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
            import_data(self.db_session, self.config["paths"]["imports"], [
                InventoryItem,
                WarehouseStockItem,
                PriceRule,
                PriceRegionItem,
                ContractItem,
            ])

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

            # Calculate new prices and get price changes.
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
            export_paths = self.config["paths"]["exports"]
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

    class generate_spl(CommandBase):
        """
        Generate a SPL for supplier prices that have changed.
        """
        aliases = ["gspl"]

        def execute(self, options):

            # Import all data related to SupplierItems.
            import_paths = self.config["paths"]["imports"]
            import_data(self.db_session, import_paths, [
                InventoryItem,
                SupplierItem,
            ])

            # Import SupplierPricelistItems.
            supp_items = import_supplier_pricelist_items(
                import_paths["supplier_pricelist"])

            # Update supplier prices and record BuyPriceChanges.
            bp_changes = update_supplier_items(
                supp_items, self.db_session)

            supp_item_bins: Dict[str, List[SupplierItem]] = {}
            # Sort SupplierItems into bins keyed by supplier code.
            for bp_change in bp_changes:
                supp_item = bp_change.supplier_item
                supp_code = supp_item.code
                if supp_code not in supp_item_bins:
                    supp_item_bins[supp_code] = []
                supp_item_bins[supp_code].append(supp_item)

            # Export report and data files:
            # - Supplier price changes report
            # - Pronto-format supplier pricelist
            export_paths = self.config["paths"]["exports"]
            export_supplier_price_changes_report(
                export_paths["supplier_price_changes_report"],
                bp_changes)
            remove_exported_supplier_pricelists(
                export_paths["supplier_pricelist"])
            for supp_code, supp_items in supp_item_bins.items():
                export_supplier_pricelist(
                    export_paths["supplier_pricelist"].format(
                        supp_code=supp_code),
                    supp_items)

            # Log results.
            logging.info(
                f"Update SupplierItems: "
                f"{len(bp_changes)} updated.")

    class web_update(CommandBase):
        """
        Sort inventory items into web categories.
        """
        aliases = ["wu", "wupd"]

        def execute(self, options):

            # Import all data related to SupplierItems.
            import_paths = self.config["paths"]["imports"]
            import_data(self.db_session, import_paths, [
                InventoryItem,
                WebMenuItem,
                PriceRule,
                PriceRegionItem,
                InventoryWebDataItem,
            ])

            # Import mappings between PriceRules and WebMenuItems.
            wmi_mappings = import_web_menu_item_mappings(
                import_paths["web_menu_mappings"],
                self.db_session)

            # Select all InventoryWebDataItems that are related to an active
            # InventoryItem and PriceRule, but not a WebMenuItem.
            # pylint:disable=no-member
            iwd_items = self.db_session.query(InventoryWebDataItem).join(
                InventoryWebDataItem.inventory_item
            ).join(
                InventoryItem.price_region_items
            ).filter(
                PriceRegionItem.price_rule_id.isnot(None),
                PriceRegionItem.code == "",
                InventoryWebDataItem.web_menu_item == None,
                InventoryItem.condition != ItemCondition.DISCONTINUED,
                InventoryItem.condition != ItemCondition.INACTIVE,
                InventoryItem.item_type != ItemType.CROSS_REFERENCE,
                InventoryItem.item_type != ItemType.LABOUR,
                InventoryItem.item_type != ItemType.INDENT_ITEM,
            ).all()

            # Update inventory web data and record changes.
            updated_iwd_items = update_product_menu(
                iwd_items, wmi_mappings, self.db_session)

            # Export report and data files:
            # - Inventory web data updates report
            # - Pronto-format web product menu data
            export_paths = self.config["paths"]["exports"]
            export_web_product_menu_data(
                export_paths["web_product_menu_data"],
                updated_iwd_items)
            export_web_data_updates_report(
                export_paths["web_data_updates_report"],
                updated_iwd_items)

            # Log results.
            logging.info(
                f"Update InventoryWebDataItems: "
                f"{len(updated_iwd_items)} updated.")

    class missing_gtin(CommandBase):
        """
        Report on inventory items without a unit GTIN.
        """
        aliases = ["mg", "mgtin"]

        def execute(self, options):

            # Import all data related to GTINItems.
            import_paths = self.config["paths"]["imports"]
            import_data(self.db_session, import_paths, [
                InventoryItem,
                GTINItem,
            ])

            # Select all active, stocked InventoryItems besides those from
            # brands that don't have barcodes.
            # pylint:disable=no-member
            inv_items = self.db_session.query(InventoryItem).join(
                InventoryItem.gtin_items
            ).filter(
                ~InventoryItem.brand.in_(self.config["gtin"]["ignore_brands"]),
                InventoryItem.condition != ItemCondition.DISCONTINUED,
                InventoryItem.condition != ItemCondition.INACTIVE,
                InventoryItem.item_type != ItemType.CROSS_REFERENCE,
                InventoryItem.item_type != ItemType.LABOUR,
                InventoryItem.item_type != ItemType.INDENT_ITEM,
            ).all()

            def is_missing_gtin(inventory_item):
                """
                Checks if InventoryItem is missing a unit barcode.

                Params:
                    inventory_item: The InventoryItem to check.

                Returns:
                    Whether the InventoryItem is missing a gtin.
                """
                for gtin_item in inventory_item.gtin_items:
                    if gtin_item.is_unit_barcode:
                        return False
                return True

            # Select InventoryItems without a unit barcode.
            inv_items_no_gtin = []
            for inv_item in inv_items:
                if is_missing_gtin(inv_item):
                    inv_items_no_gtin.append(inv_item)

            # Select InventoryItems without a unit barcode and stock on hand.
            inv_items_no_gtin_on_hand = []
            for inv_item in inv_items_no_gtin:
                for ws_item in inv_item.warehouse_stock_items:
                    if ws_item.on_hand > 0:
                        inv_items_no_gtin_on_hand.append(inv_item)
                        continue  # Yuck!

            # Export GTIN report to file.
            export_paths = self.config["paths"]["exports"]
            export_gtin_report(
                export_paths["gtin_report"],
                inv_items_no_gtin,
                inv_items_no_gtin_on_hand)

    class fetch_images(CommandBase):
        """
        Download and format images for products.
        """
        aliases = ["fi", "fimg"]

        def execute(self, options):

            # Import all data related to SupplierItems.
            import_paths = self.config["paths"]["imports"]
            import_data(self.db_session, import_paths, [
                InventoryItem,
                SupplierItem,
            ])

            # Get InventoryItems without an image.
            inv_items_no_image = import_missing_images_report(
                import_paths["missing_images_report"], self.db_session)

            # Fetch images for InventoryItems.
            export_paths = self.config["paths"]["exports"]
            fetched_images = fetch_images(
                export_paths["images_dir"], inv_items_no_image)

            # Export report on fetched images.
            export_downloaded_images_report(
                export_paths["missing_images_report"],
                fetched_images)

    class download_spl(CommandBase):
        """
        Download supplier pricelist from remote server.
        """
        aliases = ["dspl"]

        def execute(self, options):

            # Download the file using SCP.
            config = self.config["ssh"]
            src = self.config["paths"]["remote"]["supplier_pricelist"]
            dest = self.config["paths"]["imports"]["supplier_pricelist"]
            if src.startswith("https://"):
                response = requests.get(src)
                with open(dest, "wb") as file:
                    file.write(response.content)
            else:
                download_files(config, [
                    (src, dest)
                ])

            # Log results.
            logging.info(f"Downloaded SPL to {dest}")

    class upload_spls(CommandBase):
        """
        Upload supplier pricelists to remote server.
        """
        aliases = ["uspls"]

        def execute(self, options):

            config = self.config["ssh"]
            src_template = self.config["paths"]["exports"]["supplier_pricelist"]
            dest_template = self.config["paths"]["remote"]["supplier_pricelist_import"]

            # Search for SPL files in the src directory and collect the
            # supplier codes found in those filenames.
            src_dirname = os.path.dirname(src_template)
            src_filename_pattern = os.path.basename(src_template).replace(
                "{supp_code}",
                "([A-Z]{3})"
            )
            supp_codes = []
            for filename in os.listdir(src_dirname):
                matches = re.compile(src_filename_pattern).match(filename)
                if matches is not None:
                    supp_codes.append(matches[1])

            # Upload the SPL for each supplier code.
            upload_files(config, [
                (
                    src_template.format(supp_code=supp_code),
                    dest_template.format(supp_code=supp_code)
                )
                for supp_code in supp_codes
            ])

            # Display a list of uploaded SPLs.
            for supp_code in supp_codes:
                print(f"- {supp_code}")

            # Log the uploads.
            for supp_code in supp_codes:
                logging.info(
                    f"Uploaded {supp_code} SPL.")

    class list_uploaded_spls(CommandBase):
        """
        List supplier pricelists uploaded to remote server.
        """
        aliases = ["luspls"]

        def execute(self, options):
            config = self.config["ssh"]
            filepath_template = (
                self.config["paths"]["remote"]["supplier_pricelist_import"])
            filepath_pattern = filepath_template.replace("{supp_code}", "*")
            filepaths = find_files(config, filepath_pattern)
            print("dir:", os.path.dirname(filepath_template))
            for filepath in filepaths:
                print(os.path.basename(filepath))

    class upload_pricelist(CommandBase):
        """
        Upload pricelist to remote server.
        """
        aliases = ["upl"]

        def execute(self, options):

            # Upload the file using SCP.
            config = self.config["ssh"]
            src = self.config["paths"]["exports"]["pricelist"]
            dest = self.config["paths"]["remote"]["pricelist"]
            upload_files(config, [(src, dest)])
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
