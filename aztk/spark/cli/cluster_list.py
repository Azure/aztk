import argparse
import typing
from aztk import clusterlib


def setup_parser(_: argparse.ArgumentParser):
    # No arguments for list yet
    pass


def execute(_: typing.NamedTuple):
    clusters = clusterlib.list_clusters()
    clusterlib.print_clusters(clusters)
