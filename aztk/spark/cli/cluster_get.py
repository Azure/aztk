import argparse
import typing
from aztk.aztklib import Aztk

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='cluster_id',
                        required=True,
                        help='The unique id of your spark cluster')


def execute(args: typing.NamedTuple):
    aztk = Aztk()
    cluster_id = args.cluster_id
    cluster = aztk.cluster.get_cluster(cluster_id)
    aztk.cluster.print_cluster(cluster)
