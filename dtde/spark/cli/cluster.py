import argparse
import typing
from . import cluster_create
from . import cluster_add_user
from . import cluster_delete
from . import cluster_get
from . import cluster_list
from . import cluster_ssh


class ClusterAction:
    create = "create"
    add_user = "add-user"
    delete = "delete"
    get = "get"
    list = "list"
    ssh = "ssh"


def setup_parser(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="Actions", dest="cluster_action", metavar="<action>")
    subparsers.required = True

    create_parser = subparsers.add_parser(
        ClusterAction.create, help="Create a new cluster")
    add_user_parser = subparsers.add_parser(
        ClusterAction.add_user, help="Add a user to the given cluster")
    delete_parser = subparsers.add_parser(
        ClusterAction.delete, help="Delete a cluster")
    get_parser = subparsers.add_parser(
        ClusterAction.get, help="Get information about a cluster")
    list_parser = subparsers.add_parser(
        ClusterAction.list, help="List clusters in your account")
    ssh_parser = subparsers.add_parser(
        ClusterAction.ssh, help="SSH into the master node of a cluster")

    cluster_create.setup_parser(create_parser)
    cluster_add_user.setup_parser(add_user_parser)
    cluster_delete.setup_parser(delete_parser)
    cluster_get.setup_parser(get_parser)
    cluster_list.setup_parser(list_parser)
    cluster_ssh.setup_parser(ssh_parser)


def execute(args: typing.NamedTuple):
    actions = {}

    actions[ClusterAction.create] = cluster_create.execute
    actions[ClusterAction.add_user] = cluster_add_user.execute
    actions[ClusterAction.delete] = cluster_delete.execute
    actions[ClusterAction.get] = cluster_get.execute
    actions[ClusterAction.list] = cluster_list.execute
    actions[ClusterAction.ssh] = cluster_ssh.execute

    func = actions[args.cluster_action]
    func(args)
