import argparse
import typing

import aztk.spark
from aztk_cli import config, log


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--id", dest="job_id", required=True, help="The unique id of your AZTK job")
    parser.add_argument("--name", dest="app_name", required=True, help="The unique id of your job name")


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())

    if spark_client.job.stop_application(args.job_id, args.app_name):
        log.info("Stopped app %s", args.app_name)
    else:
        log.error("App with name %s does not exist or was already deleted", args.app_name)
