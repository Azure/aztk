from . import util

import random
import datetime

import azure.batch.models as batch_models

_WEBUI_PORT = 8082
_JUPYTER_PORT = 7777

def install_cmd():
    '''
    this command is run-elevated
    '''
    return [
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',
        'chmod -R 777 $SPARK_HOME',
        'exit 0'
    ]

def connect_cmd():
    return [
        # print env vars for debug
        'echo CCP_NODES:',
        'echo $CCP_NODES',
        'echo AZ_BATCH_NODE_LIST:',
        'echo $AZ_BATCH_NODE_LIST',
        'echo AZ_BATCH_HOST_LIST:',
        'echo $AZ_BATCH_HOST_LIST',
        'echo AZ_BATCH_MASTER_NODE:',
        'echo $AZ_BATCH_MASTER_NODE',
        'echo AZ_BATCH_IS_CURRENT_NODE_MASTER:',
        'echo $AZ_BATCH_IS_CURRENT_NODE_MASTER',

        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',

        # copy a 'slaves' file from the slaves.template in $SPARK_HOME/conf
        'cp $SPARK_HOME/conf/slaves.template $SPARK_HOME/conf/slaves'

        # delete existing content & create a new line in the slaves file 
        'echo > $SPARK_HOME/conf/slaves',

        # add batch pool ips to newly created slaves files
        'IFS="," read -r -a workerips <<< $AZ_BATCH_HOST_LIST',
        'for index in "${!workerips[@]}"',
        'do echo "${workerips[index]}" >> $SPARK_HOME/conf/slaves', # TODO unless node is master
        'echo "${workerips[index]}"',
        'done'
    ]

def custom_app_cmd(webui_port, app_file_name):
    return [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',

        # kick off start-all spark command as a bg process 
        '($SPARK_HOME/sbin/start-all.sh --webui-port ' + str(webui_port) + ' &)',

        # set the runtim to python 3
        'export PYSPARK_PYTHON=/usr/bin/python3',
        'export PYSPARK_DRIVER_PYTHON=python3',

        # execute spark-submit on the specified app 
        '$SPARK_HOME/bin/spark-submit ' +
            '--master spark://${AZ_BATCH_MASTER_NODE%:*}:7077 ' +
            '$AZ_BATCH_TASK_WORKING_DIR/' + app_file_name
    ]

# TODO not working
def jupyter_cmd(webui_port, jupyter_port):
    return [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',

        # kick off start-all spark command as a bg process 
        '($SPARK_HOME/sbin/start-all.sh  --webui-port ' + str(webui_port) + ' &)',

        # jupyter setup: remove auth
        'mkdir $HOME/.jupyter',
        'touch $HOME/.jupyter/jupyter_notebook_config.py',
        'echo >> $HOME/.jupyter/jupyter_notebook_config.py',
        'echo "c.NotebookApp.token=\'\'" >> $HOME/.jupyter/jupyter_notebook_config.py',
        'echo "c.NotebookApp.password=\'\'" >> $HOME/.jupyter/jupyter_notebook_config.py',

        # start jupyter notebook
        'PYSPARK_DRIVER_PYTHON=jupyter ' +
            'PYSPARK_DRIVER_PYTHON_OPTS="notebook --no-browser --port=' + str(jupyter_port) + '" ' +
            'pyspark ' +
            '--master spark://${AZ_BATCH_MASTER_NODE%:*}:7077 ' +
            '--executor-memory 6400M ' +
            '--driver-memory 6400M'
    ]

def create_cluster(
        batch_client,
        pool_id,
        vm_count,
        vm_size,
        wait = True):
    """
    Create a spark cluster

    :param batch_client: the batch client to use
    :type batch_client: 'batchserviceclient.BatchServiceClient'
    :param pool_id: The id of the pool to create
    :type pool_id: string
    :param vm_count: the number of nodes in the pool
    :type vm_count: int
    :param vm_size: The vm size to use
    :type vm_size: string
    :param wait: whether or not to wait for pool creation to compelete
    :type wait: boolean
    """

    # vm image
    _publisher = 'microsoft-ads'
    _offer = 'linux-data-science-vm'
    _sku = 'linuxdsvm'

    # start task command
    start_task_commands = install_cmd() 
    # Get a verified node agent sku
    sku_to_use, image_ref_to_use = \
        util.select_latest_verified_vm_image_with_node_agent_sku(
            batch_client, _publisher, _offer, _sku)

    # Confiure the pool
    pool = batch_models.PoolAddParameter(
        id = pool_id,
        virtual_machine_configuration = batch_models.VirtualMachineConfiguration(
            image_reference = image_ref_to_use,
            node_agent_sku_id = sku_to_use),
        vm_size = vm_size,
        target_dedicated = vm_count,
        start_task = batch_models.StartTask(
            command_line = util.wrap_commands_in_shell(start_task_commands),
            run_elevated = True,
            wait_for_success = True),
        enable_inter_node_communication = True,
        max_tasks_per_node = 1)

    # Create the pool
    util.create_pool_if_not_exist(batch_client, pool, wait=wait)

    # Create job (reuse pool_id as job_id)
    job_id = pool_id
    job = batch_models.JobAddParameter(
        id = job_id,
        pool_info=batch_models.PoolInformation(pool_id = pool_id))

    # Add job to batch
    batch_client.job.add(job)

