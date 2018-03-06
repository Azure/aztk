import argparse
import typing
import time
import aztk.spark
from aztk_cli import config
from aztk_cli import utils

def setup_parser(_: argparse.ArgumentParser):
    # No arguments for list yet
    pass

def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())

    utils.print_jobs(spark_client.list_jobs())
