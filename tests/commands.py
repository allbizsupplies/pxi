
import io
from unittest.mock import call, MagicMock, mock_open, patch

from pxi.config import Config
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
    WebMenuItem)
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
    fake_web_menu_item,
    random_string)


def get_mock_config() -> Config:
    return {
        "paths": {
            "logging": "path/logging",
            "imports": {
                "contract_items_datagrid": "path/import/contract_items_datagrid",
                "inventory_items_datagrid": "path/import/inventory_items_datagrid",
                "inventory_web_data_items_datagrid": "path/import/inventory_web_data_items_datagrid",
                "gtin_items_datagrid": "path/import/gtin_items_datagrid",
                "price_rules_datagrid": "path/import/price_rules_datagrid",
                "supplier_items_datagrid": "path/import/supplier_items_datagrid",
                "pricelist_datagrid": "path/import/pricelist_datagrid",
                "web_menu": "path/import/web_menu",
                "web_menu_mappings": "path/import/web_menu_mappings",
                "supplier_pricelist": "path/import/supplier_pricelist",
                "missing_images_report": "path/import/missing_images_report",
            },
            "exports": {
                "contract_item_task": "path/export/contract_item_task",
                "gtin_report": "path/export/gtin_report",
                "images_dir": "path/export/images_dir",
                "pricelist": "path/export/pricelist",
                "price_changes_report": "path/export/price_changes_report",
                "price_rules_json": "path/export/price_rules_json",
                "product_price_task": "path/export/product_price_task",
                "supplier_pricelist": "path/export/supplier_pricelist_{supp_code}",
                "supplier_price_changes_report": "path/export/supplier_price_changes_report",
                "tickets_list": "path/export/tickets_list",
                "web_product_menu_data": "path/export/web_product_menu_data",
                "web_data_updates_report": "path/export/web_data_updates_report",
                "missing_images_report": "path/export/missing_images_report",
                "downloaded_images_report": "path/export/downloaded_images_report",
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
            Commands.list_uploaded_spls,
            Commands.missing_gtin,
            Commands.price_calc,
            Commands.upload_pricelist,
            Commands.upload_spls,
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
            ("list_uploaded_spls", Commands.list_uploaded_spls),
            ("list-uploaded-spls", Commands.list_uploaded_spls),
            ("luspls", Commands.list_uploaded_spls),
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
            ("upload_spls", Commands.upload_spls),
            ("upload-spls", Commands.upload_spls),
            ("uspls", Commands.upload_spls),
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

    @patch("pxi.commands.download_files")
    def test_command_download_spl_ssh(self, mock_download_files):
        """
        download_spl command downloads supplier pricelist usingn SCP.
        """
        mock_config = get_mock_config()

        Commands.download_spl(mock_config)()

        mock_download_files.assert_called_with(
            mock_config["ssh"],
            [
                (mock_config["paths"]["remote"]["supplier_pricelist"],
                 mock_config["paths"]["imports"]["supplier_pricelist"])
            ])

    @patch("requests.get")
    def test_command_download_spl_https(self, mock_requests_get):
        """
        download_spl command downloads supplier pricelist usingn HTTPS.
        """
        mock_config = get_mock_config()
        mock_config["paths"]["remote"]["supplier_pricelist"] = (
            "https://path/remote/supplier_pricelist")

        with patch("builtins.open", mock_open()) as get_mock_file:
            Commands.download_spl(mock_config)()
            mock_file = get_mock_file()

        mock_requests_get.assert_called_with(
            mock_config["paths"]["remote"]["supplier_pricelist"])
        mock_file.write.assert_called_with(
            mock_requests_get.return_value.content)

    @patch("os.listdir")
    @patch("os.path")
    @patch("pxi.commands.upload_files")
    def test_command_upload_spls(
            self,
            mock_upload_files,
            mock_os_path,
            mock_os_listdir):
        """
        upload_spls command uploads supplier pricelists usingn SCP.
        """
        mock_config = get_mock_config()
        filename = "supplier_pricelist_{supp_code}.csv"
        export_path = f"export/path/{filename}"
        remote_path = f"remote/path/{filename}"
        mock_config["paths"]["exports"]["supplier_pricelist"] = export_path
        mock_config["paths"]["remote"]["supplier_pricelist_import"] = remote_path
        supp_code = random_string(3)
        mock_os_path.dirname.return_value = "export/path"
        mock_os_path.basename.return_value = filename
        mock_os_listdir.return_value = [
            filename.format(supp_code=supp_code),
            random_string(20),
        ]

        Commands.upload_spls(mock_config)()

        mock_os_path.dirname.assert_called_with(export_path)
        mock_os_path.basename.assert_called_with(export_path)
        mock_os_listdir.assert_called_with(mock_os_path.dirname.return_value)
        mock_upload_files.assert_called_with(
            mock_config["ssh"],
            [
                (export_path.format(supp_code=supp_code),
                 remote_path.format(supp_code=supp_code))
            ]
        )

    @patch("pxi.commands.find_files")
    def test_command_list_uploaded_spls(self, mock_find_files):
        """
        list_uploaded_spls command lists SPL files on the remote filesystem.
        """
        mock_config = get_mock_config()
        filename_template = "supplier_pricelist_{supp_code}.csv"
        dirpath = "remote/path"
        filepaths = [
            f"{dirpath}/{filename_template.format(supp_code=random_string(3))}",
            f"{dirpath}/{filename_template.format(supp_code=random_string(3))}",
        ]
        remote_path = f"{dirpath}/{filename_template}"
        mock_config["paths"]["remote"]["supplier_pricelist_import"] = remote_path
        supp_code = random_string(3)
        filepath_pattern = remote_path.replace("{supp_code}", "*")
        mock_find_files.return_value = filepaths

        Commands.list_uploaded_spls(mock_config)()

        mock_find_files.assert_called_with(
            mock_config["ssh"], filepath_pattern)

    @patch("pxi.commands.upload_files")
    def test_command_upload_pricelist(self, mock_upload_files):
        """
        download_spl command uploads pricelist usingn SCP.
        """
        mock_config = get_mock_config()
        mock_scp_client = MagicMock()

        Commands.upload_pricelist(mock_config)()

        mock_upload_files.assert_called_with(
            mock_config["ssh"],
            [
                (mock_config["paths"]["exports"]["pricelist"],
                 mock_config["paths"]["remote"]["pricelist"])
            ])

    @patch("pxi.commands.export_tickets_list")
    @patch("pxi.commands.export_contract_item_task")
    @patch("pxi.commands.export_product_price_task")
    @patch("pxi.commands.export_pricelist")
    @patch("pxi.commands.export_price_changes_report")
    @patch("pxi.commands.recalculate_contract_prices")
    @patch("pxi.commands.recalculate_sell_prices")
    @patch("pxi.commands.import_data")
    def test_command_price_calc(
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
        import_paths = mock_config["paths"]["imports"]
        export_paths = mock_config["paths"]["exports"]

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
        ])
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
    @patch("pxi.commands.remove_exported_supplier_pricelists")
    @patch("pxi.commands.update_supplier_items")
    @patch("pxi.commands.import_supplier_pricelist_items")
    @patch("pxi.commands.import_data")
    def test_command_generate_spl(
            self,
            mock_import_data,
            mock_import_supplier_pricelist_items,
            mock_update_supplier_items,
            mock_remove_exported_supplier_pricelists,
            mock_export_supplier_price_changes_report,
            mock_export_supplier_pricelist):
        """
        generate_spl command imports data, generates SPL, exports reports/data.
        """
        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["imports"]
        export_paths = mock_config["paths"]["exports"]

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
        ])
        mock_import_supplier_pricelist_items.assert_called_with(
            import_paths["supplier_pricelist"])
        mock_update_supplier_items.assert_called_with(
            [spl_item], command.db_session)
        mock_remove_exported_supplier_pricelists.assert_called_with(
            export_paths["supplier_pricelist"])
        mock_export_supplier_price_changes_report.assert_called_with(
            export_paths["supplier_price_changes_report"],
            [price_change])
        mock_export_supplier_pricelist.assert_called_with(
            export_paths["supplier_pricelist"].format(
                supp_code=supp_item.code),
            [supp_item])

    @patch("pxi.commands.export_supplier_pricelist")
    @patch("pxi.commands.export_supplier_price_changes_report")
    @patch("pxi.commands.remove_exported_supplier_pricelists")
    @patch("pxi.commands.update_supplier_items")
    @patch("pxi.commands.import_supplier_pricelist_items")
    @patch("pxi.commands.import_data")
    def test_command_generate_spl_with_multiple_spl_items_per_inv_item(
            self,
            mock_import_data,
            mock_import_supplier_pricelist_items,
            mock_update_supplier_items,
            mock_remove_exported_supplier_pricelists,
            mock_export_supplier_price_changes_report,
            mock_export_supplier_pricelist):
        """
        generate_spl command imports data, generates SPL, exports reports/data.
        """
        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["imports"]
        export_paths = mock_config["paths"]["exports"]

        inv_item_1 = fake_inventory_item()
        inv_item_2 = fake_inventory_item()
        supp_item_1a = fake_supplier_item(inv_item_1)
        supp_item_1b = fake_supplier_item(inv_item_1)
        spl_item_1a = fake_supplier_pricelist_item(supp_item_1a)
        spl_item_1b = fake_supplier_pricelist_item(supp_item_1b)
        bp_change_1a = fake_buy_price_change(supp_item_1a)
        bp_change_1b = fake_buy_price_change(supp_item_1b)
        self.seed([
            inv_item_1,
            supp_item_1a,
            supp_item_1b,
        ])
        spl_items = [spl_item_1a, spl_item_1b]
        bp_changes = [bp_change_1a, bp_change_1b]
        mock_import_supplier_pricelist_items.return_value = spl_items
        mock_update_supplier_items.return_value = bp_changes

        command = Commands.generate_spl(mock_config)
        command.db_session = self.db_session
        command()

        mock_import_data.assert_called_with(command.db_session, import_paths, [
            InventoryItem,
            SupplierItem,
        ])
        mock_import_supplier_pricelist_items.assert_called_with(
            import_paths["supplier_pricelist"])
        mock_update_supplier_items.assert_called_with(
            spl_items, command.db_session)
        mock_remove_exported_supplier_pricelists.assert_called_with(
            export_paths["supplier_pricelist"])
        mock_export_supplier_price_changes_report.assert_called_with(
            export_paths["supplier_price_changes_report"],
            bp_changes)
        mock_export_supplier_pricelist.assert_has_calls([
            call(
                export_paths["supplier_pricelist"].format(
                    supp_code=supp_item_1a.code),
                [supp_item_1a]
            ),
            call(
                export_paths["supplier_pricelist"].format(
                    supp_code=supp_item_1b.code),
                [supp_item_1b]
            ),
        ])

    @patch("pxi.commands.export_web_data_updates_report")
    @patch("pxi.commands.export_web_product_menu_data")
    @patch("pxi.commands.update_product_menu")
    @patch("pxi.commands.import_web_menu_item_mappings")
    @patch("pxi.commands.import_data")
    def test_command_web_update(
            self,
            mock_import_data,
            mock_import_web_menu_item_mappings,
            mock_update_product_menu,
            mock_export_web_product_menu_data,
            mock_export_web_data_updates_report):
        """
        web_update command imports data, sorts items into web categories, 
        exports reports and data.
        """
        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["imports"]
        export_paths = mock_config["paths"]["exports"]

        inv_item = fake_inventory_item()
        price_rule = fake_price_rule()
        pr_item = fake_price_region_item(inv_item, price_rule, {
            "code": PriceRegionItem.DEFAULT_REGION_CODE
        })
        web_menu_item = fake_web_menu_item()
        iwd_item = fake_inv_web_data_item(inv_item, None)
        self.seed([
            inv_item,
            price_rule,
            pr_item,
            web_menu_item,
            iwd_item,
        ])
        wmi_mappings = {
            price_rule.code: web_menu_item,
        }
        mock_import_web_menu_item_mappings.return_value = wmi_mappings
        mock_update_product_menu.return_value = [iwd_item]

        command = Commands.web_update(mock_config)
        command.db_session = self.db_session
        command()

        mock_import_data.assert_called_with(command.db_session, import_paths, [
            InventoryItem,
            WebMenuItem,
            PriceRule,
            PriceRegionItem,
            InventoryWebDataItem,
        ])
        mock_import_web_menu_item_mappings.assert_called_with(
            import_paths["web_menu_mappings"],
            command.db_session)
        mock_update_product_menu.assert_called_with(
            [iwd_item],
            wmi_mappings,
            command.db_session)
        mock_export_web_product_menu_data.assert_called_with(
            export_paths["web_product_menu_data"],
            [iwd_item])
        mock_export_web_data_updates_report.assert_called_with(
            export_paths["web_data_updates_report"],
            [iwd_item])

    @patch("pxi.commands.export_gtin_report")
    @patch("pxi.commands.import_data")
    def test_command_missing_gtin(
            self,
            mock_import_data,
            mock_export_gtin_report):
        """
        missing_gtin command imports data, reports items missing GTIN.
        """
        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["imports"]
        export_paths = mock_config["paths"]["exports"]

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
        ])
        mock_export_gtin_report.assert_called_with(
            export_paths["gtin_report"], [inv_item], [])

    @patch("pxi.commands.export_downloaded_images_report")
    @patch("pxi.commands.fetch_images")
    @patch("pxi.commands.import_missing_images_report")
    @patch("pxi.commands.import_data")
    def test_command_fetch_images(
            self,
            mock_import_data,
            mock_import_missing_images_report,
            mock_fetch_images,
            mock_export_downloaded_images_report):
        """
        fetch_images command downloads images, reports on images.
        """

        mock_config = get_mock_config()
        import_paths = mock_config["paths"]["imports"]
        export_paths = mock_config["paths"]["exports"]

        inv_item = fake_inventory_item()
        supp_item = fake_supplier_item(inv_item)
        self.seed([
            inv_item,
            supp_item,
        ])
        mock_import_missing_images_report.return_value = [inv_item]

        command = Commands.fetch_images(mock_config)
        command.db_session = self.db_session
        command()

        mock_import_data.assert_called_with(command.db_session, import_paths, [
            InventoryItem,
            SupplierItem,
        ])
        mock_import_missing_images_report.assert_called_with(
            import_paths["missing_images_report"],
            command.db_session)
        mock_fetch_images.assert_called_with(
            export_paths["images_dir"],
            [inv_item])
        mock_export_downloaded_images_report.assert_called_with(
            export_paths["missing_images_report"],
            mock_fetch_images.return_value)
