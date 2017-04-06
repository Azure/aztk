import util

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os
import datetime

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth 
import azure.batch.models as batch_models
import azure.storage.blob as blob

deployment_suffix       = '-42-dsvm'

# config file path
_CONFIG_PATH            = os.path.join(os.path.dirname(__file__), '../configuration.cfg')

# pool configs
_VM_SIZE                = 'Standard_D2_v2'
_VM_COUNT               = 5
_POOL_ID                = 'spark-test-pool' + deployment_suffix
_JOB_ID                 = 'spark-test-job' + deployment_suffix
_MULTIINSTANCE_TASK_ID  = 'multiinstance-spark-task' + deployment_suffix

# vm image
_VM_IMAGE_OPTIONS = {
    'ubuntu': {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '16.04'
    },
    'dsvm': {
        'publisher': 'microsoft-ads',
        'offer': 'linux-data-science-vm',
        'sku': 'linuxdsvm'
    }
}
_VM_IMAGE = _VM_IMAGE_OPTIONS['dsvm']

# tasks variables
_CONTAINER_NAME         = 'sparkresourcesfiles'
_START_TASK_NAME        = 'spark-install.sh'
_START_TASK_PATH        = os.path.join('resource-files/dsvm-image', _START_TASK_NAME)
_APPLICATION_TASK_NAME  = 'spark-start.sh'
_APPLICATION_TASK_PATH  = os.path.join('resource-files/dsvm-image', _APPLICATION_TASK_NAME)
_COORDINATION_TASK_NAME = 'spark-connect.sh'
_COORDINATION_TASK_PATH = os.path.join('resource-files/dsvm-image', _COORDINATION_TASK_NAME)

# ssh user variables
_USERNAME               = 'jiata'
_PASSWORD               = 'B1gComput#'

def connect(batch_client):
    """
    Creates a batch user for the master node, retrieves
    the user's login settings and generates ssh tunnel command

    :param batch_client: the batch client
    :type batch_client: azure.batch.BatchServiceClient
    :return string: the ssh tunnel command to run
    """

    # get master node id from task
    master_node_id = batch_client.task.get(_JOB_ID, _MULTIINSTANCE_TASK_ID).node_info.node_id

    # create new ssh user for the master node
    batch_client.compute_node.add_user(
        _POOL_ID,
        master_node_id,
        batch_models.ComputeNodeUser(
            _USERNAME,
            is_admin = True,
            password = _PASSWORD))

    print('\nuser {} added to node {} in pool {}'.format(_USERNAME, master_node_id, _POOL_ID))

    # get remote login settings for the user
    remote_login_settings = batch_client.compute_node.get_remote_login_settings(
        _POOL_ID, master_node_id)

    master_node_ip = remote_login_settings.remote_login_ip_address
    master_node_port = remote_login_settings.remote_login_port

    # build ssh tunnel command
    ssh_tunnel_command = "ssh -L 8080:localhost:8080 -L 8888:localhost:8888 " + \
        _USERNAME + "@" + str(master_node_ip) + " -p " + str(master_node_port)

    return ssh_tunnel_command

def submit_task(batch_client, blob_client,
        coordination_command_resource_file, application_command_resource_file):
    """
    Submits a job to the Azure Batch service and adds a task

    :param batch_client: the batch client
    :type batch_client: azure.batch.BatchServiceClient
    :param blob_client: the storage blob client
    :type blob_client: azure.storage.BlobBlockService
    :param coordination_command_resource_file: 
        the resource file that the coordination command will use
    :type coordination_command_resource_file: azure.batch.models.ResourceFile
    :param application_command_resource_file: 
        the resource file that the application command will use
    :type application_command_resource_file: azure.batch.models.ResourceFile
    """

    application_command = "/bin/sh -c $AZ_BATCH_TASK_WORKING_DIR/" + _APPLICATION_TASK_NAME
    coordination_command = "/bin/sh -c $AZ_BATCH_TASK_DIR/" + _COORDINATION_TASK_NAME

    # create multi-instance task
    task = batch_models.TaskAddParameter(
        id = _MULTIINSTANCE_TASK_ID,
        command_line = application_command,
        resource_files = [application_command_resource_file],
        run_elevated = False,
        multi_instance_settings = batch_models.MultiInstanceSettings(
            number_of_instances = _VM_COUNT,
            coordination_command_line = coordination_command,
            common_resource_files = [coordination_command_resource_file]))

    # add task to job
    batch_client.task.add(job_id = _JOB_ID, task = task)

