import argparse
import typing
from aztk import clusterlib


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='cluster_id',
                        required=True,
                        help='The unique id of your spark cluster')


def execute(args: typing.NamedTuple):
    cluster_id = args.cluster_id
    cluster = clusterlib.get_cluster(cluster_id)
    clusterlib.print_cluster(cluster)
