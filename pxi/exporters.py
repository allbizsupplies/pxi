import csv
from datetime import date
from decimal import Decimal
import logging
from os import PathLike
from typing import Dict, List

from pxi.dataclasses import BuyPriceChange, InventoryItemImageFile, SellPriceChange
from pxi.models import (
    ContractItem,
    InventoryItem,
    InventoryWebDataItem,
    PriceRegionItem,
    SupplierItem,
    WarehouseStockItem)
from pxi.report import NumberField, ReportWriter, StringField
from pxi.spl_update import SPL_FIELDNAMES


def export_pricelist(
        filepath: PathLike,
        pr_items: List[PriceRegionItem]):
    """
    Export pricelist to file.

    Params: 
        filepath: The path to the file.
        pr_items: List of PriceRegionItems to be exported.
    """
    # Assume the effective date of the pricelist is the current date.
    effective_date = date.today().strftime("%d-%b-%Y")
    price_list_field = "0"  # I have no idea what this does.
    last_change_date = ""   # Last change date is left empty.
    reason_code = ""        # Reason code is left empty.
    price_type_code = ""    # Price type is left empty.

    def price_region_item_to_row(pr_item: PriceRegionItem):
        """
        Makes a pricelist row from a PriceRegionItem.

        Params:
            price_region_item: The PriceRegionItem to convert.

        Returns:
            The pricelist row.
        """
        return [
            pr_item.inventory_item.code,
            pr_item.code,
            str(pr_item.price_0),
            str(pr_item.quantity_1),
            str(pr_item.quantity_2),
            str(pr_item.quantity_3),
            str(pr_item.quantity_4),
            str(pr_item.price_1),
            str(pr_item.price_2),
            str(pr_item.price_3),
            str(pr_item.price_4),
            str(pr_item.rrp_excl_tax),
            str(pr_item.rrp_incl_tax),
            price_list_field,
            last_change_date,
            effective_date,
            price_type_code,
            reason_code,
        ]

    # Write pricelist CSV to file.
    with open(filepath, "w", newline="") as file:
        csv.writer(file).writerows(
            [price_region_item_to_row(pr_item) for pr_item in pr_items])


