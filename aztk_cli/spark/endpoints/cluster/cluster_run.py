import argparse
import typing
import aztk.spark
from aztk_cli import utils, config

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='cluster_id',
                        required=True,
                        help='The unique id of your spark cluster')
    parser.add_argument('command',
                        help='The command to run on your spark cluster')

def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    result = spark_client.cluster_run(args.cluster_id, args.command)
    #TODO: pretty print result
