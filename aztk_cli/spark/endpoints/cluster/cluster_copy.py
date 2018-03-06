import argparse
import typing
import aztk.spark
from aztk_cli import config


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id', dest='cluster_id', required=True,
                        help='The unique id of your spark cluster')

    parser.add_argument('--source-path', required=True,
                        help='the local file you wish to copy to the cluster')

    parser.add_argument('--dest-path', required=True,
                        help='the path the file will be copied to on each node in the cluster.'\
                             'Note that this must include the file name.')


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())

    spark_client.cluster_copy(
        cluster_id=args.cluster_id,
        source_path=args.source_path,
        destination_path=args.dest_path
    )
