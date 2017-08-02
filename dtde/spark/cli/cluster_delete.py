import argparse
import typing
from dtde import clusterlib, log


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='cluster_id',
                        required=True,
                        help='The unique id of your spark cluster')


def execute(args: typing.NamedTuple):
    cluster_id = args.cluster_id
    if clusterlib.delete_cluster(cluster_id):
        log.info("Deleting cluster %s", cluster_id)
    else:
        log.info("Cluster with id '%s' doesn't exists or was already deleted.", cluster_id)
