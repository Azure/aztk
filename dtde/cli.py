"""
    DTDE module for the CLI entry point

    Note: any changes to this file need have the package reinstalled
    pip install -e .
"""
import argparse
from dtde import constants
from dtde.spark.cli import spark
from dtde.models import Software

def main():
    parser = argparse.ArgumentParser(prog=constants.CLI_EXE)
    subparsers = parser.add_subparsers(
        title="Available Softwares", dest="software", metavar="<software>")
    subparsers.required = True
    spark_parser = subparsers.add_parser(
        "spark", help="Commands to run spark jobs")

    spark.setup_parser(spark_parser)
    args = parser.parse_args()

    softwares = {}
    softwares[Software.spark] = spark.execute

    func = softwares[args.software]
    func(args)


if __name__ == '__main__':
    main()
