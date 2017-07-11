from __future__ import print_function
import datetime
import io
import os
import time
from .version import __version__
from . import azure_api, constants

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth
import azure.batch.models as batch_models
import azure.storage.blob as blob

_STANDARD_OUT_FILE_NAME = 'stdout.txt'
_STANDARD_ERROR_FILE_NAME = 'stderr.txt'


def wait_for_tasks_to_complete(job_id, timeout):
    """
    Waits for all the tasks in a particular job to complete.
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param str job_id: The id of the job to monitor.
    :param timeout: The maximum amount of time to wait.
    :type timeout: `datetime.timedelta`
    """
    batch_client = azure_api.get_batch_client()

    time_to_timeout_at = datetime.datetime.now() + timeout

    while datetime.datetime.now() < time_to_timeout_at:
        tasks = batch_client.task.list(job_id)

        incomplete_tasks = [task for task in tasks if
                            task.state != batch_models.TaskState.completed]
        if not incomplete_tasks:
            return
        time.sleep(5)

    raise TimeoutError("Timed out waiting for tasks to complete")


def upload_file_to_container(container_name, file_path, use_full_path) -> batch_models.ResourceFile:
    """
    Uploads a local file to an Azure Blob storage container.
    :param block_blob_client: A blob service client.
    :type block_blob_client: `azure.storage.blob.BlockBlobService`
    :param str container_name: The name of the Azure Blob storage container.
    :param str file_path: The local path to the file.
    :rtype: `azure.batch.models.ResourceFile`
    :return: A ResourceFile initialized with a SAS URL appropriate for Batch
    tasks.
    """
    block_blob_client = azure_api.get_blob_client()

    blob_name = None
    if (use_full_path):
        blob_name = file_path
    else:
        blob_name = os.path.basename(file_path)

    block_blob_client.create_container(container_name,
                                       fail_on_exist=False)

    block_blob_client.create_blob_from_path(container_name,
                                            blob_name,
                                            file_path)

    sas_token = block_blob_client.generate_blob_shared_access_signature(
        container_name,
        blob_name,
        permission=blob.BlobPermissions.READ,
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2))

    sas_url = block_blob_client.make_blob_url(container_name,
                                              blob_name,
                                              sas_token=sas_token)

    return batch_models.ResourceFile(file_path=blob_name,
                                     blob_source=sas_url)


def print_configuration(config):
    """
    Prints the configuration being used as a dictionary
    :param config: The configuration.
    :type config: `configparser.ConfigParser`
    """
    configuration_dict = {s: dict(config.items(s)) for s in
                          config.sections() + ['DEFAULT']}

    print("\nConfiguration is:")
    print(configuration_dict)

def get_master_node_id_from_pool(pool: batch_models.CloudPool):
    """
        :returns: the id of the node that is the assigned master of this pool
    """
    if pool.metadata is None:
        return None

    for metadata in pool.metadata:
        if metadata.name == constants.MASTER_NODE_METADATA_KEY:
            return metadata.value

    return None

def get_master_node_id(pool_id):
    batch_client = azure_api.get_batch_client()
    return get_master_node_id_from_pool(batch_client.pool.get(pool_id))


def create_pool_if_not_exist(pool, wait=True):
    """
    Creates the specified pool if it doesn't already exist
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param pool: The pool to create.
    :type pool: `batchserviceclient.models.PoolAddParameter`
    """

    batch_client = azure_api.get_batch_client()

    try:
        batch_client.pool.add(pool)
        if wait:
            wait_for_all_nodes_state(batch_client, pool, frozenset(
                (batch_models.ComputeNodeState.start_task_failed,
                 batch_models.ComputeNodeState.unusable,
                 batch_models.ComputeNodeState.idle)
            ))
            print("Created pool: {}".format(pool.id))
        else:
            print("Creating pool: {}".format(pool.id))
    except batch_models.BatchErrorException as e:
        if e.error.code != "PoolExists":
            raise
        else:
            print("Pool {!r} already exists.".format(pool.id))


def wait_for_all_nodes_state(pool, node_state):
    """
    Waits for all nodes in pool to reach any specified state in set
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param pool: The pool containing the node.
    :type pool: `batchserviceclient.models.CloudPool`
    :param set node_state: node states to wait for
    :rtype: list
    :return: list of `batchserviceclient.models.ComputeNode`
    """
    batch_client = azure_api.get_batch_client()

    print('Waiting for all nodes in pool {} to reach desired state...'.format(pool.id))
    while True:
        # refresh pool to ensure that there is no resize error
        pool = batch_client.pool.get(pool.id)
        if pool.resize_errors is not None:
            raise RuntimeError(
                'resize error encountered for pool {}: {!r}'.format(
                    pool.id, pool.resize_error))
        nodes = list(batch_client.compute_node.list(pool.id))

        totalNodes = pool.target_dedicated_nodes + pool.target_low_priority_nodes
        if (len(nodes) >= totalNodes and
                all(node.state in node_state for node in nodes)):
            return nodes
        '''
        print('waiting for {} nodes to reach desired state...'.format(
            pool.target_dedicated))
        '''
        time.sleep(1)


