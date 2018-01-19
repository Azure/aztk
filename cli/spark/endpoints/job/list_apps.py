import argparse
import typing
import aztk.spark
from cli import config
from cli import utils

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='job_id',
                        required=True,
                        help='The unique id of your AZTK job')


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_screts())
    utils.print_applications(spark_client.list_applications(args.job_id))
