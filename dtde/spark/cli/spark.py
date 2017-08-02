import argparse
import typing

from . import cluster
from . import submit


def setup_parser(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="Actions", dest="action", metavar="<action>")
    subparsers.required = True

    cluster_parser = subparsers.add_parser(
        "cluster", help="Commands to manage a cluster")
    submit_parser = subparsers.add_parser(
        "submit", help="Submit a new spark job")

    cluster.setup_parser(cluster_parser)
    submit.setup_parser(submit_parser)


def execute(args: typing.NamedTuple):
    actions = dict(
        cluster=cluster.execute,
        submit=submit.execute,
    )
    func = actions[args.action]
    func(args)
