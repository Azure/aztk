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


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_screts())

    utils.print_job(spark_client, spark_client.get_job(args.job_id))
