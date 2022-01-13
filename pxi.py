#!/usr/bin/python3

from argparse import ArgumentParser
import sys
import logging
from time import perf_counter
import yaml

from pxi.commands import Commands, get_command

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")


def main():
    start_at = perf_counter()
    args = get_args()
    with open(args.config) as file:
        config = yaml.safe_load(file)
    # Configure logging.
    logging_level = logging.DEBUG if args.debug else logging.INFO
    if args.verbose:
        logging.basicConfig(
            format="%(levelname)s: %(message)s",
            level=logging_level)
    else:
        logging.basicConfig(
            filename=config["paths"]["logging"],
            format="%(asctime)s %(levelname)s: %(message)s",
            level=logging_level)
    try:
        command_name = args.command.replace("-", "_")
        command = get_command(command_name)
        logging.info(f"Command: {args.command}")
        command(config)(
            force_imports=args.force_imports)
        duration = (perf_counter() - start_at) * 1000
        logging.info(f"{args.command} ({int(duration)}ms)")
    except AttributeError as ex:
        print("Error: Command does not exist: " + args.command)
        logging.error("Command does not exist: " + args.command)


def get_args():
    parser = ArgumentParser()
    parser.add_argument("command",
                        help="the command to execute")
    parser.add_argument("--config",
                        help="path to config",
                        default="config.yml")
    parser.add_argument("--debug",
                        help="print debugging logs",
                        dest="debug", action="store_true")
    parser.add_argument("--verbose",
                        help="print logs to terminal",
                        dest="verbose", action="store_true")
    parser.add_argument("--force-imports",
                        help="force all data to be imported",
                        dest="force_imports", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
