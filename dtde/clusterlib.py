from datetime import datetime, timedelta
from subprocess import call
import azure.batch.models as batch_models
from . import util, constants, azure_api, upload_node_scripts

pool_admin_user = batch_models.UserIdentity(
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
        'unzip $AZ_BATCH_TASK_WORKING_DIR/%s' % zip_resource_file.file_path,
        'chmod 777 $AZ_BATCH_TASK_WORKING_DIR/main.sh',
        'dos2unix $AZ_BATCH_TASK_WORKING_DIR/main.sh', # Convert windows line ending to unix if applicable
        '$AZ_BATCH_TASK_WORKING_DIR/main.sh'
    ]

    if custom_script_file is not None:
        ret.extend([
            '/bin/sh -c {}'.format(custom_script_file),
        ])

    ret.extend(['exit 0'])

    return ret


def cluster_connect_cmd():
    return [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',

        # copy a 'slaves' file from the slaves.template in $SPARK_HOME/conf
        'cp $SPARK_HOME/conf/slaves.template $SPARK_HOME/conf/slaves'

        # delete existing content & create a new line in the slaves file
        'echo > $SPARK_HOME/conf/slaves',

        # make empty 'master' file in $SPARK/conf
        'cp $SPARK_HOME/conf/slaves $SPARK_HOME/conf/master',

        # add batch pool ips to newly created slaves files
        'IFS="," read -r -a workerips <<< $AZ_BATCH_HOST_LIST',
        'for index in "${!workerips[@]}"',
        'do echo "${workerips[index]}"',
        'if [ "${AZ_BATCH_MASTER_NODE%:*}" = "${workerips[index]}" ]',
        'then echo "${workerips[index]}" >> $SPARK_HOME/conf/master',
        'else echo "${workerips[index]}" >> $SPARK_HOME/conf/slaves',
        'fi',
        'done'
    ]


def cluster_start_cmd(webui_port, jupyter_port):
    return [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',

        # get master node ip
        'export MASTER_NODE=$(cat $SPARK_HOME/conf/master)',

        # kick off start-all spark command (which starts web ui)
        '($SPARK_HOME/sbin/start-all.sh --webui-port ' + str(webui_port) + ' &)',

        # jupyter setup: remove auth
        '/anaconda/envs/py35/bin/jupyter notebook --generate-config',
        'echo >> $HOME/.jupyter/jupyter_notebook_config.py',
        'echo c.NotebookApp.token=\\\"\\\" >> $HOME/.jupyter/jupyter_notebook_config.py',
        'echo c.NotebookApp.password=\\\"\\\" >> $HOME/.jupyter/jupyter_notebook_config.py',

        # create jupyter kernal for pyspark
        'rm -rf /usr/local/share/jupyter/kernels/*',
        'mkdir /usr/local/share/jupyter/kernels/pyspark',
        'touch /usr/local/share/jupyter/kernels/pyspark/kernel.json',
        'echo { ' +
        '\\\"display_name\\\": \\\"PySpark\\\", ' +
        '\\\"language\\\": \\\"python\\\", ' +
        '\\\"argv\\\": [ ' +
        '\\\"/usr/bin/python3\\\", ' +
        '\\\"-m\\\", ' +
        '\\\"ipykernel\\\", ' +
        '\\\"-f\\\", ' +
        '\\\"{connection_file}\\\" ' +
        '], ' +
        '\\\"env\\\": { ' +
        '\\\"SPARK_HOME\\\": \\\"/dsvm/tools/spark/current\\\", ' +
        '\\\"PYSPARK_PYTHON\\\": \\\"/usr/bin/python3\\\", ' +
        '\\\"PYSPARK_SUBMIT_ARGS\\\": ' +
        '\\\"--master spark://${MASTER_NODE%:*}:7077 ' +
        # '--executor-memory 6400M ' +
        # '--driver-memory 6400M ' +
        'pyspark-shell\\\" ' +
        '}' +
        '} >> /usr/local/share/jupyter/kernels/pyspark/kernel.json',

        # start jupyter notebook
        '(PYSPARK_DRIVER_PYTHON=/anaconda/envs/py35/bin/jupyter ' +
        'PYSPARK_DRIVER_PYTHON_OPTS="notebook --no-browser --port=' + str(jupyter_port) + '" ' +
        'pyspark &)'  # +
        #     '--master spark://${MASTER_NODE%:*}:7077 '  +
        #     '--executor-memory 6400M ' +
        #     '--driver-memory 6400M &)'
    ]


