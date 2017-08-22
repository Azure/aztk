import argparse
import typing
from dtde import clusterlib, log


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
                        help="The password to access your spark cluster's head node. If not provided will use ssh public key.")
    parser.add_argument('--ssh-key',
                        help="The ssh public key to access your spark cluster\'s head node. You can also set the ssh-key in the configuration file.")
    parser.add_argument('--no-wait', dest='wait', action='store_false')
    parser.add_argument('--wait', dest='wait', action='store_true')
    parser.set_defaults(wait=False, size=0, size_low_pri=0)


def execute(args: typing.NamedTuple):
    log.info("-------------------------------------------")
    log.info("spark cluster id:        %s", args.cluster_id)
    log.info("spark cluster size:      %s", args.size + args.size_low_pri)
    log.info(">        dedicated:      %s", args.size)
    log.info(">     low priority:      %s", args.size_low_pri)
    log.info("spark cluster vm size:   %s", args.vm_size)
    log.info("path to custom script:   %s", args.custom_script)
    log.info("wait for cluster:        %s", args.wait)
    log.info("username:                %s", args.username)
    if args.password:
        log.info("Password: %s", '*' * len(args.password))
    log.info("-------------------------------------------")

    # create spark cluster
    clusterlib.create_cluster(
        args.custom_script,
        args.cluster_id,
        args.size,
        args.size_low_pri,
        args.vm_size,
        args.username,
        args.password,
        args.ssh_key,
        args.wait)

    log.info("Cluster created successfully.")