def get_cluster_details(
        batch_client,
        pool_id):
    pool = batch_client.pool.get(pool_id)
    if (pool.state == batch_models.PoolState.deleting):
        print
    nodes = batch_client.compute_node.list(pool_id=pool_id)
    # node_specs = common.vm_helpers.get_vm_specs(pool.vm_size)
    print("State:       {}".format(pool.state.value))
    print("Node Size:   {}".format(pool.vm_size))
    # print("Node Size:   {} [{} Core(s), {} GB RAM, {} GB Disk]".format(
    #     pool.vm_size,
    #     node_specs["Cores"],
    #     node_specs["RAM"],
    #     node_specs["Disk"]))
    # print("Resources:   {} Core(s), {} GB RAM, {} GB Disk".format(
    #     node_specs["Cores"] * pool.current_dedicated,
    #     node_specs["RAM"] * pool.current_dedicated,
    #     node_specs["Disk"] * pool.current_dedicated))

    print()
    node_label = "Nodes ({})".format(pool.current_dedicated)
    print_format = '{:<34}| {:<10} | {:<21}| {:<8}'
    print_format_underline = '{:-<34}|{:-<12}|{:-<22}|{:-<8}'
    print(print_format.format(node_label, 'State', 'IP:Port', 'Master'))
    print(print_format_underline.format('', '', '', ''))

    master_node = get_master_node_id(batch_client, pool_id)

    for node in nodes:
        ip, port = util.get_connection_info(batch_client, pool_id, node.id)
        print (print_format.format(node.id, node.state.value, "{}:{}".format(ip, port),
                                       "*" if node.id == master_node else ""))
    print()

#TODO: Move this out of here
def get_master_node_id(batch_client, pool_id):
    # Currently, the jobId == poolId so this is safe to assume
    job_id = pool_id
    tasks = batch_client.task.list(job_id=job_id)
    tasks = [task for task in tasks if
             task.state != batchmodels.TaskState.completed]
    
    if (len(tasks) > 0):
        master_node_id = tasks[0].node_info.node_id
        return master_node_id

    return ""

def list_clusters(
    batch_client):
    print_format = '{:<32}|{:<10}|{:1<0}'
    print_format_underline = '{:-<32}|{:-<10}|{:-<10}'
    
    pools = batch_client.pool.list()
    print(print_format.format('Cluster', 'State', 'Nodes'))
    print(print_format_underline.format('','',''))
    for pool in pools:
        print(print_format.format(pool.id, pool.state.value, pool.current_dedicated))
    

def delete_cluster(
        batch_client,
        pool_id):
    """
    Delete a spark cluster

    :param batch_client: the batch client to use
    :type batch_client: 'batchserviceclient.BatchServiceClient'
    :param pool_id: The id of the pool to create
    :type pool_id: string
    """
    # delete pool by id
    pool = batch_client.pool.get(pool_id)

    # job id is equal to pool id
    job_id = pool_id

    if batch_client.pool.exists(pool_id) == True:
        batch_client.pool.delete(pool_id)
        batch_client.job.delete(job_id)
        print("\nThe pool, '%s', is being deleted" % pool_id)
    else:
        print("\nThe pool, '%s', does not exist" % pool_id)


def submit_app(
        batch_client,
        blob_client,
        pool_id,
        app_id,
        app_file_path,
        app_file_name):
    #TODO add 'wait' param

    """
    Submit a spark app 

    :param batch_client: the batch client to use
    :type batch_client: 'batchserviceclient.BatchServiceClient'
    :param block_blob_client: A blob service client.
    :type block_blob_client: `azure.storage.blob.BlockBlobService`
    :param pool_id: The id of the pool to submit app to 
    :type pool_id: string
    :param app_id: The id of the spark app (corresponds to batch task)
    :type app_id: string
    :param app_file_path: The path of the spark app to run
    :type app_file_path: string
    :param app_file_name: The name of the spark app file to run
    :type app_file_name: string
    """

    # Upload app resource files to blob storage
    app_resource_file = \
        util.upload_file_to_container(
            blob_client, container_name = app_id, file_path = app_file_path)

    # create application/coordination commands
    coordination_cmd = connect_cmd()
    application_cmd = custom_app_cmd(_WEBUI_PORT, app_file_name)
 
    # Get pool size
    pool = batch_client.pool.get(pool_id)
    pool_size = pool.target_dedicated

    # Create multi-instance task
    task = batch_models.TaskAddParameter(
        id = app_id,
        command_line = util.wrap_commands_in_shell(application_cmd),
        resource_files = [app_resource_file],
        run_elevated = False,
        multi_instance_settings = batch_models.MultiInstanceSettings(
            number_of_instances = pool_size,
            coordination_command_line = util.wrap_commands_in_shell(coordination_cmd),
            common_resource_files = []))

    # Add task to batch job (which has the same name as pool_id)
    job_id = pool_id
    batch_client.task.add(job_id = job_id, task = task)

    # Wait for the app to finish
    util.wait_for_tasks_to_complete(
        batch_client,
        job_id,
        datetime.timedelta(minutes=60))

