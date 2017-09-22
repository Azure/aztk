import os
from datetime import datetime, timedelta
from dtde.core import CommandBuilder, ssh
from subprocess import call
from typing import List
from dtde.models import Software
import azure.batch.models as batch_models
from . import azure_api, constants, upload_node_scripts, util, log
from dtde.error import ClusterNotReadyError, InvalidUserCredentialsError
from collections import namedtuple

POOL_ADMIN_USER_IDENTITY = batch_models.UserIdentity(
    auto_user=batch_models.AutoUserSpecification(
        scope=batch_models.AutoUserScope.pool,
        elevation_level=batch_models.ElevationLevel.admin))


def cluster_install_cmd(
        zip_resource_file: batch_models.ResourceFile,
        docker_repo: str = None):
    """
        For Docker on ubuntu 16.04 - return the command line 
        to be run on the start task of the pool to setup spark.
    """

    ret = [
        'apt-get -y clean',
        'apt-get -y update',
        'apt-get install --fix-missing',
        'apt-get -y install unzip',
        'unzip $AZ_BATCH_TASK_WORKING_DIR/{0}'.format(
            zip_resource_file.file_path),
        'chmod 777 $AZ_BATCH_TASK_WORKING_DIR/setup_node.sh',
        '/bin/bash $AZ_BATCH_TASK_WORKING_DIR/setup_node.sh {0} {1} "{2}"'.format(
            constants.DOCKER_SPARK_CONTAINER_NAME, 
            constants.DEFAULT_DOCKER_REPO, 
            docker_run_cmd(docker_repo)),
    ]

    return ret


def docker_run_cmd(docker_repo: str = None) -> str:
    """
        Build the docker run command by setting up the environment variables
    """

    docker_repo = docker_repo if docker_repo != None \
            else constants.DEFAULT_DOCKER_REPO

    cmd = CommandBuilder('docker run')
    cmd.add_option('--net', 'host')
    cmd.add_option('--name', constants.DOCKER_SPARK_CONTAINER_NAME)
    cmd.add_option('-v', '/mnt/batch/tasks:/batch')

    cmd.add_option('-e', 'DOCKER_WORKING_DIR=/batch/startup/wd')
    cmd.add_option('-e', 'AZ_BATCH_ACCOUNT_NAME=$AZ_BATCH_ACCOUNT_NAME')
    cmd.add_option('-e', 'BATCH_ACCOUNT_KEY=$BATCH_ACCOUNT_KEY')
    cmd.add_option('-e', 'BATCH_ACCOUNT_URL=$BATCH_ACCOUNT_URL')
    cmd.add_option('-e', 'STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT_NAME')
    cmd.add_option('-e', 'STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY')
    cmd.add_option('-e', 'STORAGE_ACCOUNT_SUFFIX=$STORAGE_ACCOUNT_SUFFIX')
    cmd.add_option('-e', 'AZ_BATCH_POOL_ID=$AZ_BATCH_POOL_ID')
    cmd.add_option('-e', 'AZ_BATCH_NODE_ID=$AZ_BATCH_NODE_ID')
    cmd.add_option(
        '-e', 'AZ_BATCH_NODE_IS_DEDICATED=$AZ_BATCH_NODE_IS_DEDICATED')
    cmd.add_option('-e', 'SPARK_MASTER_UI_PORT=$SPARK_MASTER_UI_PORT')
    cmd.add_option('-e', 'SPARK_WORKER_UI_PORT=$SPARK_WORKER_UI_PORT')
    cmd.add_option('-e', 'SPARK_JUPYTER_PORT=$SPARK_JUPYTER_PORT')
    cmd.add_option('-e', 'SPARK_WEB_UI_PORT=$SPARK_WEB_UI_PORT')
    cmd.add_option('-p', '8080:8080')
    cmd.add_option('-p', '7077:7077')
    cmd.add_option('-p', '4040:4040')
    cmd.add_option('-p', '8888:8888')
    cmd.add_option('-d', docker_repo)
    cmd.add_argument('/bin/bash /batch/startup/wd/docker_main.sh')
    return cmd.to_str()


