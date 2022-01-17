

from tests import DatabaseTestCase
from pxi.commands import Commands, get_command


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
