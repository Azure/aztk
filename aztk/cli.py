"""
    AZTK module for the CLI entry point

    Note: any changes to this file need have the package reinstalled
    pip install -e .
"""
import argparse
from typing import NamedTuple
import azure.batch.models.batch_error as batch_error
from aztk import constants, version, logger, log
import aztk.util as util
import aztk.error as error
from aztk.spark.cli import spark
from aztk.models import Software

def main():
    parser = argparse.ArgumentParser(prog=constants.CLI_EXE)

    setup_common_args(parser)

    subparsers = parser.add_subparsers(
        title="Available Softwares", dest="software", metavar="<software>")
    subparsers.required = True
    spark_parser = subparsers.add_parser(
        "spark", help="Commands to run spark jobs")

    spark.setup_parser(spark_parser)
    args = parser.parse_args()

    parse_common_args(args)

    try:
        run_software(args)
    except batch_error.BatchErrorException as e:
        util.print_batch_exception(e)
    except error.AztkError as e:
        log.error(e.message)


def setup_common_args(parser: argparse.ArgumentParser):
    parser.add_argument('--version', action='version',
                        version=version.__version__)
    parser.add_argument("--verbose", action='store_true',
                        help="Enable verbose logging.")


def parse_common_args(args: NamedTuple):
    if args.verbose:
        logger.setup_logging(True)
        log.debug("Verbose logging enabled")
    else:
        logger.setup_logging(False)


def run_software(args: NamedTuple):
    softwares = {}
    softwares[Software.spark] = spark.execute

    func = softwares[args.software]
    func(args)


if __name__ == '__main__':
    main()
