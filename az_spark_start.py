import common.util as util

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os
import datetime
import random
import argparse

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth 
import azure.batch.models as batch_models
import azure.storage.blob as blob

# config file path
_config_path = os.path.join(os.path.dirname(__file__), 'configuration.cfg')

# generate random number for deployment suffix
_deployment_suffix = str(random.randint(0,1000000))

# default pool configs
_vm_size = 'Standard_D2_v2'
_vm_count = 5
_pool_id = 'az-spark-' + _deployment_suffix
_wait = True
# _job_id = 'az-spark-' + _deployment_suffix

# vm image
_publisher = 'microsoft-ads'
_offer = 'linux-data-science-vm'
_sku = 'linuxdsvm'

# storage container name
_container_name = 'azsparksetup'

# tasks variables
_start_task_name = 'spark-install.sh'
_start_task_path = os.path.join(os.path.dirname(__file__), 'common/resource-files/dsvm-image/spark-install.sh')

if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(prog="az_spark")

    parser.add_argument("--cluster-id",
                        help="the unique name of your spark cluster")
    parser.add_argument("--cluster-size", type=int, 
                        help="number of vms in your cluster")
    parser.add_argument("--cluster-vm-size", 
                        help="size of each vm in your cluster")
    parser.add_argument('--wait', dest='wait', action='store_true')
    parser.add_argument('--no-wait', dest='wait', action='store_false')
    parser.set_defaults(wait=True)

    args = parser.parse_args()
    
    print()
    if args.cluster_id is not None:
        _pool_id = args.cluster_id
        print("spark cluster id:      %s" % _pool_id)

    if args.cluster_size is not None:
        _vm_count = args.cluster_size
        print("spark cluster size:    %i" % _vm_count)

    if args.cluster_vm_size is not None:
        _vm_size = args.cluster_vm_size
        print("spark cluster vm size: %s" % _vm_size)

    if args.wait is not None:
        if args.wait == False:
            _wait = False
        print("wait for cluster:      %r" % _wait)


    # Read config file
    global_config = configparser.ConfigParser()
    global_config.read(_config_path)

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

    # Upload start task resource files to blob storage
    start_task_resource_file = \
        util.upload_file_to_container(
            blob_client, _container_name, _start_task_path)
   
    # Get a verified node agent sku
    sku_to_use, image_ref_to_use = \
        util.select_latest_verified_vm_image_with_node_agent_sku(
            batch_client, _publisher, _offer, _sku)

    # start task command
    start_task_commands = [ _start_task_name ]

    # Confiure the pool
    pool = batch_models.PoolAddParameter(
        id = _pool_id,
        virtual_machine_configuration = batch_models.VirtualMachineConfiguration(
            image_reference = image_ref_to_use,
            node_agent_sku_id = sku_to_use),
        vm_size = _vm_size,
        target_dedicated = _vm_count,
        start_task = batch_models.StartTask(
            command_line = util.wrap_commands_in_shell(start_task_commands),
            # command_line = "/bin/sh -c " + _start_task_name,
            resource_files = [start_task_resource_file],
            run_elevated = True,
            wait_for_success = True),
        enable_inter_node_communication = True,
        max_tasks_per_node = 1)

    # Create the pool
    util.create_pool_if_not_exist(batch_client, pool, wait=_wait)
