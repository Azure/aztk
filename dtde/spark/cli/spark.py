import argparse
import typing

from . import cluster
from . import init

def setup_parser(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="Actions", dest="action", metavar="<action>")
    subparsers.required = True

    cluster_parser = subparsers.add_parser(
        "cluster", help="Commands to manage a cluster")
    init_parser = subparsers.add_parser(
        "init", help="Initialize your environment")

    cluster.setup_parser(cluster_parser)
    init.setup_parser(init_parser)

def execute(args: typing.NamedTuple):
    actions = dict(
        cluster=cluster.execute,
        init=init.execute
    )
    func = actions[args.action]
    func(args)