def generate_cluster_start_task(
        cluster_id: str,
        zip_resource_file: batch_models.ResourceFile,
        custom_script: str = None,
        docker_repo: str = None):
    """
        This will return the start task object for the pool to be created.
        :param cluster_id str: Id of the cluster(Used for uploading the resource files)
        :param zip_resource_file: Resource file object pointing to the zip file containing scripts to run on the node
        :param custom_script str: Path to a local file to be uploaded to storage and run after spark started.
    """

    resource_files = [zip_resource_file]

    # Upload custom script file if given
    if custom_script is not None:
        resource_files.append(
            util.upload_shell_script_to_container(
                container_name=cluster_id,
                file_path=custom_script,
                node_path="custom-scripts/{0}".format(os.path.basename(custom_script))))

    spark_master_ui_port = constants.DOCKER_SPARK_MASTER_UI_PORT
    spark_worker_ui_port = constants.DOCKER_SPARK_WORKER_UI_PORT
    spark_jupyter_port = constants.DOCKER_SPARK_JUPYTER_PORT
    spark_web_ui_port = constants.DOCKER_SPARK_WEB_UI_PORT

    # TODO use certificate
    batch_config = azure_api.get_batch_config()
    blob_config = azure_api.get_blob_config()
    environment_settings = [
        batch_models.EnvironmentSetting(
            name="BATCH_ACCOUNT_KEY", value=batch_config.account_key),
        batch_models.EnvironmentSetting(
            name="BATCH_ACCOUNT_URL", value=batch_config.account_url),
        batch_models.EnvironmentSetting(
            name="STORAGE_ACCOUNT_NAME", value=blob_config.account_name),
        batch_models.EnvironmentSetting(
            name="STORAGE_ACCOUNT_KEY", value=blob_config.account_key),
        batch_models.EnvironmentSetting(
            name="STORAGE_ACCOUNT_SUFFIX", value=blob_config.account_suffix),
        batch_models.EnvironmentSetting(
            name="SPARK_MASTER_UI_PORT", value=spark_master_ui_port),
        batch_models.EnvironmentSetting(
            name="SPARK_WORKER_UI_PORT", value=spark_worker_ui_port),
        batch_models.EnvironmentSetting(
            name="SPARK_JUPYTER_PORT", value=spark_jupyter_port),
        batch_models.EnvironmentSetting(
            name="SPARK_WEB_UI_PORT", value=spark_web_ui_port),
    ]

    # start task command
    command = cluster_install_cmd(zip_resource_file, docker_repo)

    return batch_models.StartTask(
        command_line=util.wrap_commands_in_shell(command),
        resource_files=resource_files,
        environment_settings=environment_settings,
        user_identity=POOL_ADMIN_USER_IDENTITY,
        wait_for_success=True)


def create_cluster(
        custom_script: str,
        cluster_id: str,
        vm_count,
        vm_low_pri_count,
        vm_size,
        username: str,
        password: str = None,
        ssh_key: str = None,
        docker_repo: str = None,
        wait=True):
    """
        Create a spark cluster
        :param custom_script: Path to a custom script to run on all the node of the cluster
        :parm cluster_id: Id of the cluster
        :param vm_count: Number of node in the cluster
        :param vm_low_pri_count: Number of low pri node in the cluster
        :param vm_size: Tier of the node(standard_a2, standard_g2, etc.)
        :param username: Optional username of user to add to the pool when ready(Need wait to be True)
        :param password: Optional password of user to add to the pool when ready(Need wait to be True)
        :param wait: If this function should wait for the cluster to be ready(Master and all slave booted)
    """

    # Upload start task scripts
    zip_resource_file = upload_node_scripts.zip_and_upload()

    batch_client = azure_api.get_batch_client()

    # vm image
    publisher = 'Canonical'
    offer = 'UbuntuServer'
    sku = '16.04'

    # reuse pool_id as job_id
    pool_id = cluster_id
    job_id = cluster_id

    # Get a verified node agent sku
    sku_to_use, image_ref_to_use = \
        util.select_latest_verified_vm_image_with_node_agent_sku(
            publisher, offer, sku)

    # Confiure the pool
    pool = batch_models.PoolAddParameter(
        id=pool_id,
        virtual_machine_configuration=batch_models.VirtualMachineConfiguration(
            image_reference=image_ref_to_use,
            node_agent_sku_id=sku_to_use),
        vm_size=vm_size,
        target_dedicated_nodes=vm_count,
        target_low_priority_nodes=vm_low_pri_count,
        start_task=generate_cluster_start_task(
            pool_id, zip_resource_file, custom_script, docker_repo),
        enable_inter_node_communication=True,
        max_tasks_per_node=1,
        metadata=[
            batch_models.MetadataItem(
                name=constants.AZB_SOFTWARE_METADATA_KEY, value=Software.spark),
        ])

    # Create the pool + create user for the pool
    util.create_pool_if_not_exist(
        pool,
        wait)

    # Create job
    job = batch_models.JobAddParameter(
        id=job_id,
        pool_info=batch_models.PoolInformation(pool_id=pool_id))

    # Add job to batch
    batch_client.job.add(job)

    # Wait for the app to finish
    if wait:
        util.wait_for_master_to_be_ready(pool_id)

        if username is not None:
            create_user(pool_id, username, password, ssh_key)


