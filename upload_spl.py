#!/usr/bin/python
"""
Upload SPL file to Pronto server.
"""
from dotenv import load_dotenv
import os
import pathlib
import sys
from pxi.scp import get_scp_client

REMOTE_FILE = "/home/albbrad/import/supplier_pricelist.csv"
LOCAL_FILE = os.path.join("data", "export", "supplier_pricelist.csv")

load_dotenv()
hostname = os.getenv("PRONTO_HOSTNAME")
username = os.getenv("PRONTO_USERNAME")
password = os.getenv("PRONTO_PASSWORD")
supplier_code = sys.argv[1] if len(sys.argv) >= 2 else ""
scp_client = get_scp_client(hostname, username, password)
scp_client.put(LOCAL_FILE, REMOTE_FILE)
