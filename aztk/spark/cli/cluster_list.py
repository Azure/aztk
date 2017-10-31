import argparse
import typing
from aztk.aztklib import Aztk
from aztk import utils


def setup_parser(_: argparse.ArgumentParser):
    # No arguments for list yet
    pass


def execute(_: typing.NamedTuple):
    aztk = Aztk()
    clusters = aztk.client.list_clusters()
    utils.print_clusters(clusters)