def submit_job(batch_client):
    """
    Submits a job to the Azure Batch service and adds a task

    :param batch_client: the batch client
    :type batch_client: azure.batch.BatchServiceClient
    """

    #create job
    job = batch_models.JobAddParameter(
        id = _JOB_ID,
        pool_info=batch_models.PoolInformation(pool_id = _POOL_ID))

    # add job to batch
    batch_client.job.add(job)

def create_pool(batch_client, blob_client, start_task_resource_file):
    """
    Create an Azure Batch pool

    :param batch_client: the batch client
    :type batch_client: azure.batch.BatchServiceClient
    :param blob_client: the storage blob client
    :type blob_client: azure.storage.blob.BlockBlobService
    :param start_task_resource_file: the resource file that the start task will use
    :type start_task_resource_file: azure.batch.models.ResourceFile
    """
    
    # Get a verified node agent sku
    sku_to_use, image_ref_to_use = \
        util.select_latest_verified_vm_image_with_node_agent_sku(
            batch_client, _VM_IMAGE['publisher'], _VM_IMAGE['offer'], _VM_IMAGE['sku'])

    # Confiure the pool
    pool = batch_models.PoolAddParameter(
        id = _POOL_ID,
        virtual_machine_configuration = batch_models.VirtualMachineConfiguration(
            image_reference = image_ref_to_use,
            node_agent_sku_id = sku_to_use),
        vm_size = _VM_SIZE,
        target_dedicated = _VM_COUNT,
        start_task = batch_models.StartTask(
            command_line = "/bin/sh -c " + _START_TASK_NAME,
            resource_files = [start_task_resource_file],
            run_elevated = True,
            wait_for_success = True),
        enable_inter_node_communication = True,
        max_tasks_per_node = 1)

    # Create the pool
    util.create_pool_if_not_exist(batch_client, pool)

if __name__ == '__main__':
    """
    Start script
    """
    global_config = configparser.ConfigParser()
    global_config.read(_CONFIG_PATH)

    util.print_configuration(global_config)

'''
    # Set up the configuration
    batch_account_key = global_config.get('Batch', 'batchaccountkey')
    batch_account_name = global_config.get('Batch', 'batchaccountname')
    batch_service_url = global_config.get('Batch', 'batchserviceurl')
    storage_account_key = global_config.get('Storage', 'storageaccountkey')
    storage_account_name = global_config.get('Storage', 'storageaccountname')
    storage_account_suffix = global_config.get('Storage', 'storageaccountsuffix')

    # Set up SharedKeyCredentials
    credentials = batch_auth.SharedKeyCredentials(
        batch_account_name,
        batch_account_key)

    # Set up Batch Client
    batch_client = batch.BatchServiceClient(
        credentials,
        base_url=batch_service_url)

    # Set retry policy
    batch_client.config.retry_policy.retries = 5

    # Set up BlockBlobStorage
    blob_client = blob.BlockBlobService(
        account_name = storage_account_name,
        account_key = storage_account_key,
        endpoint_suffix = storage_account_suffix)

    """
    Upload resource files to storage container
    """

    # Upload start task resource files to blob storage
    start_task_resource_file = \
        util.upload_file_to_container(
            blob_client, _CONTAINER_NAME, _START_TASK_PATH)

    # Upload Coordination command resource files to blob storage
    coordination_command_resource_file = \
        util.upload_file_to_container(
            blob_client, _CONTAINER_NAME, _COORDINATION_TASK_PATH)

    # Upload Application command resource files to blob storage
    application_command_resource_file = \
        util.upload_file_to_container(
            blob_client, _CONTAINER_NAME, _APPLICATION_TASK_PATH)
    
    """
    Start pool, Start Job, Start task!
    """

    # Create a pool if the pool doesn't already exist
    create_pool(
        batch_client, 
        blob_client, 
        start_task_resource_file)

    # Submit a job
    submit_job(batch_client)

    # Submit a task
    submit_task(
        batch_client, 
        blob_client, 
        coordination_command_resource_file,
        application_command_resource_file)

    # wait for the job to finish
    util.wait_for_tasks_to_complete(
        batch_client,
        _JOB_ID,
        datetime.timedelta(minutes=60))

    """
    Return user/credentials to ssh tunnel into Master node
    """

    # Create user and get her credentials to create the ssh tunnel
    ssh_tunnel_command = connect(batch_client)
    print('\nuse the following command to get started!')
    print(ssh_tunnel_command)
    print()

'''
