import argparse
import typing
from aztk.aztklib import Aztk
from aztk import utils


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='cluster_id',
                        required=True,
                        help='The unique id of your spark cluster')


def execute(args: typing.NamedTuple):
    aztk = Aztk()
    cluster_id = args.cluster_id
    cluster = aztk.client.get_cluster(cluster_id)
    utils.print_cluster(aztk.client, cluster)
