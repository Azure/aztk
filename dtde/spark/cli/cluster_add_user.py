import argparse
import typing
from dtde import clusterlib


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id', dest='cluster_id', required=True,
                        help='The unique id of your spark cluster')
    parser.add_argument('-u', '--username',
                        help='The usernameto access your spark cluster\'s head node')

    auth_group = parser.add_mutually_exclusive_group()
    auth_group.add_argument('-p', '--password',
                            help="The password to access your spark cluster's master node. If not provided will use ssh public key.")
    auth_group.add_argument('--ssh-key',
                            help="The ssh public key to access your spark cluster's master node. You can also set the ssh-key in the configuration file.")
    parser.set_defaults(username="admin")


def execute(args: typing.NamedTuple):
    print('-------------------------------------------')
    print('spark cluster id:    {}'.format(args.cluster_id))
    print('username:            {}'.format(args.username))

    password, ssh_key = clusterlib.create_user(
        args.cluster_id,
        args.username,
        args.password,
        args.ssh_key)

    if password:
        print('password:            {}'.format(password))
    elif ssh_key:
        print('ssh public key:      {}'.format(ssh_key))

    print('-------------------------------------------')