def select_latest_verified_vm_image_with_node_agent_sku(
        publisher, offer, sku_starts_with):
    """
    Select the latest verified image that Azure Batch supports given
    a publisher, offer and sku (starts with filter).
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param str publisher: vm image publisher
    :param str offer: vm image offer
    :param str sku_starts_with: vm sku starts with filter
    :rtype: tuple
    :return: (node agent sku id to use, vm image ref to use)
    """
    batch_client = azure_api.get_batch_client()

    # get verified vm image list and node agent sku ids from service
    node_agent_skus = batch_client.account.list_node_agent_skus()

    # pick the latest supported sku
    skus_to_use = [
        (sku, image_ref) for sku in node_agent_skus for image_ref in sorted(
            sku.verified_image_references, key=lambda item: item.sku)
        if image_ref.publisher.lower() == publisher.lower() and
        image_ref.offer.lower() == offer.lower() and
        image_ref.sku.startswith(sku_starts_with)
    ]

    # skus are listed in reverse order, pick first for latest
    sku_to_use, image_ref_to_use = skus_to_use[0]
    return (sku_to_use.id, image_ref_to_use)


def create_sas_token(
        container_name, blob_name, permission, expiry=None,
        timeout=None):
    """
    Create a blob sas token
    :param block_blob_client: The storage block blob client to use.
    :type block_blob_client: `azure.storage.blob.BlockBlobService`
    :param str container_name: The name of the container to upload the blob to.
    :param str blob_name: The name of the blob to upload the local file to.
    :param expiry: The SAS expiry time.
    :type expiry: `datetime.datetime`
    :param int timeout: timeout in minutes from now for expiry,
        will only be used if expiry is not specified
    :return: A SAS token
    :rtype: str
    """
    block_blob_client = azure_api.get_blob_client()

    if expiry is None:
        if timeout is None:
            timeout = 30
        expiry = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=timeout)
    return block_blob_client.generate_blob_shared_access_signature(
        container_name, blob_name, permission=permission, expiry=expiry)


def upload_blob_and_create_sas(
        container_name, blob_name, file_name, expiry,
        timeout=None):
    """
    Uploads a file from local disk to Azure Storage and creates a SAS for it.
    :param block_blob_client: The storage block blob client to use.
    :type block_blob_client: `azure.storage.blob.BlockBlobService`
    :param str container_name: The name of the container to upload the blob to.
    :param str blob_name: The name of the blob to upload the local file to.
    :param str file_name: The name of the local file to upload.
    :param expiry: The SAS expiry time.
    :type expiry: `datetime.datetime`
    :param int timeout: timeout in minutes from now for expiry,
        will only be used if expiry is not specified
    :return: A SAS URL to the blob with the specified expiry time.
    :rtype: str
    """
    block_blob_client = azure_api.get_blob_client()

    block_blob_client.create_container(
        container_name,
        fail_on_exist=False)

    block_blob_client.create_blob_from_path(
        container_name,
        blob_name,
        file_name)

    sas_token = create_sas_token(
        block_blob_client,
        container_name,
        blob_name,
        permission=blob.BlobPermissions.READ,
        expiry=expiry,
        timeout=timeout)

    sas_url = block_blob_client.make_blob_url(
        container_name,
        blob_name,
        sas_token=sas_token)

    return sas_url


def wrap_commands_in_shell(commands):
    """
    Wrap commands in a shell
    :param list commands: list of commands to wrap
    :param str ostype: OS type, linux or windows
    :rtype: str
    :return: a shell wrapping commands
    """
    return '/bin/bash -c \'set -e; set -o pipefail; {}; wait\''.format(
        ';'.join(commands))


def get_connection_info(pool_id, node_id):
    """
    Get connection info of specified node in pool
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param str pool_id: The pool id to look up
    :param str node_id: The node id to look up
    """
    batch_client = azure_api.get_batch_client()

    rls = batch_client.compute_node.get_remote_login_settings(
        pool_id, node_id)
    remote_ip = rls.remote_login_ip_address
    ssh_port = str(rls.remote_login_port)
    return (remote_ip, ssh_port)


def print_batch_exception(batch_exception):
    """
    Prints the contents of the specified Batch exception.
    :param batch_exception:
    """
    print('-------------------------------------------')
    print('Exception encountered:')
    if batch_exception.error and \
            batch_exception.error.message and \
            batch_exception.error.message.value:
        print(batch_exception.error.message.value)
        if batch_exception.error.values:
            print()
            for mesg in batch_exception.error.values:
                print('{}:\t{}'.format(mesg.key, mesg.value))
    print('-------------------------------------------')


def get_cluster_total_target_nodes(pool):
    """
    Get the total number of target nodes (dedicated + low pri) for the pool
    """
    return pool.target_dedicated_nodes + pool.target_low_priority_nodes


def get_cluster_total_current_nodes(pool):
    """
    Get the total number of current nodes (dedicated + low pri) in the pool
    """
    return pool.current_dedicated_nodes + pool.current_low_priority_nodes
