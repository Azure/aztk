import argparse
import typing

from . import cluster
from . import submit
from . import app


def setup_parser(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="Actions", dest="action", metavar="<action>")
    subparsers.required = True

    cluster_parser = subparsers.add_parser(
        "cluster", help="Commands to manage a cluster")
    app_parser = subparsers.add_parser(
        "app", help="Action on an app")

    cluster.setup_parser(cluster_parser)
    app.setup_parser(app_parser)


def execute(args: typing.NamedTuple):
    actions = dict(
        cluster=cluster.execute,
        app=app.execute,
    )
    func = actions[args.action]
    func(args)
