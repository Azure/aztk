import argparse
import typing

import aztk
from aztk_cli import config, utils


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-q", "--quiet", dest="quiet", required=False, action="store_true", help="The unique id of your spark cluster")
    parser.set_defaults(quiet=False)


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    clusters = spark_client.cluster.list()
    if args.quiet:
        utils.print_clusters_quiet(clusters)
    else:
        utils.print_clusters(clusters)