def generate_cluster_start_task(cluster_id: str, zip_resource_file: batch_models.ResourceFile, custom_script: str = None):
    """
        This will return the start task object for the pool to be created.
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
            name="ACCOUNT_KEY", value=batch_config.account_key),
        batch_models.EnvironmentSetting(
            name="ACCOUNT_URL", value=batch_config.account_url),
    ]

    # start task command
    command = cluster_install_cmd(zip_resource_file, custom_script)

    return batch_models.StartTask(
        command_line=util.wrap_commands_in_shell(command),
        resource_files=resource_files,
        environment_settings=environment_settings,
        user_identity=pool_admin_user,
        wait_for_success=True)


def create_cluster(
        custom_script,
        pool_id,
        vm_count,
        vm_low_pri_count,
        vm_size,
        username,
        password,
        wait=True):
    """
    Create a spark cluster
    """

    # Upload start task scripts
    zip_resource_file = upload_node_scripts.zip_and_upload()

    batch_client = azure_api.get_batch_client()
    blob_client = azure_api.get_blob_client()

    # vm image
    publisher = 'microsoft-ads'
    offer = 'linux-data-science-vm'
    sku = 'linuxdsvm'

    # reuse pool_id as job_id
    job_id = pool_id

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
        start_task=generate_cluster_start_task(pool_id, zip_resource_file, custom_script),
        enable_inter_node_communication=True,
        max_tasks_per_node=1)

    # Create the pool + create user for the pool
    util.create_pool_if_not_exist(
        pool,
        wait)

    return # TODO 

    # Create job
    job = batch_models.JobAddParameter(
        id=job_id,
        pool_info=batch_models.PoolInformation(pool_id=pool_id))

    # Add job to batch
    batch_client.job.add(job)

    # create application/coordination commands
    coordination_cmd = cluster_connect_cmd()
    application_cmd = cluster_start_cmd(
        constants._WEBUI_PORT, constants._JUPYTER_PORT)

    # reuse pool_id as multi-instance task id
    task_id = pool_id

    # Create multi-instance task
    task = batch_models.TaskAddParameter(
        id=task_id,
        command_line=util.wrap_commands_in_shell(application_cmd),
        resource_files=[],
        multi_instance_settings=batch_models.MultiInstanceSettings(
            number_of_instances=vm_count + vm_low_pri_count,
            coordination_command_line=util.wrap_commands_in_shell(
                coordination_cmd),
            common_resource_files=[]))

    # Add task to batch job (which has the same name as pool_id)
    try:
        batch_client.task.add(job_id=job_id, task=task)
    except batch_models.batch_error.BatchErrorException as err:
        util.print_batch_exception(err)
        if err.error.code != 'JobExists':
            raise
        else:
            print('Job {!r} already exists'.format(job_id))

    # Wait for the app to finish
    if wait == True:

        util.wait_for_tasks_to_complete(
            job_id,
            timedelta(minutes=60))

        if username is not None and password is not None:
            create_user(pool_id, username, password)


def create_user(
        pool_id,
        username,
        password):
    """
    Create a cluster user
    """
    batch_client = azure_api.get_batch_client()

    # Get master node id from task
    master_node_id = None
    try:
        # job and task are both named pool_id
        master_node_id = batch_client.task \
            .get(job_id=pool_id, task_id=pool_id) \
            .node_info.node_id
    except AttributeError as err:
        print('cluster, "{}", is still setting up - '.format(pool_id) +
              'please wait for your cluster to be created ' +
              'before creating a user')
        exit()

    # Create new ssh user for the master node
    batch_client.compute_node.add_user(
        pool_id,
        master_node_id,
        batch_models.ComputeNodeUser(
            username,
            is_admin=True,
            password=password,
            expiry_time=datetime.now() + timedelta(days=365)))


def get_cluster_details(pool_id: str):
    """
    print out specified cluster info
    """
    batch_client = azure_api.get_batch_client()

    pool = batch_client.pool.get(pool_id)
    if (pool.state == batch_models.PoolState.deleting):
        print
    nodes = batch_client.compute_node.list(pool_id=pool_id)
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

    # Do not print node details if the pool is deleting
    if pool.state.value is 'deleting':
        return

    node_label = 'Nodes'
    print_format = '{:<36}| {:<15} | {:<21}| {:<8}'
    print_format_underline = '{:-<36}|{:-<17}|{:-<22}|{:-<8}'
    print(print_format.format(node_label, 'State', 'IP:Port', 'Master'))
    print(print_format_underline.format('', '', '', ''))

    master_node = util.get_master_node_id(pool_id)

    for node in nodes:
        ip, port = util.get_connection_info(pool_id, node.id)
        print(print_format.format(node.id, node.state.value, '{}:{}'.format(ip, port),
                                  '*' if node.id == master_node else ''))
    print()


def list_clusters():
    """
    print out all clusters 
    """
    batch_client = azure_api.get_batch_client()

    print_format = '{:<34}| {:<10}| {:<20}| {:<7}'
    print_format_underline = '{:-<34}|{:-<11}|{:-<21}|{:-<7}'

    pools = batch_client.pool.list()
    print(print_format.format('Cluster', 'State', 'VM Size', 'Nodes'))
    print(print_format_underline.format('', '', '', ''))
    for pool in pools:
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


def delete_cluster(pool_id: str):
    """
    Delete a spark cluster
    """
    batch_client = azure_api.get_batch_client()

    # delete pool by id
    pool = batch_client.pool.get(pool_id)

    # job id is equal to pool id
    job_id = pool_id

    if batch_client.pool.exists(pool_id) == True:
        batch_client.pool.delete(pool_id)
        batch_client.job.delete(job_id)
        print('The pool, \'{}\', is being deleted'.format(pool_id))
    else:
        print('The pool, \'{}\', does not exist'.format(pool_id))


def ssh(
        pool_id: str,
        username=None,
        masterui=None,
        webui=None,
        jupyter=None,
        ports=None,
        connect=True):
    """
    SSH into head node of spark-app
    :param ports: an list of local and remote ports
    :type ports: [[<local-port>, <remote-port>]]
    """
    batch_client = azure_api.get_batch_client()

    # Get master node id from task (job and task are both named pool_id)
    master_node_id = batch_client.task \
        .get(job_id=pool_id, task_id=pool_id) \
        .node_info.node_id

    # get remote login settings for the user
    remote_login_settings = batch_client.compute_node.get_remote_login_settings(
        pool_id, master_node_id)

    master_node_ip = remote_login_settings.remote_login_ip_address
    master_node_port = remote_login_settings.remote_login_port

    # build ssh tunnel command
    ssh_command = 'ssh '
    if masterui is not None:
        ssh_command += '-L ' + \
            str(masterui) + ':localhost:' + \
            str(constants._MASTER_UI_PORT) + ' '
    if webui is not None:
        ssh_command += '-L ' + \
            str(webui) + ':localhost:' + str(constants._WEBUI_PORT) + ' '
    if jupyter is not None:
        ssh_command += '-L ' + \
            str(jupyter) + ':localhost:' + str(constants._JUPYTER_PORT) + ' '
    if ports is not None:
        for port in ports:
            ssh_command += '-L ' + \
                str(port[0]) + ':localhost:' + str(port[1]) + ' '

    user = username if username is not None else '<username>'
    ssh_command += user + '@' + \
        str(master_node_ip) + ' -p ' + str(master_node_port)
    ssh_command_array = ssh_command.split()

    if (not connect):
        print('\nuse the following command to connect to your spark head node:')
        print('\n\t{}\n'.format(ssh_command))
    else:
        call(ssh_command_array)
