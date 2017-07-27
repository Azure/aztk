from datetime import datetime, timedelta
from subprocess import call
from dtde.core import CommandBuilder, ssh
from collections import namedtuple
import azure.batch.models as batch_models
from dtde.models import Software
from dtde.error import ClusterNotReadyError, InvalidUserCredentialsError
from . import azure_api, constants, upload_node_scripts, util

POOL_ADMIN_USER_IDENTITY = batch_models.UserIdentity(
    auto_user=batch_models.AutoUserSpecification(
        scope=batch_models.AutoUserScope.pool,
        elevation_level=batch_models.ElevationLevel.admin))


def cluster_install_cmd(zip_resource_file: batch_models.ResourceFile, custom_script_file):
    """
        This will return the command line to be run on the start task of the pool to setup spark.
    """
    ret = [
        # setup spark home and permissions for spark folder
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',
        'chmod -R 777 $SPARK_HOME',
        'chmod -R 777 /usr/local/share/jupyter/kernels',
        # To avoid error: "sudo: sorry, you must have a tty to run sudo"
        'sed -i -e "s/Defaults    requiretty.*/ #Defaults    requiretty/g" /etc/sudoers',
        'unzip $AZ_BATCH_TASK_WORKING_DIR/{0}'.format(
            zip_resource_file.file_path),
        'chmod 777 $AZ_BATCH_TASK_WORKING_DIR/main.sh',
        # Convert windows line ending to unix if applicable
        'dos2unix $AZ_BATCH_TASK_WORKING_DIR/main.sh',
        '$AZ_BATCH_TASK_WORKING_DIR/main.sh'
    ]

    if custom_script_file is not None:
        ret.extend([
            '/bin/sh -c {}'.format(custom_script_file),
        ])

    ret.extend(['exit 0'])

    return ret


def generate_cluster_start_task(
        cluster_id: str,
        zip_resource_file: batch_models.ResourceFile,
        custom_script: str=None):
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
            util.upload_file_to_container(
                container_name=cluster_id,
                file_path=custom_script,
                use_full_path=True))

    # TODO use certificate
    batch_config = azure_api.get_batch_config()
    environment_settings = [
        batch_models.EnvironmentSetting(
            name="BATCH_ACCOUNT_KEY", value=batch_config.account_key),
        batch_models.EnvironmentSetting(
            name="BATCH_ACCOUNT_URL", value=batch_config.account_url),
    ]

    # start task command
    command = cluster_install_cmd(zip_resource_file, custom_script)

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
    publisher = 'microsoft-ads'
    offer = 'linux-data-science-vm'
    sku = 'linuxdsvm'

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
            pool_id, zip_resource_file, custom_script),
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


def get_cluster_details(cluster_id: str):
    """
        Print the information for the given cluster
        :param cluster_id: Id of the cluster
    """
    batch_client = azure_api.get_batch_client()

    pool = batch_client.pool.get(cluster_id)
    if pool.state is batch_models.PoolState.deleting:
        print("Cluster is being deleted!")
        return
    nodes = batch_client.compute_node.list(pool_id=cluster_id)
    visible_state = pool.allocation_state.value if pool.state.value is 'active' else pool.state.value
    node_count = '{} -> {}'.format(
        pool.current_dedicated_nodes + pool.current_low_priority_nodes,
        pool.target_dedicated_nodes + pool.target_low_priority_nodes) if pool.state.value is 'resizing' or (pool.state.value is 'deleting' and pool.allocation_state.value is 'resizing') else '{}'.format(pool.current_dedicated_nodes)

    print()
    print('State:          {}'.format(visible_state))
    print('Node Size:      {}'.format(pool.vm_size))
    print('Nodes:          {}'.format(node_count))
    print('| Dedicated:    {}'.format(pool.current_dedicated_nodes))
    print('| Low priority: {}'.format(pool.current_low_priority_nodes))
    print()

    node_label = 'Nodes'
    print_format = '{:<36}| {:<15} | {:<21}| {:<8}'
    print_format_underline = '{:-<36}|{:-<17}|{:-<22}|{:-<8}'
    print(print_format.format(node_label, 'State', 'IP:Port', 'Master'))
    print(print_format_underline.format('', '', '', ''))

    master_node = util.get_master_node_id_from_pool(pool)

    for node in nodes:
        ip, port = util.get_connection_info(cluster_id, node.id)
        print(print_format.format(node.id, node.state.value, '{}:{}'.format(ip, port),
                                  '*' if node.id == master_node else ''))
    print()


def is_pool_running_spark(pool: batch_models.CloudPool):
    if pool.metadata is None:
        return False

    for metadata in pool.metadata:
        if metadata.name == constants.AZB_SOFTWARE_METADATA_KEY:
            return metadata.value == Software.spark

    return False


def list_clusters():
    """
        List all the cluster on your account.
    """
    batch_client = azure_api.get_batch_client()

    print_format = '{:<34}| {:<10}| {:<20}| {:<7}'
    print_format_underline = '{:-<34}|{:-<11}|{:-<21}|{:-<7}'

    pools = batch_client.pool.list()
    print(print_format.format('Cluster', 'State', 'VM Size', 'Nodes'))
    print(print_format_underline.format('', '', '', ''))
    for pool in pools:
        if not is_pool_running_spark(pool):
            continue
        pool_state = pool.allocation_state.value if pool.state.value is 'active' else pool.state.value

        target_nodes = util.get_cluster_total_target_nodes(pool)
        current_nodes = util.get_cluster_total_current_nodes(pool)
        node_count = current_nodes
        if pool_state is 'resizing' or (pool_state is 'deleting' and pool.allocation_state.value is 'resizing'):
            node_count = '{} -> {}'.format(current_nodes, target_nodes)

        print(print_format.format(pool.id,
                                  pool_state,
                                  pool.vm_size,
                                  node_count))


def delete_cluster(cluster_id: str):
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

    if job_exists or pool_exists:
        print("Deleting cluster {0}".format(cluster_id))


def ssh_in_master(
        cluster_id: str,
        username: str=None,
        masterui: str=None,
        webui: str=None,
        jupyter: str=None,
        ports=None,
        connect: bool=True):
    """
        SSH into head node of spark-app
        :param cluster_id: Id of the cluster to ssh in
        :param username: Username to use to ssh
        :param masterui: Port for the master ui(Local port)
        :param webui: Port for the spark web ui(Local port)
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

    ssh_command = CommandBuilder('ssh')

    ssh_command.add_option("-L", "{0}:localhost:{1}".format(
        masterui, constants.SPARK_MASTER_UI_PORT), enable=bool(masterui))
    ssh_command.add_option(
        "-L", "{0}:localhost:{1}".format(webui, constants.SPARK_WEBUI_PORT), enable=bool(webui))
    ssh_command.add_option("-L", "{0}:localhost:{1}".format(
        jupyter, constants.SPARK_JUPYTER_PORT), enable=bool(jupyter))

    if ports is not None:
        for port in ports:
            ssh_command.add_option(
                "-L", "{0}:localhost:{1}".format(port[0], port[1]))

    user = username if username is not None else '<username>'
    ssh_command.add_argument(
        "{0}@{1} -p {2}".format(user, master_node_ip, master_node_port))

    command = ssh_command.to_str()
    ssh_command_array = command.split()

    if not connect:
        print('\nuse the following command to connect to your spark head node:')
        print('\n\t{}\n'.format(command))
    else:
        call(ssh_command_array)
