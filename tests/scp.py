from random import random
from unittest import TestCase
from unittest.mock import patch

from pxi.scp import get_scp_client
from tests.fakes import random_string


class SCPClientTests(TestCase):

    @patch("pxi.scp.SCPClient")
    @patch("pxi.scp.SSHClient")
    def test_get_scp_client(self, mock_ssh_client_class, mock_scp_client_class):
        hostname = random_string(10)
        username = random_string(10)
        password = random_string(10)
        mock_ssh_client = mock_ssh_client_class.return_value

        scp_client = get_scp_client(hostname, username, password)

        mock_ssh_client_class.assert_called()
        mock_ssh_client.set_missing_host_key_policy.assert_called()
        mock_ssh_client.connect.assert_called_with(
            hostname, username=username, password=password)
        mock_scp_client_class.assert_called_with(
            mock_ssh_client.get_transport.return_value)
        self.assertEqual(scp_client, mock_scp_client_class.return_value)
