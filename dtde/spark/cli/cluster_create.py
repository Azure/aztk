import argparse
import typing
from dtde import clusterlib, util


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id', dest='cluster_id', required=True,
                        help='The unique id of your spark cluster')

    # Make --size and --size-low-pri mutually exclusive until there is a fix for
    # having clusters with mixed priority types
    size_group = parser.add_mutually_exclusive_group(required=True)
    size_group.add_argument('--size', type=int,
                            help='Number of vms in your cluster')
    size_group.add_argument('--size-low-pri', type=int,
                            help='Number of low priority vms in your cluster')
    parser.add_argument('--vm-size', required=True,
                        help='VM size for nodes in your cluster')
    parser.add_argument('--custom-script',
                        help='Absolute path of custom bash script (.sh) to run on each node')
    parser.add_argument('--username',
                        help='Username to access your cluster (required: --wait flag)')
    parser.add_argument('--password',
                        help='Password to access your cluster (required: --wait flag)')
    parser.add_argument('--no-wait', dest='wait', action='store_false')
    parser.add_argument('--wait', dest='wait', action='store_true')
    parser.set_defaults(wait=False, size=0, size_low_pri=0)


def execute(args: typing.NamedTuple):
    print('-------------------------------------------')
    print('spark cluster id:        {}'.format(args.cluster_id))
    print('spark cluster size:      {}'.format(args.size + args.size_low_pri))
    print('>        dedicated:      {}'.format(args.size))
    print('>     low priority:      {}'.format(args.size_low_pri))
    print('spark cluster vm size:   {}'.format(args.vm_size))
    print('path to custom script:   {}'.format(args.custom_script))
    print('wait for cluster:        {}'.format(args.wait))
    print('username:                {}'.format(args.username))
    print('password:                {}'.format(args.password))
    print('-------------------------------------------')

    # create spark cluster
    clusterlib.create_cluster(
        args.custom_script,
        args.cluster_id,
        args.size,
        args.size_low_pri,
        args.vm_size,
        args.username,
        args.password,
        args.wait)
