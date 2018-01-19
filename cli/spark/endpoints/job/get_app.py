import argparse
import typing
import time
import aztk.spark
from cli import config
from cli import utils

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='job_id',
                        required=True,
                        help='The unique id of your AZTK job')
    parser.add_argument('--name',
                        dest='app_name',
                        required=True,
                        help='The unique id of your job name')


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_screts())

    utils.print_application(spark_client.get_application(args.job_id, args.app_name))
