
import io
from unittest.mock import MagicMock, patch

from pxi.commands import Commands, commands, get_command
from pxi.enum import ItemCondition, ItemType
from pxi.models import (
    ContractItem,
    GTINItem,
    InventoryItem,
    InventoryWebDataItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem,
    WebSortcode)
from tests import DatabaseTestCase
from tests.fakes import (
    fake_contract_item,
    fake_gtin_item,
    fake_inv_web_data_item,
    fake_inventory_item,
    fake_buy_price_change,
    fake_price_region_item,
    fake_price_rule,
    fake_sell_price_change,
    fake_supplier_item,
    fake_supplier_pricelist_item,
    fake_warehouse_stock_item,
    fake_web_sortcode)


def get_mock_config():
    return {
        "paths": {
            "database": ":memory:",
            "import": {
                "inventory_metadata": "path/import/inventory_metadata",
                "pricelist": "path/import/pricelist",
                "supplier_pricelist": "path/import/supplier_pricelist",
                "website_images_report": "path/import/website_images_report",
            },
            "export": {
                "contract_item_task": "path/export/contract_item_task",
                "gtin_report": "path/export/gtin_report",
                "images_dir": "path/export/images_dir",
                "pricelist": "path/export/pricelist",
                "price_changes_report": "path/export/price_changes_report",
                "product_price_task": "path/export/product_price_task",
                "supplier_pricelist": "path/export/supplier_pricelist",
                "supplier_price_changes_report": "path/export/supplier_price_changes_report",
                "tickets_list": "path/export/tickets_list",
                "web_product_menu_data": "path/export/web_product_menu_data",
                "web_data_updates_report": "path/export/web_data_updates_report",
                "website_images_report": "path/export/website_images_report",
            },
            "remote": {
                "pricelist": "path/remote/pricelist",
                "supplier_pricelist": "path/remote/supplier_pricelist",
                "supplier_pricelist_import": "path/remote/supplier_pricelist_import",
            }
        },
        "ssh": {
            "hostname": "pronto.example.com",
            "username": "prontousername",
            "password": "prontopassword",
        },
        "price_rules": {
            "ignore": [
                "NA",
            ]
        },
        "bin_locations": {
            "ignore": [
                "IGNORED",
            ]
        },
        "gtin": {
            "ignore_brands": [
                "IGN",
            ]
        }
    }


