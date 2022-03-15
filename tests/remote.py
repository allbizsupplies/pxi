from random import random
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from pxi.remote import (
    download_files,
    get_scp_client,
    get_ssh_client,
    find_files,
    remove_files,
    upload_files)
from tests.fakes import random_string


class RemoteTests(TestCase):

    @patch("pxi.remote.SSHClient")
    def test_get_ssh_client(self, mock_ssh_client_class):
        ssh_config = {
            "hostname": random_string(20),
            "username": random_string(20),
            "password": random_string(20),
        }
        mock_ssh_client = mock_ssh_client_class.return_value

        ssh_client = get_ssh_client(ssh_config)

        mock_ssh_client_class.assert_called()
        mock_ssh_client.set_missing_host_key_policy.assert_called()
        mock_ssh_client.connect.assert_called_with(
            ssh_config["hostname"],
            username=ssh_config["username"],
            password=ssh_config["password"])
        self.assertEqual(ssh_client, mock_ssh_client_class.return_value)

    @patch("pxi.remote.SCPClient")
    @patch("pxi.remote.get_ssh_client")
    def test_get_scp_client(self, mock_get_ssh_client, mock_scp_client_class):
        ssh_config = {
            "hostname": random_string(20),
            "username": random_string(20),
            "password": random_string(20),
        }
        mock_ssh_client = mock_get_ssh_client.return_value

        scp_client = get_scp_client(ssh_config)

        mock_get_ssh_client.assert_called_with(ssh_config)
        mock_scp_client_class.assert_called_with(
            mock_ssh_client.get_transport.return_value)
        self.assertEqual(scp_client, mock_scp_client_class.return_value)

    @patch("pxi.remote.get_scp_client")
    def test_upload_files(self, mock_get_scp_client):
        ssh_config = {
            "hostname": random_string(20),
            "username": random_string(20),
            "password": random_string(20),
        }
        files = [
            (random_string(10), random_string(10)),
        ]
        mock_scp_client = mock_get_scp_client.return_value

        upload_files(ssh_config, files)

        mock_get_scp_client.assert_called_with(ssh_config)
        mock_scp_client.put.assert_has_calls([
            call(src, dest) for src, dest in files])

    @patch("pxi.remote.get_scp_client")
    def test_download_files(self, mock_get_scp_client):
        ssh_config = {
            "hostname": random_string(20),
            "username": random_string(20),
            "password": random_string(20),
        }
        files = [
            (random_string(10), random_string(10)),
        ]
        mock_scp_client = mock_get_scp_client.return_value

        download_files(ssh_config, files)

        mock_get_scp_client.assert_called_with(ssh_config)
        mock_scp_client.get.assert_has_calls([
            call(src, dest) for src, dest in files])

    @patch("pxi.remote.SSHClient")
    def test_remove_files(self, mock_ssh_client_class):
        ssh_config = {
            "hostname": random_string(20),
            "username": random_string(20),
            "password": random_string(20),
        }
        filepaths = [
            random_string(10),
        ]
        mock_ssh_client = mock_ssh_client_class.return_value

        remove_files(ssh_config, filepaths)

        mock_ssh_client_class.assert_called()
        mock_ssh_client.set_missing_host_key_policy.assert_called()
        mock_ssh_client.connect.assert_called_with(**ssh_config)
        mock_ssh_client.exec_command.assert_has_calls([
            call(f"rm {filepath}") for filepath in filepaths])

    @patch("pxi.remote.SSHClient")
    def test_find_files(self, mock_ssh_client_class):
        dirpath = random_string(20)
        filename_pattern = f"{random_string(20)}_*.csv"
        filepath_pattern = f"{dirpath}/{filename_pattern}"
        filenames = [
            filename_pattern.replace("*", random_string(3)),
            filename_pattern.replace("*", random_string(3)),
        ]
        ssh_config = {
            "hostname": random_string(20),
            "username": random_string(20),
            "password": random_string(20),
        }
        mock_ssh_client = mock_ssh_client_class.return_value
        mock_ssh_stdout = MagicMock()
        mock_ssh_stdout.readlines.return_value = filenames
        mock_ssh_client.exec_command.return_value = (
            None, mock_ssh_stdout, None)

        result = find_files(ssh_config, filepath_pattern)

        mock_ssh_client_class.assert_called()
        mock_ssh_client.set_missing_host_key_policy.assert_called()
        mock_ssh_client.connect.assert_called_with(**ssh_config)
        mock_ssh_client.exec_command.assert_called_with(
            f"find {dirpath} -iname \"{filename_pattern}\"")
        self.assertEqual(result, filenames)
