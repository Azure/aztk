import argparse
import typing
from dtde import clusterlib


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id', dest='cluster_id', required=True,
                        help='The unique id of your spark cluster')
    parser.add_argument('-u', '--username',
                        help='The usernameto access your spark cluster\'s head node')
    parser.add_argument('-p', '--password',
                        help='The password to access your spark cluster\'s head node')
    parser.set_defaults(username="admin", password="pass123!")


def execute(args: typing.NamedTuple):
    print('-------------------------------------------')
    print('spark cluster id:    {}'.format(args.cluster_id))
    print('username:            {}'.format(args.username))
    print('password:            {}'.format(args.password))
    print('-------------------------------------------')
    clusterlib.create_user(
        args.cluster_id,
        args.username,
        args.password)
