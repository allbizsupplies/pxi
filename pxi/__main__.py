
import argparse
import os
from pxi.operations import operations
import sys

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

# Get the commandline arguments.
parser = argparse.ArgumentParser(
    description="Price Management Helper for Pronto XI.")
parser.add_argument("operation", metavar="operation")
args = parser.parse_args()

# Execute the operation given in the commandline arguments.
operation = getattr(operations, args.operation)
operation()
