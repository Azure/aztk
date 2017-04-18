from . import util

import random
import datetime

import azure.batch.models as batch_models

_WEBUI_PORT = 8082
_JUPYTER_PORT = 7777

def cluster_install_cmd():
    return [
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',
        'chmod -R 777 $SPARK_HOME',
        'exit 0'
    ]

def cluster_connect_cmd():
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

        # start jupyter notebook
        '(PYSPARK_DRIVER_PYTHON=/anaconda/envs/py35/bin/jupyter ' +
            'PYSPARK_DRIVER_PYTHON_OPTS="notebook --no-browser --port=' + str(jupyter_port) + '" ' +
            'pyspark ' +
            '--master spark://${MASTER_NODE%:*}:7077 ' +
            '--executor-memory 6400M ' +
            '--driver-memory 6400M &)'
    ]

def app_submit_cmd(webui_port, app_file_name):
    return [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',

        # set the runtime to python 3
        'export PYSPARK_PYTHON=/usr/bin/python3',
        'export PYSPARK_DRIVER_PYTHON=python3',

        # get master node ip
        'export MASTER_NODE=$(cat $SPARK_HOME/conf/master)',

        # execute spark-submit on the specified app 
        '$SPARK_HOME/bin/spark-submit ' +
            '--master spark://${MASTER_NODE%:*}:7077 ' + 
            '$AZ_BATCH_TASK_WORKING_DIR/' + app_file_name
    ]

def create_cluster(
        batch_client,
        pool_id,
        vm_count,
        vm_size,
        wait = True):
    """
    Create a spark cluster
    """

    # vm image
    _publisher = 'microsoft-ads'
    _offer = 'linux-data-science-vm'
    _sku = 'linuxdsvm'

    # reuse pool_id as job_id
    job_id = pool_id

    # start task command
    start_task_commands = cluster_install_cmd() 

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

    # Create the pool + create user for the pool
    util.create_pool_if_not_exist(
        batch_client, 
        pool, 
        wait)

    # Create job 
    job = batch_models.JobAddParameter(
        id = job_id,
        pool_info=batch_models.PoolInformation(pool_id = pool_id))

    # Add job to batch
    batch_client.job.add(job)

    # create application/coordination commands
    coordination_cmd = cluster_connect_cmd()
    application_cmd = cluster_start_cmd(_WEBUI_PORT, _JUPYTER_PORT)

    # reuse pool_id as multi-instance task id
    task_id = pool_id

    # Create multi-instance task
    task = batch_models.TaskAddParameter(
        id = task_id,
        command_line = util.wrap_commands_in_shell(application_cmd),
        resource_files = [],
        run_elevated = False,
        multi_instance_settings = batch_models.MultiInstanceSettings(
            number_of_instances = vm_count,
            coordination_command_line = util.wrap_commands_in_shell(coordination_cmd),
            common_resource_files = []))

    # Add task to batch job (which has the same name as pool_id)
    batch_client.task.add(job_id = job_id, task = task)

    # Wait for the app to finish
    if wait == True:
        util.wait_for_tasks_to_complete(
            batch_client,
            job_id,
            datetime.timedelta(minutes=60))

def create_user(
        batch_client,
        pool_id,
        username, 
        password):
    """
    Create a cluster user
    """

    # Get master node id from task (job and task are both named pool_id)
    master_node_id = batch_client.task \
        .get(job_id=pool_id, task_id=pool_id) \
        .node_info.node_id

    # Create new ssh user for the master node
    batch_client.compute_node.add_user(
        pool_id,
        master_node_id,
        batch_models.ComputeNodeUser(
            username,
            is_admin = True,
            password = password))


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

    # Create a local collection from the cloud enumerable
    tasks = [task for task in tasks]

    if (len(tasks) > 0):
        master_node_id = tasks[0].node_info.node_id
        return master_node_id

    return ""

def list_clusters(
        batch_client):
    print_format = '{:<34}| {:<10}| {:<20}| {:<7}'
    print_format_underline = '{:-<34}|{:-<11}|{:-<21}|{:-<7}'
    
    pools = batch_client.pool.list()
    print(print_format.format('Cluster', 'State', 'VM Size', 'Nodes'))
    print(print_format_underline.format('','','',''))
    for pool in pools:
        pool_state = pool.allocation_state.value if pool.state.value is "active" else pool.state.value
        print(print_format.format(pool.id, 
            pool_state, 
            pool.vm_size,
            pool.current_dedicated))    

def delete_cluster(
        batch_client,
        pool_id):
    """
    Delete a spark cluster
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
        app_file_name,
        wait):

    """
    Submit a spark app 
    """

    # Upload app resource files to blob storage
    app_resource_file = \
        util.upload_file_to_container(
            blob_client, container_name = app_id, file_path = app_file_path)

    # create command to submit task
    cmd = app_submit_cmd(_WEBUI_PORT, app_file_name)
 
    # Get pool size
    pool = batch_client.pool.get(pool_id)
    pool_size = pool.target_dedicated

    # Create task
    task = batch_models.TaskAddParameter(
        id=app_id,
        command_line=util.wrap_commands_in_shell(cmd),
        resource_files = [app_resource_file],
        run_elevated = False
    )

    # Add task to batch job (which has the same name as pool_id)
    job_id = pool_id
    batch_client.task.add(job_id = job_id, task = task)

    # Wait for the app to finish
    if wait == True:
        util.wait_for_tasks_to_complete(
            batch_client,
            job_id,
            datetime.timedelta(minutes=60))

def ssh(
        batch_client,
        pool_id,
        webui = None,
        jupyter = None,
        ports = None):

    """
    SSH into head node of spark-app
    :param ports: an list of local and remote ports
    :type ports: [[<local-port>, <remote-port>]]
    """

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
    ssh_command = "ssh "
    if webui is not None:
        ssh_command += "-L " + str(webui) + ":localhost:" + str(_WEBUI_PORT) + " "
    if jupyter is not None:
        ssh_command += "-L " + str(jupyter) + ":localhost:" + str(_JUPYTER_PORT) + " "
    if ports is not None:
        for port in ports:
            ssh_command += "-L " + str(port[0]) + ":localhost:" + str(port[1]) + " "
    ssh_command += "<username>@" + str(master_node_ip) + " -p " + str(master_node_port)

    print('\nuse the following command to connect to your spark head node:')
    print()
    print('\t%s' % ssh_command)
    print()

def list_apps(
        batch_client,
        pool_id):
    """
    List all spark apps for a given cluster
    """
    apps = batch_client.task.list(job_id=pool_id)
    #TODO actually print
    print(apps)

   