def ssh_app(
        batch_client,
        pool_id,
        app_id,
        username,
        password,
        ports = None):

    """
    SSH into head node of spark-app

    :param batch_client: the batch client to use
    :type batch_client: 'batchserviceclient.BatchServiceClient'
    :param pool_id: The id of the pool to submit app to 
    :type pool_id: string
    :param app_id: The id of the spark app (corresponds to batch task)
    :type app_id: string
    :param username: The username to access the head node via ssh
    :type username: string
    :param password: The password to access the head node via ssh
    :type password: string
    :param ports: A list of ports to open tunnels to
    :type ports: [<int>]
    """

    # Get master node id from task
    master_node_id = batch_client.task \
        .get(job_id=pool_id, task_id=app_id) \
        .node_info.node_id

    # Create new ssh user for the master node
    batch_client.compute_node.add_user(
        pool_id,
        master_node_id,
        batch_models.ComputeNodeUser(
            username,
            is_admin = True,
            password = password))

    print('\nuser "{}" added to node "{}"in pool "{}"'.format(
        username, master_node_id, pool_id))

    # get remote login settings for the user
    remote_login_settings = batch_client.compute_node.get_remote_login_settings(
        pool_id, master_node_id)

    master_node_ip = remote_login_settings.remote_login_ip_address
    master_node_port = remote_login_settings.remote_login_port

    # build ssh tunnel command
    ssh_command = "ssh "
    for port in ports:
        ssh_command += "-L " + str(port) + ":localhost:" + str(port) + " "
    ssh_command += username + "@" + str(master_node_ip) + " -p " + str(master_node_port)

    print('\nuse the following command to connect to your spark head node:')
    print()
    print('\t%s' % ssh_command)
    print()

def list_apps(
        batch_client,
        pool_id):
    """
    List all spark apps for a given cluster

    :param batch_client: the batch client to use
    :type batch_client: 'batchserviceclient.BatchServiceClient'
    :param pool_id: The id of the pool to submit app to 
    :type pool_id: string
    """
    apps = batch_client.task.list(job_id=pool_id)
    #TODO actually print
    print(apps)

# TODO not working 
def jupyter(
        batch_client,
        pool_id,
        app_id,
        username,
        password):
    """
    Install jupyter, create app_id and open ssh tunnel

    :param batch_client: the batch client to use
    :type batch_client: 'batchserviceclient.BatchServiceClient'
    :param pool_id: The id of the pool to submit app to 
    :type pool_id: string
    :param username: The username to access the head node via ssh
    :type username: string
    :param password: The password to access the head node via ssh
    :type password: string

    """

    # create application/coordination commands
    coordination_cmd = connect_cmd()
    application_cmd = jupyter_cmd(_WEBUI_PORT, _JUPYTER_PORT)
 
    # Get pool size
    pool = batch_client.pool.get(pool_id)
    pool_size = pool.target_dedicated

    # Create multi-instance task
    task = batch_models.TaskAddParameter(
        id = app_id,
        command_line = util.wrap_commands_in_shell(application_cmd),
        resource_files = [],
        run_elevated = False,
        multi_instance_settings = batch_models.MultiInstanceSettings(
            number_of_instances = pool_size,
            coordination_command_line = util.wrap_commands_in_shell(coordination_cmd),
            common_resource_files = []))

    # Add task to batch job (which has the same name as pool_id)
    job_id = pool_id
    batch_client.task.add(job_id = job_id, task = task)

    # get job id (job id is the same as pool id)
    job_id = pool_id

    # Wait for the app to finish
    util.wait_for_tasks_to_complete(
        batch_client,
        job_id,
        datetime.timedelta(minutes=60))

    # print ssh command
    ssh_app(
        batch_client,
        pool_id,
        app_id,
        username,
        password,
        ports = [_JUPYTER_PORT, _WEBUI_PORT])
    