def create_user(
        cluster_id: str,
        username: str,
        password: str = None,
        ssh_key: str = None) -> str:
    """
        Create a cluster user
        :param cluster_id: id of the spark cluster
        :param username: username of the user to add
        :param password: password of the user to add
    """
    batch_client = azure_api.get_batch_client()
    if password is None:
        ssh_key = ssh.get_user_public_key(ssh_key)

    if not password and not ssh_key:
        raise InvalidUserCredentialsError(
            "Cannot add user to cluster. Need to provide a ssh public key or password.")

    # Create new ssh user for the master node
    batch_client.compute_node.add_user(
        cluster_id,
        util.get_master_node_id(cluster_id),
        batch_models.ComputeNodeUser(
            username,
            is_admin=True,
            password=password,
            ssh_public_key=ssh_key,
            expiry_time=datetime.now() + timedelta(days=365)))

    return (
        '*' * len(password) if password else None,
        ssh_key,
    )


class Cluster:
    def __init__(self, pool, nodes=None):
        self.id = pool.id
        self.pool = pool
        self.nodes = nodes
        self.master_node_id = util.get_master_node_id_from_pool(pool)
        if pool.state.value is batch_models.PoolState.active:
            self.visible_state = pool.allocation_state.value
        else:
            self.visible_state = pool.state.value
        self.vm_size = pool.vm_size
        self.total_current_nodes = pool.current_dedicated_nodes + \
            pool.current_low_priority_nodes
        self.total_target_nodes = pool.target_dedicated_nodes + \
            pool.target_low_priority_nodes
        self.dedicated_nodes = pool.current_dedicated_nodes
        self.low_pri_nodes = pool.current_low_priority_nodes
        self.target_dedicated_nodes = pool.target_dedicated_nodes
        self.target_low_pri_nodes = pool.target_low_priority_nodes


def pretty_node_count(cluster: Cluster) -> str:
    if cluster.pool.allocation_state is batch_models.AllocationState.resizing:
        return '{} -> {}'.format(
            cluster.total_current_nodes,
            cluster.total_target_nodes)
    else:
        return '{}'.format(cluster.total_current_nodes)


def pretty_dedicated_node_count(cluster: Cluster)-> str:
    if (cluster.pool.allocation_state is batch_models.AllocationState.resizing\
        or cluster.pool.state is batch_models.PoolState.deleting)\
        and cluster.dedicated_nodes != cluster.target_dedicated_nodes:
        return '{} -> {}'.format(
            cluster.dedicated_nodes,
            cluster.target_dedicated_nodes)
    else:
        return '{}'.format(cluster.dedicated_nodes)


def pretty_low_pri_node_count(cluster: Cluster)-> str:
    if (cluster.pool.allocation_state is batch_models.AllocationState.resizing\
        or cluster.pool.state is batch_models.PoolState.deleting)\
        and cluster.low_pri_nodes != cluster.target_low_pri_nodes:
        return '{} -> {}'.format(
            cluster.low_pri_nodes,
            cluster.target_low_pri_nodes)
    else:
        return '{}'.format(cluster.low_pri_nodes)


def print_cluster(cluster: Cluster):
    node_count = pretty_node_count(cluster)

    log.info("")
    log.info("Cluster         %s", cluster.id)
    log.info("------------------------------------------")
    log.info("State:          %s", cluster.visible_state)
    log.info("Node Size:      %s", cluster.vm_size)
    log.info("Nodes:          %s", node_count)
    log.info("| Dedicated:    %s", pretty_dedicated_node_count(cluster))
    log.info("| Low priority: %s", pretty_low_pri_node_count(cluster))
    log.info("")

    print_format = '{:<36}| {:<15} | {:<21}| {:<8}'
    print_format_underline = '{:-<36}|{:-<17}|{:-<22}|{:-<8}'
    log.info(print_format.format("Nodes", "State", "IP:Port", "Master"))
    log.info(print_format_underline.format('', '', '', ''))

    if not cluster.nodes:
        return
    for node in cluster.nodes:
        ip, port = util.get_connection_info(cluster.id, node.id)
        log.info(print_format.format(node.id, node.state.value, '{}:{}'.format(ip, port),
                                     '*' if node.id == cluster.master_node_id else ''))
    log.info('')


