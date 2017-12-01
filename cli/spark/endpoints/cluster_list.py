import argparse
import typing
from cli.spark.aztklib import load_spark_client
from cli import utils


def setup_parser(_: argparse.ArgumentParser):
    # No arguments for list yet
    pass


def execute(_: typing.NamedTuple):
    spark_client = load_spark_client()
    clusters = spark_client.list_clusters()
    utils.print_clusters(clusters)