def export_price_changes_report(
        filepath: PathLike,
        sp_changes: List[SellPriceChange]):
    """
    Export report to file.

    Params:
        filepath: The path to the report.
        sp_changes: List of SellPriceCHanges to export.
    """

    def sp_change_row(sp_change: SellPriceChange):
        """
        Makes a price change report row from a SellPriceChange.

        Params:
            sp_change: The SellPriceChange to convert.

        Returns:
            The report row.
        """
        price_region_item = sp_change.price_region_item
        price_diffs = sp_change.price_diffs
        inventory_item = price_region_item.inventory_item
        price_rule = price_region_item.price_rule
        row = {
            "item_code": inventory_item.code,
            "region": price_region_item.code,
            "brand": inventory_item.brand,
            "apn": inventory_item.apn,
            "description": inventory_item.full_description,
            "price_rule": price_rule.code
        }
        for level in range(PriceRegionItem.PRICE_LEVELS):
            if level > 0:
                row[f"quantity_{level}"] = price_region_item.quantity(level)
            price_now = price_region_item.price(level)
            price_diff = price_diffs[level]
            price_was = price_now - price_diff
            price_diff_percentage = None
            if price_was > 0:
                price_diff_percentage = (
                    price_diff / price_was).quantize(price_now)
            row[f"price_{level}_was"] = price_now - price_diff
            row[f"price_{level}_now"] = price_now
            row[f"price_{level}_diff"] = price_diff
            row[f"price_{level}_diff_percentage"] = price_diff_percentage
        return row

    def contract_item_row(con_item: ContractItem, price_diff: Decimal):
        """
        Makes a row for a ContractItem.

        Params:
            con_item: The ContractItem to convert.
            price_diff: The price difference amount to include in the row.

        Returns:
            The report row.
        """
        inv_item = con_item.inventory_item
        pr_item = inv_item.default_price_region_item
        price_now = pr_item.price(0)
        price_was = price_now - price_diff
        price_diff_percentage = None
        if price_was > 0:
            price_diff_percentage = (
                price_diff / price_was).quantize(price_now)
        row = {
            "contract": con_item.code,
            "item_code": inv_item.code,
            "description": inv_item.full_description,
            "retail_price": pr_item.price(0),
            "retail_price_diff": price_diff,
            "retail_price_diff_percentage": price_diff_percentage,
        }
        for level in range(1, ContractItem.PRICE_LEVELS + 1):
            row[f"price_{level}"] = con_item.price(level)
        return row

    def contract_item_rows(sp_changes: List[SellPriceChange]):
        """
        Makes rows for ContractItems that are related to a SellPriceChange.

        Params:
            sp_changes: List of SellPriceChanges, possibly related to one or 
                more ContractItems.

        Returns:
            List of report rows.
        """
        rows = []
        for sp_change in sp_changes:
            pr_item = sp_change.price_region_item
            con_items = pr_item.inventory_item.contract_items
            if con_items:
                # Make row for each ContractItem.
                for con_item in con_items:
                    price_diff = sp_change.price_diffs[0]
                    rows.append(contract_item_row(con_item, price_diff))
        return rows

    # Define fields for price changes report sheet.
    sp_change_fields = [
        StringField("item_code", "Item Code", 20),
        StringField("region", "Region", 4),
        StringField("brand", "Brand", 7),
        StringField("apn", "APN", 20),
        StringField("description", "Description", 80),
        StringField("price_rule", "Price Rule", 7),
    ]
    for level in range(PriceRegionItem.PRICE_LEVELS):
        if level > 0:
            sp_change_fields.append(NumberField(
                f"quantity_{level}", f"Quantity {level}", number_format="0"))
        sp_change_fields.append(NumberField(
            f"price_{level}_was", f"Price {level} Was"))
        sp_change_fields.append(NumberField(
            f"price_{level}_now", f"Price {level} Now"))
        sp_change_fields.append(NumberField(
            f"price_{level}_diff", f"Price {level} Diff"))
        sp_change_fields.append(NumberField(
            f"price_{level}_diff_percentage", f"Price {level} Diff %",
            number_format="0%"))

    # Define fields for contract item changes report sheet.
    con_item_fields = [
        StringField("contract", "Contract", 20),
        StringField("item_code", "Item Code", 20),
        StringField("description", "Description", 80),
        NumberField("retail_price", "Retail Price"),
        NumberField("retail_price_diff", "Price Diff"),
        NumberField("retail_price_diff_percentage", "Price Diff %",
                    number_format="0%"),
    ]
    for level in range(1, 7):
        con_item_fields.append(NumberField(
            f"price_{level}", f"Price {level}"))

    # Create the report sheets and write the report to file.
    report_writer = ReportWriter(filepath)
    report_writer.write_sheet(
        "Price Changes",
        sp_change_fields,
        [sp_change_row(sp_change) for sp_change in sp_changes])
    report_writer.write_sheet(
        "Contract Changes",
        con_item_fields,
        contract_item_rows(sp_changes))
    report_writer.save()


def export_supplier_price_changes_report(
        filepath: PathLike,
        bp_changes: List[BuyPriceChange]):
    """
    Export supplier price report to file.

    Params:
        filepath: The path to the report.
        bp_changes: List of BuyPriceChanges to export.
    """

    # Define fields for price changes report sheet.
    bp_change_fields = [
        StringField("item_code", "Item Code", 20),
        StringField("supplier", "Supplier", 8),
        StringField("brand", "Brand", 7),
        StringField("apn", "APN", 20),
        StringField("description", "Description", 80),
        NumberField("price_was", "Price Was", number_format="0.00"),
        NumberField("price_now", "Price Now", number_format="0.00"),
        NumberField("price_diff", "Price Diff", number_format="0.00"),
        NumberField("price_diff_percentage",
                    "Price Diff %", number_format="0%"),
    ]

    def bp_change_row(bp_change: BuyPriceChange):
        """
        Makes a price change report row from a BuyPriceChange.

        Params:
            bp_change: The BuyPriceChange to convert.

        Returns:
            The report row.
        """
        supp_item = bp_change.supplier_item
        inv_item = supp_item.inventory_item
        row = {
            "item_code": inv_item.code,
            "supplier": supp_item.code,
            "brand": inv_item.brand,
            "apn": inv_item.apn,
            "description": inv_item.full_description,
            "price_was": bp_change.price_was,
            "price_now": bp_change.price_now,
            "price_diff": bp_change.price_diff,
            "price_diff_percentage": bp_change.price_diff_percentage,
        }
        return row

    # Create the report sheet and write the report to file.
    report_writer = ReportWriter(filepath)
    report_writer.write_sheet(
        "Price Changes",
        bp_change_fields,
        [bp_change_row(bp_change) for bp_change in bp_changes])
    report_writer.save()


