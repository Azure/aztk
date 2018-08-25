import argparse
import typing

import aztk.spark
from aztk_cli import config, log


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--id", dest="job_id", required=True, help="The unique id of your AZTK job")


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    spark_client.job.stop(args.job_id)
    log.print("Stopped Job {0}".format(args.job_id))
