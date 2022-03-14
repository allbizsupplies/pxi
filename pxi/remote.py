from paramiko import AutoAddPolicy, SSHClient
from scp import SCPClient  # type: ignore
from typing import List, Tuple

from pxi.config import SSHConfig


def upload_files(paths: List[Tuple[str, str]], ssh_config: SSHConfig):
    scp_client = get_scp_client(ssh_config)
    for src, dest in paths:
        scp_client.put(src, dest)


def download_files(paths: List[Tuple[str, str]], ssh_config: SSHConfig):
    scp_client = get_scp_client(ssh_config)
    for src, dest in paths:
        scp_client.get(src, dest)


def remove_files(paths: List[str], ssh_config: SSHConfig):
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    ssh_client.connect(**ssh_config)
    for path in paths:
        ssh_client.exec_command(f"rm {path}")


def get_scp_client(ssh_config: SSHConfig):
    ssh_client = get_ssh_client(ssh_config)
    scp_client = SCPClient(ssh_client.get_transport())
    return scp_client


def get_ssh_client(ssh_config: SSHConfig):
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    ssh_client.connect(
        ssh_config["hostname"],
        username=ssh_config["username"],
        password=ssh_config["password"])
    return ssh_client
