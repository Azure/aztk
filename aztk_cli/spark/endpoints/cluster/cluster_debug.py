import argparse
import os
import typing
import time

import aztk.spark
from aztk_cli import config, utils


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id', dest='cluster_id', required=True,
                        help='The unique id of your spark cluster')

    parser.add_argument('--output', '-o', required=False,
                        help='the directory for the output folder')


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    timestr = time.strftime("%Y%m%d-%H%M%S")

    if not args.output:
        args.output = os.path.join(os.getcwd(), "debug-{0}-{1}".format(args.cluster_id, timestr))
    with utils.Spinner():
        spark_client.run_cluster_diagnostics(cluster_id=args.cluster_id, output_directory=args.output)
    # TODO: analyze results, display some info about status