def export_downloaded_images_report(
        filepath: PathLike,
        image_files: List[InventoryItemImageFile]):
    """
    Export supplier price report to file.

    Params:
        filepath: The path to the report.
        downloaded_images: The data for downloaded images.
    """

    def downloaded_images_row(image_file: InventoryItemImageFile):
        """
        Makes a downloaded images report row from image information.

        Params:
            image_data: The image data to convert.

        Returns:
            The report row.
        """
        return {
            "item_code": image_file.inventory_item.code,
            "filename": image_file.filename,
        }

    # Define fields for the downloaded images report.
    downloaded_images_fields = [
        StringField("item_code", "Item Code", 20),
        StringField("filename", "Filename", 40),
    ]

    # Create report sheet and write report to file.
    report_writer = ReportWriter(filepath)
    report_writer.write_sheet(
        "Downloaded Images",
        downloaded_images_fields,
        [downloaded_images_row(image_file) for image_file in image_files])
    report_writer.save()


def export_gtin_report(
        filepath: PathLike,
        inv_items_no_gtin: List[InventoryItem],
        inv_items_no_gtin_on_hand: List[InventoryItem]):
    """
    Export list of missing GTINItems to file, including second report sheet
    showing which items are in stock.

    Params:
        filepath: The path to the report.
        inv_items_missing_gtin: List of InventoryItems with no GTINItems.
        inv_items_on_hand: List of InventoryItems with stock on hand.
    """

    def missing_gtin_row(inv_item: InventoryItem):
        """
        Makes a missing GTINs report row from an InventoryItem.

        Params:
            inv_item: The InventoryItem to convert.

        Returns:
            The report row.
        """
        return {
            "item_code": inv_item.code,
            "brand": inv_item.brand,
            "apn": inv_item.apn,
            "description": inv_item.full_description,
        }

    # Define fields for the missing GTINs report.
    missing_gtin_fields = [
        StringField("item_code", "Item Code", 20),
        StringField("brand", "Brand", 8),
        StringField("apn", "APN", 20),
        StringField("description", "Description", 80),
    ]

    # Create report sheets and write report to file.
    report_writer = ReportWriter(filepath)
    report_writer.write_sheet(
        "Missing GTIN",
        missing_gtin_fields,
        [missing_gtin_row(inv_item) for inv_item in inv_items_no_gtin])
    report_writer.write_sheet(
        "Missing GTIN and on hand",
        missing_gtin_fields,
        [missing_gtin_row(inv_item) for inv_item in inv_items_no_gtin_on_hand])
    report_writer.save()


def export_web_data_updates_report(
        filepath: PathLike,
        iwd_items: List[InventoryWebDataItem]):
    """
    Export web data updates report to file.

    Params:
        filepath: The path to the report.
        web_product_menu_data_updates: List of InventoryItems with updated
            InventoryWebDataItems.
    """

    def updated_item_row(iwd_item: InventoryWebDataItem):
        """
        Makes a web data updates report row from an InventoryItem.

        Params:
            inv_item: The InventoryItem to convert.

        Returns:
            The report row.
        """
        inv_item = iwd_item.inventory_item
        return {
            "item_code": inv_item.code,
            "brand": inv_item.brand,
            "apn": inv_item.apn,
            "description": inv_item.full_description,
            "menu_parent_name": iwd_item.web_sortcode.parent_name,
            "menu_child_name": iwd_item.web_sortcode.child_name,
        }

    # Define fields for the web data updates report.
    updated_item_fields = [
        StringField("item_code", "Item Code", 20),
        StringField("brand", "Brand", 7),
        StringField("apn", "APN", 20),
        StringField("description", "Description", 80),
        StringField("menu_parent_name", "Menu Parent", 40),
        StringField("menu_child_name", "Menu Child", 40),
    ]

    # Create report sheet and write report to file.
    report_writer = ReportWriter(filepath)
    report_writer.write_sheet(
        "Product Menu Updates",
        updated_item_fields,
        [updated_item_row(iwd_item) for iwd_item in iwd_items])
    report_writer.save()


def export_product_price_task(
        filepath: PathLike,
        pr_items: List[PriceRegionItem]):
    """
    Exports product price update task to file.

    Params:
        filepath: The path to the task file.
        pr_items: List of PriceRegionItems to export.
    """

    def price_region_item_to_row(pr_item: PriceRegionItem):
        """
        Makes a task row from a PriceRegionItem.

        Params:
            inv_item: The PriceRegionItem to convert.

        Returns:
            The task row.
        """
        inv_item = pr_item.inventory_item
        row = {
            "item_code": inv_item.code,
            "region": pr_item.code,
        }
        for level in range(PriceRegionItem.PRICE_LEVELS):
            fieldname = f"price_{level}"
            row[fieldname] = pr_item.price(level)
        return row

    # Define fieldnames for the price update task.
    fieldnames = [
        "item_code",
        "region"
    ] + [
        f"price_{level}" for level in range(PriceRegionItem.PRICE_LEVELS)
    ]

    # Write task data to CSV file.
    with open(filepath, "w") as file:
        writer = csv.DictWriter(file, fieldnames, dialect="excel-tab")
        writer.writeheader()
        writer.writerows(
            [price_region_item_to_row(pr_item) for pr_item in pr_items])


