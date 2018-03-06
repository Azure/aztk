import argparse
import typing
import aztk
from aztk_cli import log
from aztk_cli import utils, config


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='cluster_id',
                        required=True,
                        help='The unique id of your spark cluster')
    parser.add_argument('--show-config',
                        dest='show_config',
                        action='store_true',
                        help='Show the cluster configuration')


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    cluster_id = args.cluster_id
    cluster = spark_client.get_cluster(cluster_id)
    utils.print_cluster(spark_client, cluster)

    configuration = utils.helpers.read_cluster_config(cluster_id, spark_client.blob_client)
    if configuration and args.show_config:
        log.info("-------------------------------------------")
        log.info("Cluster configuration:")
        utils.print_cluster_conf(configuration, False)
