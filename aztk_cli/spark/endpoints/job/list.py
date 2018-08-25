import argparse
import typing

import aztk.spark
from aztk_cli import config, utils


def setup_parser(_: argparse.ArgumentParser):
    # No arguments for list yet
    pass


def execute(_: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())

    utils.print_jobs(spark_client.job.list())
