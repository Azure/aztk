import os
import argparse
import typing
import aztk.spark
from cli import log
from cli.config import ClusterConfig, load_aztk_spark_config
from cli import utils, config


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
    parser.add_argument('--username',
                        help='Username to access your cluster (required: --wait flag)')
    parser.add_argument('--password',
                        help="The password to access your spark cluster's head \
                             node. If not provided will use ssh public key.")
    parser.add_argument('--docker-repo',
                        help='The location of the public docker image you want to use \
                             (<my-username>/<my-repo>:<tag>)')
    parser.add_argument('--subnet-id',
                        help='The subnet in which to create the cluster.')

    parser.add_argument('--no-wait', dest='wait', action='store_false')
    parser.add_argument('--wait', dest='wait', action='store_true')
    parser.set_defaults(wait=None, size=None, size_low_pri=None)


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_screts())

    # read cluster.yaml configuartion file, overwrite values with args
    cluster_conf = ClusterConfig()

    cluster_conf.merge(
        uid=args.cluster_id,
        size=args.size,
        size_low_pri=args.size_low_pri,
        vm_size=args.vm_size,
        subnet_id=args.subnet_id,
        wait=args.wait,
        username=args.username,
        password=args.password,
        docker_repo=args.docker_repo)

    print_cluster_conf(cluster_conf)

    spinner = utils.Spinner()

    log.info("Please wait while your cluster is being provisioned")
    spinner.start()

    if cluster_conf.custom_scripts:
        custom_scripts = []
        for custom_script in cluster_conf.custom_scripts:
            custom_scripts.append(
                aztk.spark.models.CustomScript(
                    script=custom_script['script'],
                    run_on=custom_script['runOn']
                )
            )
    else:
        custom_scripts = None

    if cluster_conf.file_shares:
        file_shares = []
        for file_share in cluster_conf.file_shares:
            file_shares.append(
                aztk.spark.models.FileShare(
                    storage_account_name=file_share['storage_account_name'],
                    storage_account_key=file_share['storage_account_key'],
                    file_share_path=file_share['file_share_path'],
                    mount_path=file_share['mount_path']
                )
            )
    else:
        file_shares = None

    # create spark cluster
    cluster = spark_client.create_cluster(
        aztk.spark.models.ClusterConfiguration(
            cluster_id=cluster_conf.uid,
            vm_count=cluster_conf.size,
            vm_low_pri_count=cluster_conf.size_low_pri,
            vm_size=cluster_conf.vm_size,
            subnet_id=cluster_conf.subnet_id,
            custom_scripts=custom_scripts,
            file_shares=file_shares,
            docker_repo=cluster_conf.docker_repo,
            spark_configuration=load_aztk_spark_config()
        ),
        wait=cluster_conf.wait
    )

    if cluster_conf.username:
        ssh_key = spark_client.secrets_config.ssh_pub_key

        ssh_key, password = utils.get_ssh_key_or_prompt(
            ssh_key, cluster_conf.username, cluster_conf.password, spark_client.secrets_config)

        spark_client.create_user(
            cluster_id=cluster_conf.uid,
            username=cluster_conf.username,
            password=password,
            ssh_key=ssh_key
        )

    spinner.stop()

    if cluster_conf.wait:
        log.info("Cluster %s created successfully.", cluster.id)
    else:
        log.info("Cluster %s is being provisioned.", cluster.id)


def print_cluster_conf(cluster_conf):
    log.info("-------------------------------------------")
    log.info("spark cluster id:        %s", cluster_conf.uid)
    log.info("spark cluster size:      %s",
             cluster_conf.size + cluster_conf.size_low_pri)
    log.info(">        dedicated:      %s", cluster_conf.size)
    log.info(">     low priority:      %s", cluster_conf.size_low_pri)
    log.info("spark cluster vm size:   %s", cluster_conf.vm_size)
    log.info("custom scripts:          %s", cluster_conf.custom_scripts)
    log.info("subnet ID:               %s", cluster_conf.subnet_id)
    log.info("file shares:             %s", len(cluster_conf.file_shares) if cluster_conf.file_shares is not None else 0)
    log.info("docker repo name:        %s", cluster_conf.docker_repo)
    log.info("wait for cluster:        %s", cluster_conf.wait)
    log.info("username:                %s", cluster_conf.username)
    if cluster_conf.password:
        log.info("Password: %s", '*' * len(cluster_conf.password))
    log.info("-------------------------------------------")
