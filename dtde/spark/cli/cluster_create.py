import argparse
import typing
from dtde.config import load_spark_config, cleanup_spark_config
from dtde import clusterlib, log
from dtde.config import ClusterConfig

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id', dest='cluster_id',
                        help='The unique id of your spark cluster')

    # Make --size and --size-low-pri mutually exclusive until there is a fix for
    # having clusters with mixed priority types
    size_group = parser.add_mutually_exclusive_group()
    size_group.add_argument('--size', type=int,
                            help='Number of vms in your cluster')
    size_group.add_argument('--size-low-pri', type=int,
                            help='Number of low priority vms in your cluster')
    parser.add_argument('--vm-size',
                        help='VM size for nodes in your cluster')
    parser.add_argument('--custom-script',
                        help='Absolute path of custom bash script (.sh) to run \
                              on each node')
    parser.add_argument('--username',
                        help='Username to access your cluster (required: --wait flag)')
    parser.add_argument('--password',
                        help="The password to access your spark cluster's head \
                             node. If not provided will use ssh public key.")
    parser.add_argument('--ssh-key',
                        help="The ssh public key to access your spark cluster\'s head \
                             node. You can also set the ssh-key in the configuration file.")
    parser.add_argument('--docker-repo',
                        help='The location of the public docker image you want to use \
                             (<my-username>/<my-repo>:<tag>)')

    parser.add_argument('--no-wait', dest='wait', action='store_false')
    parser.add_argument('--wait', dest='wait', action='store_true')
    parser.set_defaults(wait=False, size=0, size_low_pri=0)


def execute(args: typing.NamedTuple):
    # read cluster.yaml configuartion file, overwrite values with args
    cluster_conf = ClusterConfig()

    cluster_conf.merge(
            uid = args.cluster_id,
            size = args.size,
            size_low_pri = args.size_low_pri,
            vm_size = args.vm_size,
            custom_script = args.custom_script,
            wait = args.wait,
            username = args.username,
            password = args.password,
            ssh_key = args.ssh_key,
            docker_repo = args.docker_repo)

    load_spark_config()

    log.info("-------------------------------------------")
    log.info("spark cluster id:        %s", cluster_conf.uid)
    log.info("spark cluster size:      %s", cluster_conf.size + cluster_conf.size_low_pri)
    log.info(">        dedicated:      %s", cluster_conf.size)
    log.info(">     low priority:      %s", cluster_conf.size_low_pri)
    log.info("spark cluster vm size:   %s", cluster_conf.vm_size)
    log.info("path to custom script:   %s", cluster_conf.custom_script)
    log.info("docker repo name:        %s", cluster_conf.docker_repo)
    log.info("wait for cluster:        %s", cluster_conf.wait)
    log.info("username:                %s", cluster_conf.username)
    if args.password:
        log.info("Password: %s", '*' * len(cluster_conf.password))
    log.info("-------------------------------------------")

    # create spark cluster
    clusterlib.create_cluster(
        cluster_conf.custom_script,
        cluster_conf.uid,
        cluster_conf.size,
        cluster_conf.size_low_pri,
        cluster_conf.vm_size,
        cluster_conf.username,
        cluster_conf.password,
        cluster_conf.ssh_key,
        cluster_conf.ports,
        cluster_conf.docker_repo,
        cluster_conf.wait)

    log.info("Cluster created successfully.")

    cleanup_spark_config()
