#!/usr/bin/python
"""
Download SPL file from Pronto server.
"""
from dotenv import load_dotenv
import os
import sys
from pxi.scp import get_scp_client

REMOTE_FILE = "/oclimport/supplierpricelist/SPL{}.PRN"
LOCAL_FILE = "data/import/supplier_pricelist.csv"

load_dotenv()
hostname = os.getenv("PRONTO_HOSTNAME")
username = os.getenv("PRONTO_USERNAME")
password = os.getenv("PRONTO_PASSWORD")
supplier_code = sys.argv[1] if len(sys.argv) >= 2 else ""
scp_client = get_scp_client(hostname, username, password)
scp_client.get(REMOTE_FILE.format(supplier_code), LOCAL_FILE)

# Convert GNS SPL to SAT SPL
if supplier_code == "SAT":
    with open(LOCAL_FILE, "r") as file:
        lines = file.readlines()
    new_lines = [line.replace("GNS", "SAT") for line in lines]
    with open(LOCAL_FILE, "w") as file:
        file.writelines(new_lines)