def get_cluster(cluster_id: str) -> Cluster:
    """
        Print the information for the given cluster
        :param cluster_id: Id of the cluster
    """
    batch_client = azure_api.get_batch_client()

    pool = batch_client.pool.get(cluster_id)
    if pool.state is batch_models.PoolState.deleting:
        return Cluster(pool)

    nodes = batch_client.compute_node.list(pool_id=cluster_id)
    return Cluster(pool, nodes)


def is_pool_running_spark(pool: batch_models.CloudPool):
    if pool.metadata is None:
        return False

    for metadata in pool.metadata:
        if metadata.name == constants.AZB_SOFTWARE_METADATA_KEY:
            return metadata.value == Software.spark

    return False


def list_clusters() -> List[Cluster]:
    """
        List all the cluster on your account.
    """
    batch_client = azure_api.get_batch_client()

    pools = batch_client.pool.list()

    return [Cluster(pool) for pool in pools if is_pool_running_spark(pool)]


def print_clusters(clusters: List[Cluster]):
    print_format = '{:<34}| {:<10}| {:<20}| {:<7}'
    print_format_underline = '{:-<34}|{:-<11}|{:-<21}|{:-<7}'

    log.info(print_format.format('Cluster', 'State', 'VM Size', 'Nodes'))
    log.info(print_format_underline.format('', '', '', ''))
    for cluster in clusters:
        node_count = pretty_node_count(cluster)

        log.info(print_format.format(cluster.id,
                                     cluster.visible_state,
                                     cluster.vm_size,
                                     node_count))


def delete_cluster(cluster_id: str) -> bool:
    """
        Delete a spark cluster
        :param cluster_id: Id of the cluster to delete
    """
    batch_client = azure_api.get_batch_client()

    # delete pool by id
    pool_id = cluster_id

    # job id is equal to pool id
    job_id = pool_id
    job_exists = True

    try:
        batch_client.job.get(job_id)
    except:
        job_exists = False

    pool_exists = batch_client.pool.exists(pool_id)

    if job_exists:
        batch_client.job.delete(job_id)

    if pool_exists:
        batch_client.pool.delete(pool_id)

    return job_exists or pool_exists


def ssh_in_master(
        cluster_id: str,
        username: str=None,
        webui: str=None,
        jobui: str=None,
        jupyter: str=None,
        ports=None,
        connect: bool=True):
    """
        SSH into head node of spark-app
        :param cluster_id: Id of the cluster to ssh in
        :param username: Username to use to ssh
        :param webui: Port for the spark master web ui (Local port)
        :param jobui: Port for the job web ui (Local port)
        :param jupyter: Port for jupyter(Local port)
        :param ports: an list of local and remote ports
        :type ports: [[<local-port>, <remote-port>]]
    """
    batch_client = azure_api.get_batch_client()

    # Get master node id from task (job and task are both named pool_id)
    master_node_id = util.get_master_node_id(cluster_id)

    if master_node_id is None:
        raise ClusterNotReadyError("Master node has not yet been picked!")

    # get remote login settings for the user
    remote_login_settings = batch_client.compute_node.get_remote_login_settings(
        cluster_id, master_node_id)

    master_node_ip = remote_login_settings.remote_login_ip_address
    master_node_port = remote_login_settings.remote_login_port

    pool = batch_client.pool.get(cluster_id)

    spark_master_ui_port = constants.DOCKER_SPARK_MASTER_UI_PORT
    spark_worker_ui_port = constants.DOCKER_SPARK_WORKER_UI_PORT
    spark_jupyter_port = constants.DOCKER_SPARK_JUPYTER_PORT
    spark_web_ui_port = constants.DOCKER_SPARK_WEB_UI_PORT

    ssh_command = CommandBuilder('ssh')

    ssh_command.add_option("-L", "{0}:localhost:{1}".format(
        webui,  spark_master_ui_port), enable=bool(webui))
    ssh_command.add_option("-L", "{0}:localhost:{1}".format(
        jobui, spark_web_ui_port), enable=bool(jobui))
    ssh_command.add_option("-L", "{0}:localhost:{1}".format(
        jupyter, spark_jupyter_port), enable=bool(jupyter))

    if ports is not None:
        for port in ports:
            ssh_command.add_option(
                "-L", "{0}:localhost:{1}".format(port[0], port[1]))

    user = username if username is not None else '<username>'
    ssh_command.add_argument(
        "{0}@{1} -p {2}".format(user, master_node_ip, master_node_port))

    command = ssh_command.to_str()
    ssh_command_array = command.split()

    if connect:
        call(ssh_command_array)
    return '\n\t{}\n'.format(command)
