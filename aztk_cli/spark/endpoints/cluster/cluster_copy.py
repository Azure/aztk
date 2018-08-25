import argparse
import sys
import typing

import aztk.spark
from aztk_cli import config, utils


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--id", dest="cluster_id", required=True, help="The unique id of your spark cluster")

    parser.add_argument("--source-path", required=True, help="the local file you wish to copy to the cluster")

    parser.add_argument(
        "--dest-path",
        required=True,
        help="the path the file will be copied to on each node in the cluster."
        "Note that this must include the file name.",
    )
    parser.add_argument(
        "--internal",
        action="store_true",
        help="Connect using the local IP of the master node. Only use if using a VPN.",
    )
    parser.set_defaults(internal=False)


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    with utils.Spinner():
        copy_output = spark_client.cluster.copy(
            id=args.cluster_id, source_path=args.source_path, destination_path=args.dest_path, internal=args.internal)
    for node_output in copy_output:
        utils.log_node_copy_output(node_output)
    sys.exit(0 if not any([node_output.error for node_output in copy_output]) else 1)
