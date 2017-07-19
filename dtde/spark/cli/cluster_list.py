import argparse
import typing
from dtde import clusterlib


def setup_parser(_: argparse.ArgumentParser):
    # No arguments for list yet
    pass


def execute(_: typing.NamedTuple):
    clusterlib.list_clusters()
