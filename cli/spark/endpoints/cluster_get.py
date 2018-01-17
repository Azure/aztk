import argparse
import typing
import aztk
from cli import utils, config


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='cluster_id',
                        required=True,
                        help='The unique id of your spark cluster')


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_screts())
    cluster_id = args.cluster_id
    cluster = spark_client.get_cluster(cluster_id)
    utils.print_cluster(spark_client, cluster)
