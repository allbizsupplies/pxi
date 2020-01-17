#!/usr/bin/python3

import argparse
import os

# Get the commandline arguments.
parser = argparse.ArgumentParser(
    description="Price Management Helper for Pronto XI.")
parser.add_argument("operation", metavar="operation")
args = parser.parse_args()

# TODO execute operation given as args.operation
# Execute the operation given in the commandline arguments.
if args.operation == "calc:prices":
    pass
else:
    raise ValueError("Invalid operation.")
