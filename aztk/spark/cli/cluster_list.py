import argparse
import typing
from aztk.aztklib import Aztk


def setup_parser(_: argparse.ArgumentParser):
    # No arguments for list yet
    pass


def execute(_: typing.NamedTuple):
    aztk = Aztk()
    clusters = aztk.cluster.list_clusters()
    aztk.cluster.print_clusters(clusters)
