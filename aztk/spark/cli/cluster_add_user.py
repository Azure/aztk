import argparse
import typing
from aztk import log
from aztk.aztklib import Aztk

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
    aztk = Aztk()
    log.info('-------------------------------------------')
    log.info('spark cluster id:    {}'.format(args.cluster_id))
    log.info('username:            {}'.format(args.username))
    log.info('-------------------------------------------')
    password, ssh_key = aztk.cluster.create_user(
        args.cluster_id,
        args.username,
        args.password,
        args.ssh_key)

    if password:
        log.info('password:            %s', password)
    elif ssh_key:
        log.info('ssh public key:      %s', ssh_key)

    log.info('-------------------------------------------')
