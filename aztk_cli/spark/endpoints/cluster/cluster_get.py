import argparse
import typing

import aztk
from aztk_cli import config, log, utils


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--id", dest="cluster_id", required=True, help="The unique id of your spark cluster")
    parser.add_argument("--show-config", dest="show_config", action="store_true", help="Show the cluster configuration")
    parser.add_argument(
        "--internal",
        action="store_true",
        help="Show the local IP of the nodes. "
        "Only use if using connecting with a VPN.",
    )
    parser.set_defaults(internal=False)


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    cluster_id = args.cluster_id
    cluster = spark_client.cluster.get(cluster_id)
    utils.print_cluster(spark_client, cluster, args.internal)

    if args.show_config:
        configuration = spark_client.cluster.get_configuration(cluster_id)
        if configuration:
            log.info("-------------------------------------------")
            log.info("Cluster configuration:")
            utils.print_cluster_conf(configuration, False)
