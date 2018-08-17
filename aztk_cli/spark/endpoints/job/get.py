import argparse
import typing

import aztk.spark
from aztk_cli import config, utils


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--id", dest="job_id", required=True, help="The unique id of your AZTK job")


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())

    utils.print_job(spark_client, spark_client.job.get(id=args.job_id))
