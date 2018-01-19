import argparse
import typing
import time
import aztk.spark
from cli import config
from cli import utils

def setup_parser(_: argparse.ArgumentParser):
    # No arguments for list yet
    pass

def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_screts())

    utils.print_jobs(spark_client.list_jobs())
