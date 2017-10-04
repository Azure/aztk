import argparse
import typing
from aztk.aztklib import Aztk


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='cluster_id',
                        required=True,
                        help='The unique id of your spark cluster')
    parser.add_argument('--name',
                        dest='app_name',
                        required=True,
                        help='The unique id of your job name')

    parser.add_argument('--tail', dest='tail', action='store_true')


def execute(args: typing.NamedTuple):
    aztk = Aztk()
    cluster_id = args.cluster_id
    app_name = args.app_name
    tail = args.tail
    aztk.job.read_log(cluster_id, app_name, tail=tail)
