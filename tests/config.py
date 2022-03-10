
from unittest.mock import patch, mock_open

from pxi.config import load_config
from tests import PXITestCase
from tests.fakes import random_string


class ConfigTests(PXITestCase):

    @patch("yaml.safe_load")
    def test_load_config(self, mock_yaml_safe_load):
        """
        Loads config from yaml file.
        """
        filename = random_string(20)

        with patch("builtins.open", mock_open()) as mock_get_file_handler:
            result = load_config(filename)
            mock_file = mock_get_file_handler()

        mock_yaml_safe_load.assert_called_with(mock_file)
        self.assertEqual(result, mock_yaml_safe_load.return_value)