class CommandTests(DatabaseTestCase):

    def test_commands_generator(self):
        """
        Generates a list of command classes.
        """
        expected_commands = [
            Commands.download_spl,
            Commands.fetch_images,
            Commands.generate_spl,
            Commands.help,
            Commands.missing_gtin,
            Commands.price_calc,
            Commands.upload_pricelist,
            Commands.upload_spl,
            Commands.web_update,
        ]

        self.assertEqual(
            list(commands()),
            expected_commands)

    def test_get_command(self):
        """
        Gets a command given its class name or one of its aliases.
        """
        fixtures = [
            ("download_spl", Commands.download_spl),
            ("download-spl", Commands.download_spl),
            ("dspl", Commands.download_spl),
            ("help", Commands.help),
            ("h", Commands.help),
            ("missing_gtin", Commands.missing_gtin),
            ("missing-gtin", Commands.missing_gtin),
            ("mg", Commands.missing_gtin),
            ("mgtin", Commands.missing_gtin),
            ("price_calc", Commands.price_calc),
            ("price-calc", Commands.price_calc),
            ("pc", Commands.price_calc),
            ("upload_pricelist", Commands.upload_pricelist),
            ("upload-pricelist", Commands.upload_pricelist),
            ("upl", Commands.upload_pricelist),
            ("upload_spl", Commands.upload_spl),
            ("upload-spl", Commands.upload_spl),
            ("uspl", Commands.upload_spl),
            ("generate_spl", Commands.generate_spl),
            ("generate-spl", Commands.generate_spl),
            ("gspl", Commands.generate_spl),
            ("web_update", Commands.web_update),
            ("web-update", Commands.web_update),
            ("wu", Commands.web_update),
            ("wupd", Commands.web_update),
            ("fetch_images", Commands.fetch_images),
            ("fetch-images", Commands.fetch_images),
            ("fi", Commands.fetch_images),
            ("fimg", Commands.fetch_images),
        ]

        for command_name, expected_command in fixtures:
            self.assertEqual(expected_command, get_command(command_name))

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_command_help(self, mock_stdout):
        """
        Prints a list of commands.
        """
        mock_config = get_mock_config()
        Commands.help(mock_config)()
        printed_lines = mock_stdout.getvalue().split("\n")
        self.assertEqual(printed_lines[1], "Available commands:")
        for index, command in enumerate(commands()):
            line = printed_lines[index + 3]
            self.assertIn(command.__name__, line)
            self.assertIn(command.__doc__.strip(), line)

    @patch("pxi.commands.get_scp_client")
    def test_command_download_spl(self, mock_get_scp_client):
        """
        download_spl command downloads supplier pricelist usingn SCP.
        """
        mock_config = get_mock_config()
        mock_scp_client = MagicMock()
        mock_get_scp_client.return_value = mock_scp_client

        Commands.download_spl(mock_config)()

        mock_get_scp_client.assert_called_with(*mock_config["ssh"].values())
        mock_scp_client.get.assert_called_with(
            mock_config["paths"]["remote"]["supplier_pricelist"],
            mock_config["paths"]["import"]["supplier_pricelist"])

    @patch("pxi.commands.get_scp_client")
    def test_command_upload_spl(self, mock_get_scp_client):
        """
        download_spl command uploads supplier pricelist usingn SCP.
        """
        mock_config = get_mock_config()
        mock_scp_client = MagicMock()
        mock_get_scp_client.return_value = mock_scp_client

        Commands.upload_spl(mock_config)()

        mock_get_scp_client.assert_called_with(*mock_config["ssh"].values())
        mock_scp_client.put.assert_called_with(
            mock_config["paths"]["export"]["supplier_pricelist"],
            mock_config["paths"]["remote"]["supplier_pricelist_import"])

    @patch("pxi.commands.get_scp_client")
    def test_command_upload_pricelist(self, mock_get_scp_client):
        """
        download_spl command uploads pricelist usingn SCP.
        """
        mock_config = get_mock_config()
        mock_scp_client = MagicMock()
        mock_get_scp_client.return_value = mock_scp_client

        Commands.upload_pricelist(mock_config)()

        mock_get_scp_client.assert_called_with(*mock_config["ssh"].values())
        mock_scp_client.put.assert_called_with(
            mock_config["paths"]["export"]["pricelist"],
            mock_config["paths"]["remote"]["pricelist"])

    @patch("pxi.commands.export_tickets_list")
    @patch("pxi.commands.export_contract_item_task")
    @patch("pxi.commands.export_product_price_task")
    @patch("pxi.commands.export_pricelist")
    @patch("pxi.commands.export_price_changes_report")
    @patch("pxi.commands.recalculate_contract_prices")
    @patch("pxi.commands.recalculate_sell_prices")
    @patch("pxi.commands.import_data")
    def test_price_calc(
            self,
            mock_import_data,
            mock_recalculate_sell_prices,
            mock_recalculate_contract_prices,
            mock_export_price_changes_report,
            mock_export_pricelist,
            mock_export_product_price_task,
            mock_export_contract_item_task,
            mock_export_tickets_list):
        """
        price_calc command imports data, calculates prices, exports 
        reports/data.
        """
        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["import"]
        export_paths = mock_config["paths"]["export"]

        inv_item = fake_inventory_item()
        con_item = fake_contract_item(inv_item)
        ws_item = fake_warehouse_stock_item(inv_item)
        price_rule = fake_price_rule()
        pr_item = fake_price_region_item(inv_item, price_rule, {
            "code": "",
        })
        price_change = fake_sell_price_change(pr_item)
        mock_recalculate_sell_prices.return_value = [price_change]
        mock_recalculate_contract_prices.return_value = [con_item]
        self.seed([
            inv_item,
            con_item,
            ws_item,
            price_rule,
            pr_item,
        ])

        command = Commands.price_calc(mock_config)
        command.db_session = self.db_session
        command()

        mock_import_data.assert_called_with(command.db_session, import_paths, [
            InventoryItem,
            WarehouseStockItem,
            PriceRule,
            PriceRegionItem,
            ContractItem,
        ], force_imports=False)
        mock_recalculate_sell_prices.assert_called_with(
            [pr_item], command.db_session)
        mock_recalculate_contract_prices.assert_called_with(
            [price_change], command.db_session)
        mock_export_price_changes_report.assert_called_with(
            export_paths["price_changes_report"],
            [price_change])
        mock_export_pricelist.assert_called_with(
            export_paths["pricelist"],
            [pr_item])
        mock_export_product_price_task.assert_called_with(
            export_paths["product_price_task"],
            [pr_item])
        mock_export_contract_item_task.assert_called_with(
            export_paths["contract_item_task"],
            [con_item])
        mock_export_tickets_list.assert_called_with(
            export_paths["tickets_list"],
            [ws_item])

    @patch("pxi.commands.export_supplier_pricelist")
    @patch("pxi.commands.export_supplier_price_changes_report")
    @patch("pxi.commands.update_supplier_items")
    @patch("pxi.commands.import_supplier_pricelist_items")
    @patch("pxi.commands.import_data")
    def test_generate_spl(
            self,
            mock_import_data,
            mock_import_supplier_pricelist_items,
            mock_update_supplier_items,
            mock_export_supplier_price_changes_report,
            mock_export_supplier_pricelist):
        """
        generate_spl command imports data, generates SPL, exports reports/data.
        """
        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["import"]
        export_paths = mock_config["paths"]["export"]

        inv_item = fake_inventory_item()
        supp_item = fake_supplier_item(inv_item)
        spl_item = fake_supplier_pricelist_item(supp_item)
        price_change = fake_buy_price_change(supp_item)
        self.seed([
            inv_item,
            supp_item,
        ])
        mock_import_supplier_pricelist_items.return_value = [spl_item]
        mock_update_supplier_items.return_value = [price_change]

        command = Commands.generate_spl(mock_config)
        command.db_session = self.db_session
        command()

        mock_import_data.assert_called_with(command.db_session, import_paths, [
            InventoryItem,
            SupplierItem,
        ], force_imports=False)
        mock_import_supplier_pricelist_items.assert_called_with(
            import_paths["supplier_pricelist"])
        mock_update_supplier_items.assert_called_with(
            [spl_item], command.db_session)
        mock_export_supplier_price_changes_report.assert_called_with(
            export_paths["supplier_price_changes_report"],
            [price_change])
        mock_export_supplier_pricelist.assert_called_with(
            export_paths["supplier_pricelist"],
            [supp_item])

    @patch("pxi.commands.export_web_data_updates_report")
    @patch("pxi.commands.export_web_product_menu_data")
    @patch("pxi.commands.update_product_menu")
    @patch("pxi.commands.import_web_sortcode_mappings")
    @patch("pxi.commands.import_data")
    def test_web_update(
            self,
            mock_import_data,
            mock_import_web_sortcode_mappings,
            mock_update_product_menu,
            mock_export_web_product_menu_data,
            mock_export_web_data_updates_report):
        """
        web_update command imports data, sorts items into web categories, 
        exports reports and data.
        """
        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["import"]
        export_paths = mock_config["paths"]["export"]

        inv_item = fake_inventory_item()
        price_rule = fake_price_rule()
        pr_item = fake_price_region_item(inv_item, price_rule, {
            "code": PriceRegionItem.DEFAULT_REGION_CODE
        })
        web_sortcode = fake_web_sortcode()
        iwd_item = fake_inv_web_data_item(inv_item, None)
        self.seed([
            inv_item,
            price_rule,
            pr_item,
            web_sortcode,
            iwd_item,
        ])
        wsc_mappings = {
            price_rule.code: web_sortcode,
        }
        mock_import_web_sortcode_mappings.return_value = wsc_mappings
        mock_update_product_menu.return_value = [iwd_item]

        command = Commands.web_update(mock_config)
        command.db_session = self.db_session
        command()

        mock_import_data.assert_called_with(command.db_session, import_paths, [
            InventoryItem,
            WebSortcode,
            PriceRule,
            PriceRegionItem,
            InventoryWebDataItem,
        ], force_imports=False)
        mock_import_web_sortcode_mappings.assert_called_with(
            import_paths["inventory_metadata"],
            command.db_session,
            worksheet_name="rules")
        mock_update_product_menu.assert_called_with(
            [iwd_item],
            wsc_mappings,
            command.db_session)
        mock_export_web_product_menu_data.assert_called_with(
            export_paths["web_product_menu_data"],
            [iwd_item])
        mock_export_web_data_updates_report.assert_called_with(
            export_paths["web_data_updates_report"],
            [iwd_item])

    @patch("pxi.commands.export_gtin_report")
    @patch("pxi.commands.import_data")
    def test_missing_gtin(
            self,
            mock_import_data,
            mock_export_gtin_report):
        """
        missing_gtin command imports data, reports items missing GTIN.
        """
        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["import"]
        export_paths = mock_config["paths"]["export"]

        inv_item = fake_inventory_item()
        gtin_item = fake_gtin_item(inv_item, {
            "gtin": "NOT A BARCODE",
        })
        self.seed([
            inv_item,
            gtin_item,
        ])

        command = Commands.missing_gtin(mock_config)
        command.db_session = self.db_session
        command()

        mock_import_data.assert_called_with(command.db_session, import_paths, [
            InventoryItem,
            GTINItem,
        ], force_imports=False)
        mock_export_gtin_report.assert_called_with(
            export_paths["gtin_report"], [inv_item], [])

    @patch("pxi.commands.export_downloaded_images_report")
    @patch("pxi.commands.fetch_images")
    @patch("pxi.commands.import_website_images_report")
    @patch("pxi.commands.import_data")
    def test_fetch_images(
            self,
            mock_import_data,
            mock_import_website_images_report,
            mock_fetch_images,
            mock_export_downloaded_images_report):
        """
        fetch_images command downloads images, reports on images.
        """

        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["import"]
        export_paths = mock_config["paths"]["export"]

        inv_item = fake_inventory_item()
        supp_item = fake_supplier_item(inv_item)
        self.seed([
            inv_item,
            supp_item,
        ])
        mock_import_website_images_report.return_value = [
            (inv_item, None)]

        command = Commands.fetch_images(mock_config)
        command.db_session = self.db_session
        command()

        mock_import_data.assert_called_with(command.db_session, import_paths, [
            InventoryItem,
            SupplierItem,
        ], force_imports=False)
        mock_import_website_images_report.assert_called_with(
            import_paths["website_images_report"],
            command.db_session)
        mock_fetch_images.assert_called_with(
            export_paths["images_dir"],
            [inv_item])
        mock_export_downloaded_images_report.assert_called_with(
            export_paths["website_images_report"],
            mock_fetch_images.return_value)
