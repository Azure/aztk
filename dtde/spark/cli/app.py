import argparse
import typing

from . import submit
from . import app_logs


def setup_parser(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="Actions", dest="app_action", metavar="<app_action>")
    submit_parser = subparsers.add_parser(
        "submit", help="Submit a new spark job")
    logs_parser = subparsers.add_parser(
        "logs", help="Action on an app")

    submit.setup_parser(submit_parser)
    app_logs.setup_parser(logs_parser)


def execute(args: typing.NamedTuple):
    actions = dict(
        submit=submit.execute,
        logs=app_logs.execute,
    )
    func = actions[args.app_action]
    func(args)
