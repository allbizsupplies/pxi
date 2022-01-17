
from unittest.mock import MagicMock, patch

from tests import DatabaseTestCase
from pxi.commands import Commands, get_command


def get_mock_config():
    return {
        "paths": {
            "database": ":memory:",
            "import": {
                "supplier_pricelist": "path/import/supplier_pricelist",
                "pricelist": "path/import/pricelist",
            },
            "export": {
                "supplier_pricelist": "path/export/supplier_pricelist",
                "pricelist": "path/export/pricelist",
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
        }
    }


class CommandTests(DatabaseTestCase):

    def test_get_command(self):
        fixtures = [
            ("download_spl", Commands.download_spl),
            ("download-spl", Commands.download_spl),
            ("dspl", Commands.download_spl),
            ("help", Commands.help),
            ("h", Commands.help),
            ("price_calc", Commands.price_calc),
            ("price-calc", Commands.price_calc),
            ("pc", Commands.price_calc),
            ("upload_pricelist", Commands.upload_pricelist),
            ("upload-pricelist", Commands.upload_pricelist),
            ("upl", Commands.upload_pricelist),
            ("upload_spl", Commands.upload_spl),
            ("upload-spl", Commands.upload_spl),
            ("uspl", Commands.upload_spl),
        ]

        for command_name, expected_command in fixtures:
            self.assertEqual(expected_command, get_command(command_name))

    def test_command_help(self):
        mock_config = get_mock_config()
        command = Commands.help(mock_config)
        command()

    @patch("pxi.commands.get_scp_client")
    def test_command_download_spl(self, mock_get_scp_client):
        mock_config = get_mock_config()
        mock_scp_client = MagicMock()
        mock_get_scp_client.return_value = mock_scp_client
        command = Commands.download_spl(mock_config)()
        mock_get_scp_client.assert_called_with(*mock_config["ssh"].values())
        mock_scp_client.get.assert_called_with(
            mock_config["paths"]["remote"]["supplier_pricelist"],
            mock_config["paths"]["import"]["supplier_pricelist"])

    @patch("pxi.commands.get_scp_client")
    def test_command_upload_spl(self, mock_get_scp_client):
        mock_config = get_mock_config()
        mock_scp_client = MagicMock()
        mock_get_scp_client.return_value = mock_scp_client
        command = Commands.upload_spl(mock_config)()
        mock_get_scp_client.assert_called_with(*mock_config["ssh"].values())
        mock_scp_client.put.assert_called_with(
            mock_config["paths"]["export"]["supplier_pricelist"],
            mock_config["paths"]["remote"]["supplier_pricelist_import"])

    @patch("pxi.commands.get_scp_client")
    def test_command_upload_pricelist(self, mock_get_scp_client):
        mock_config = get_mock_config()
        mock_scp_client = MagicMock()
        mock_get_scp_client.return_value = mock_scp_client
        command = Commands.upload_pricelist(mock_config)()
        mock_get_scp_client.assert_called_with(*mock_config["ssh"].values())
        mock_scp_client.put.assert_called_with(
            mock_config["paths"]["export"]["pricelist"],
            mock_config["paths"]["remote"]["pricelist"])
