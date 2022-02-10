import csv
from datetime import date
from decimal import Decimal
import os
import pathlib
from unittest.mock import mock_open, patch
from pxi.models import InventoryItem
import random

from pxi.enum import WebStatus
from pxi.exporters import (
    export_downloaded_images_report,
    export_price_changes_report,
    export_pricelist,
    export_product_price_task,
    export_contract_item_task,
    export_supplier_pricelist,
    export_supplier_price_changes_report,
    export_tickets_list,
    export_web_data_updates_report,
    export_web_product_menu_data)
from pxi.price_calc import recalculate_sell_prices
from pxi.spl_update import SPL_FIELDNAMES
from tests import PXITestCase
from tests.fakes import (
    fake_buy_price_change,
    fake_contract_item,
    fake_inv_item_image_file,
    fake_inv_web_data_item,
    fake_inventory_item,
    fake_price_region_item,
    fake_price_rule,
    fake_sell_price_change,
    fake_supplier_item,
    fake_supplier_pricelist_item,
    fake_warehouse_stock_item,
    fake_web_menu_item,
    random_string)


def delete_temporary_file(filepath):
    try:
        os.remove(filepath)
    except PermissionError:
        return


class ExporterTests(PXITestCase):

    @patch("csv.writer")
    def test_export_pricelist(self, mock_csvwrtr_class):
        """
        Export Pronto pricelist.
        """
        filepath = random_string(20)
        pr_item = fake_price_region_item(
            fake_inventory_item(), fake_price_rule())
        mock_csvwrtr = mock_csvwrtr_class.return_value

        with patch("builtins.open", mock_open()):
            export_pricelist(filepath, [pr_item])
        mock_csvwrtr = mock_csvwrtr_class.return_value
        mock_csvwrtr.writerows.assert_called_once()

    @patch("pxi.exporters.ReportWriter")
    def test_export_price_changes_report(self, mock_rprtwrtr_class):
        """
        Export price updates to XLSX report.
        """
        filepath = random_string(20)
        sp_change = fake_sell_price_change(
            fake_price_region_item(fake_inventory_item(), fake_price_rule()))
        mock_rprtwrtr = mock_rprtwrtr_class.return_value

        export_price_changes_report(filepath, [sp_change])

        mock_rprtwrtr_class.assert_called_with(filepath)
        self.assertEqual(mock_rprtwrtr.write_sheet.call_count, 2)
        write_sheet_args_list = mock_rprtwrtr.write_sheet.call_args_list
        self.assertEqual(write_sheet_args_list[0][0][0], "Price Changes")
        self.assertEqual(write_sheet_args_list[1][0][0], "Contract Changes")

    @patch("pxi.exporters.ReportWriter")
    def test_export_supplier_price_changes_report(self, mock_rprtwrtr_class):
        """
        Export supplier price updates to XLSX report.
        """
        filepath = random_string(20)
        bp_change = fake_buy_price_change(
            fake_price_region_item(fake_inventory_item(), fake_price_rule()))
        mock_rprtwrtr = mock_rprtwrtr_class.return_value

        export_supplier_price_changes_report(filepath, [bp_change])

        mock_rprtwrtr_class.assert_called_with(filepath)
        mock_rprtwrtr.write_sheet.assert_called_once()
        write_sheet_args_list = mock_rprtwrtr.write_sheet.call_args_list
        self.assertEqual(write_sheet_args_list[0][0][0], "Price Changes")

    @patch("pxi.exporters.ReportWriter")
    def test_export_downloaded_images_report(self, mock_rprtwrtr_class):
        """
        Export downloaded images report to file.
        """
        filepath = random_string(20)
        iii_file = fake_inv_item_image_file(fake_inventory_item())
        mock_rprtwrtr = mock_rprtwrtr_class.return_value

        export_downloaded_images_report(filepath, [iii_file])

        mock_rprtwrtr_class.assert_called_with(filepath)
        mock_rprtwrtr.write_sheet.assert_called_once()

    @patch("pxi.exporters.ReportWriter")
    def test_export_web_data_updates_report(self, mock_rprtwrtr_class):
        """
        Export web data updates to file.
        """
        filepath = random_string(20)
        iwd_item = fake_inv_web_data_item(
            fake_inventory_item(), fake_web_menu_item())
        mock_rprtwrtr = mock_rprtwrtr_class.return_value

        export_web_data_updates_report(filepath, [iwd_item])

        mock_rprtwrtr_class.assert_called_with(filepath)
        mock_rprtwrtr.write_sheet.assert_called_once()

    @patch("csv.DictWriter")
    def test_export_product_price_task(self, mock_csvwrtr_class):
        """
        Export product price update task to file.
        """
        filepath = random_string(20)
        pr_item = fake_price_region_item(
            fake_inventory_item(), fake_price_rule())
        mock_csvwrtr = mock_csvwrtr_class.return_value

        with patch("builtins.open", mock_open()):
            export_product_price_task(filepath, [pr_item])

        mock_csvwrtr.writeheader.assert_called()
        mock_csvwrtr.writerows.assert_called()

    @patch("csv.DictWriter")
    def test_export_contract_item_task(self, mock_csvwrtr_class):
        """
        Export contract item task to file.
        """
        filepath = random_string(20)
        con_item = fake_contract_item(fake_inventory_item())
        mock_csvwrtr = mock_csvwrtr_class.return_value

        with patch("builtins.open", mock_open()):
            export_contract_item_task(filepath, [con_item])

        mock_csvwrtr.writeheader.assert_called()
        mock_csvwrtr.writerows.assert_called()

    def test_export_tickets_list(self):
        """
        Export tickets list to file.
        """
        filepath = random_string(20)
        ws_item = fake_warehouse_stock_item(fake_inventory_item())

        with patch("builtins.open", mock_open()) as get_mock_file:
            export_tickets_list(filepath, [ws_item])
            mock_file = get_mock_file()

        mock_file.writelines.assert_called_with([
            f"{ws_item.inventory_item.code}\n",
        ])

    @patch("csv.DictWriter")
    def test_export_supplier_pricelist(self, mock_csvwrtr_class):
        """
        Export supplier pricelist to CSV file.
        """
        filepath = random_string(20)
        supp_item = fake_supplier_item(fake_inventory_item())
        mock_csvwrtr = mock_csvwrtr_class.return_value

        with patch("builtins.open", mock_open()) as get_mock_file:
            export_supplier_pricelist(filepath, [])

        mock_csvwrtr.writerows.assert_called()

    @patch("csv.DictWriter")
    def test_export_web_product_menu_data(self, mock_csvwrtr_class):
        """
        Export inventory web data to file.
        """
        filepath = random_string(20)
        iwd_item = fake_inv_web_data_item(
            fake_inventory_item(), fake_web_menu_item())
        mock_csvwrtr = mock_csvwrtr_class.return_value

        with patch("builtins.open", mock_open()) as get_mock_file:
            export_web_product_menu_data(filepath, [iwd_item])
            mock_file = get_mock_file()

        mock_csvwrtr.writerows.assert_called()
