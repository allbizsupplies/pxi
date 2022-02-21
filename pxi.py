#!/usr/bin/python3

from argparse import ArgumentParser
import sys
import logging
from time import perf_counter
import yaml

from pxi.commands import get_command

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")


def main():
    """
    Loads config, sets logging level and runs command passed as CLI argument.
    """
    # Record start time for logging.
    start_at = perf_counter()

    # Get commandline arguments.
    args = get_args()

    # Load config.
    with open(args.config) as file:
        config = yaml.safe_load(file)

    # Get the command and display an error if it doesn't exist.
    command = get_command(args.command)
    if command is None:
        print("Error: Command does not exist: " + args.command)
        logging.error("Command does not exist: " + args.command)
        return
    command_name = command.__name__

    # Configure logging level and verbosity.
    logging_level = logging.DEBUG if args.debug else logging.INFO
    if args.verbose:
        logging.basicConfig(
            format="%(levelname)s: %(message)s",
            level=logging_level)
    else:
        logging.basicConfig(
            filename=config["paths"]["logging"],
            format=f"%(asctime)s %(levelname)s: {command_name} => %(message)s",
            level=logging_level)

    # Execute the command.
    print(f"pxi: {command_name}")
    logging.info(f"Started")
    command(config)(force_imports=args.force_imports)

    # Log the command execution time.
    duration = (perf_counter() - start_at)
    duration_units = "s"
    if duration < 1:
        duration = duration * 1000
        duration_units = "ms"
    logging.info(f"Completed ({int(duration)}{duration_units})")


def get_args():
    """
    Collects commandline arguments:

    Returns:
        Args namespace with the following attributes:
        - command: the name or alias of the command to be executed.
        - config: the path to the config file. Defaults to "config.yml".
        - debug: flag to increase logging level to logging.DEBUG.
        - verbose: flag to print logs to stdout instead of writing to file.
        - force-imports: flag to force all files to be imported regardless of 
          when last import was completed.
    """
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
