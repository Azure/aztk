import argparse
import typing
from cli.spark.aztklib import load_spark_client
from cli import utils


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='cluster_id',
                        required=True,
                        help='The unique id of your spark cluster')


def execute(args: typing.NamedTuple):
    spark_client = load_spark_client()
    cluster_id = args.cluster_id
    cluster = spark_client.get_cluster(cluster_id)
    utils.print_cluster(spark_client, cluster)
