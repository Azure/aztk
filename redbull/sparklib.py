from . import util

import random
import datetime

import azure.batch.models as batch_models

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
    start_task_commands = [
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',
        'chmod -R 777 $SPARK_HOME',
        'exit 0'
    ]

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
        app_file_name,
        username,
        password):

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
    :param username: The username to access the head node via ssh
    :type username: string
    :param password: The password to access the head node via ssh
    :type password: string

    """

    # set multi-instance task id 
    # TODO create a real GUID instead of just a random number
    deployment_suffix = str(random.randint(0,1000000))
    multiinstance_task_id= 'az-spark-' + deployment_suffix

    # Upload app resource files to blob storage
    app_resource_file = \
        util.upload_file_to_container(
            blob_client, container_name = app_id, file_path = app_file_path)
 
    # configure multi-instance task commands
    coordination_commands = [
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
        # create a 'slaves' file from the slaves.template in $SPARK_HOME/conf
        'cp $SPARK_HOME/conf/slaves.template $SPARK_HOME/conf/slaves'
        # create a new line in the slaves file
        'echo >> $SPARK_HOME/conf/slaves',
        # add batch pool ips to newly created slaves files
        'IFS="," read -r -a workerips <<< $AZ_BATCH_HOST_LIST',
        'for index in "${!workerips[@]}"',
        'do echo "${workerips[index]}" >> $SPARK_HOME/conf/slaves',
        'echo "${workerips[index]}"',
        'done'
    ]
    application_commands = [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',
        # kick off start-all spark command as a bg process 
        '($SPARK_HOME/sbin/start-all.sh &)',
        # execute spark-submit on the specified app 
        '$SPARK_HOME/bin/spark-submit ' +
            '--master spark://${AZ_BATCH_MASTER_NODE%:*}:7077 ' +
            '$AZ_BATCH_TASK_WORKING_DIR/' + app_file_name
    ]

    # Get pool size
    pool = batch_client.pool.get(pool_id)
    pool_size = pool.target_dedicated

    # Create multi-instance task
    task = batch_models.TaskAddParameter(
        id = multiinstance_task_id,
        command_line = util.wrap_commands_in_shell(application_commands),
        resource_files = [app_resource_file],
        run_elevated = False,
        multi_instance_settings = batch_models.MultiInstanceSettings(
            number_of_instances = pool_size,
            coordination_command_line = util.wrap_commands_in_shell(coordination_commands),
            common_resource_files = []))

    # Add task to batch job (which has the same name as pool_id)
    job_id = pool_id
    batch_client.task.add(job_id = job_id, task = task)

    # Wait for the app to finish
    util.wait_for_tasks_to_complete(
        batch_client,
        job_id,
        datetime.timedelta(minutes=60))

    # Get master node id from task
    master_node_id = batch_client.task \
        .get(job_id=pool_id, task_id=multiinstance_task_id) \
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
    ssh_tunnel_command = "ssh -L 8080:localhost:8080 " + \
        username + "@" + str(master_node_ip) + " -p " + str(master_node_port)

    print('\nuse the following command to connect to your spark head node:')
    print()
    print('\t%s' % ssh_tunnel_command)
    print()


