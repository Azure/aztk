import argparse
import typing

from . import init
from .cluster import cluster
from .job import job


def setup_parser(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(title="Actions", dest="action", metavar="<action>")
    subparsers.required = True

    cluster_parser = subparsers.add_parser("cluster", help="Commands to manage a cluster")
    job_parser = subparsers.add_parser("job", help="Commands to manage a Job")
    init_parser = subparsers.add_parser("init", help="Initialize your environment")

    cluster.setup_parser(cluster_parser)
    job.setup_parser(job_parser)
    init.setup_parser(init_parser)


def execute(args: typing.NamedTuple):
    actions = dict(cluster=cluster.execute, job=job.execute, init=init.execute)
    func = actions[args.action]
    func(args)
