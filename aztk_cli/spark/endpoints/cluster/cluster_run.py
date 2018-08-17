import argparse
import typing

import aztk.spark
from aztk_cli import config, utils


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--id", dest="cluster_id", required=True, help="The unique id of your spark cluster")
    parser.add_argument(
        "--node-id",
        "-n",
        dest="node_id",
        required=False,
        help="The unique id of the node in the cluster to run the command on",
    )
    parser.add_argument("command", help="The command to run on your spark cluster")
    parser.add_argument(
        "--internal",
        action="store_true",
        help="Connect using the local IP of the master node. Only use if using a VPN")
    parser.add_argument(
        "--host", action="store_true", help="Run the command on the host instead of the Spark Docker container")
    parser.set_defaults(internal=False, host=False)


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    with utils.Spinner():
        if args.node_id:
            results = [
                spark_client.cluster.node_run(args.cluster_id, args.node_id, args.command, args.host, args.internal)
            ]
        else:
            results = spark_client.cluster.run(args.cluster_id, args.command, args.host, args.internal)
    for node_output in results:
        utils.log_node_run_output(node_output)