def export_contract_item_task(
        filepath: PathLike,
        con_items: List[ContractItem]):
    """
    Exports product price update task to file.

    Params:
        filepath: The path to the task file.
        con_items: List of ContractItems to export.
    """

    def contract_item_to_row(con_item: ContractItem):
        """
        Makes a task row from a ContractItem.

        Params:
            inv_item: The ContractItem to convert.

        Returns:
            The task row.
        """
        inventory_item = con_item.inventory_item
        row = {
            "contract": con_item.code,
            "item_code": inventory_item.code,
        }
        for level in range(1, ContractItem.PRICE_LEVELS + 1):
            fieldname = f"price_{level}"
            row[fieldname] = con_item.price(level)
        return row

    # Define fieldnames for the price update task.
    fieldnames = ["contract", "item_code"]

    # Write task data to CSV file.
    with open(filepath, "w") as file:
        for level in range(1, ContractItem.PRICE_LEVELS + 1):
            fieldnames.append(f"price_{level}")
        writer = csv.DictWriter(file, fieldnames, dialect="excel-tab")
        writer.writeheader()
        writer.writerows(
            [contract_item_to_row(con_item) for con_item in con_items])


def export_supplier_pricelist(
        filepath: PathLike,
        supp_items: List[SupplierItem]):
    """
    Export supplier items to Pronto SPL file.

    Params:
        filepath: The path to the pricelist file.
        supp_items: List of SupplierItems to export.
    """

    seen_item_codes = {}  # Item codes already added to rows.
    duplicates = {}       # Rows with a duplicate item code.

    def supplier_item_to_row(supp_item: SupplierItem):
        """
        Makes a pricelist row from a SupplierItem.

        Params:
            inv_item: The SupplierItem to convert.

        Returns:
            The pricelist row.
        """
        item_code = supp_item.item_code
        if item_code not in seen_item_codes:
            seen_item_codes.add(item_code)
        else:
            duplicates.add(item_code)
        inventory_item = supp_item.inventory_item
        row = {
            "supplier_code": supp_item.code,
            "supp_item_code": supp_item.item_code,
            "desc_line_1": inventory_item.description_line_1,
            "desc_line_2": inventory_item.description_line_2,
            "supp_uom": supp_item.uom,
            "supp_eoq": supp_item.moq,
            "supp_conv_factor": supp_item.conv_factor,
            "supp_price_1": supp_item.buy_price,
            "item_code": inventory_item.code,
        }
        return row

    # Log duplicates that will be overridden during import.
    if len(duplicates) > 0:
        logging.warn(
            f"Export SPL: {len(duplicates)} will be overridden on import.")

    # Write pricelist to CSV file.
    with open(filepath, "w") as file:
        fieldnames = SPL_FIELDNAMES
        writer = csv.DictWriter(file, fieldnames, dialect="excel")
        writer.writerows(
            [supplier_item_to_row(item) for item in supp_items])


def export_tickets_list(
        filepath: PathLike,
        ws_items: List[WarehouseStockItem]):
    """
    Export tickets list to file.

    Params:
        filepath: The path to the tickets file.
        ws_items: List of WarehouseStockItems to export.
    """

    # Write a list of item codes to a plain text file.
    lines = [f"{ws_item.inventory_item.code}\n" for ws_item in ws_items]
    with open(filepath, "w") as file:
        file.writelines(lines)


def export_web_product_menu_data(
        filepath: PathLike,
        iwd_items: List[InventoryWebDataItem]):
    """
    Export Pronto web menu data file.

    Params:
        filepath: The path to the tickets file.
        ws_items: List of InventoryItems to export.
    """

    def inventory_item_to_row(iwd_item: InventoryWebDataItem):
        """
        Make data row from InventoryWebDataItem.

        Params:
            iwd_item: The InventoryWebDataItem to convert.

        Returns:
            The data row.
        """
        return {
            "item_code": iwd_item.inventory_item.code,
            "menu_name": iwd_item.web_sortcode.name,
        }

    # Define fieldnames for the CSV file.
    fieldnames = [
        "item_code",
        "menu_name",
    ]

    # Write data to CSV file.
    with open(filepath, "w", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames, delimiter="|", quoting=csv.QUOTE_NONE)
        writer.writerows(
            [inventory_item_to_row(iwd_item) for iwd_item in iwd_items])
