from __future__ import print_function
import datetime
import io
import os
import time
import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth
import azure.batch.models as batch_models
import azure.storage.blob as blob
from .version import __version__
from . import constants, log, error


_STANDARD_OUT_FILE_NAME = 'stdout.txt'
_STANDARD_ERROR_FILE_NAME = 'stderr.txt'


def wait_for_tasks_to_complete(job_id, timeout, batch_client):
    """
    Waits for all the tasks in a particular job to complete.
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param str job_id: The id of the job to monitor.
    :param timeout: The maximum amount of time to wait.
    :type timeout: `datetime.timedelta`
    """
    time_to_timeout_at = datetime.datetime.now() + timeout

    while datetime.datetime.now() < time_to_timeout_at:
        tasks = batch_client.task.list(job_id)

        incomplete_tasks = [task for task in tasks if
                            task.state != batch_models.TaskState.completed]
        if not incomplete_tasks:
            return
        time.sleep(5)

    raise TimeoutError("Timed out waiting for tasks to complete")


class MasterInvalidStateError(Exception):
    pass


def wait_for_master_to_be_ready(cluster_id: str, batch_client):
    master_node_id = None
    log.info("Waiting for spark master to be ready")
    start_time = datetime.datetime.now()
    while True:
        if not master_node_id:
            master_node_id = get_master_node_id(cluster_id, batch_client)
            if not master_node_id:
                time.sleep(5)
                continue

        master_node = batch_client.compute_node.get(cluster_id, master_node_id)

        if master_node.state in [batch_models.ComputeNodeState.idle,  batch_models.ComputeNodeState.running]:
            break
        elif master_node.state is batch_models.ComputeNodeState.start_task_failed:
            raise MasterInvalidStateError("Start task failed on master")
        elif master_node.state in [batch_models.ComputeNodeState.unknown, batch_models.ComputeNodeState.unusable]:
            raise MasterInvalidStateError("Master is in an invalid state")
        else:
            now = datetime.datetime.now()

            delta = now - start_time
            if delta.total_seconds() > constants.WAIT_FOR_MASTER_TIMEOUT:
                raise MasterInvalidStateError(
                    "Master didn't become ready before timeout.")

            time.sleep(10)
    time.sleep(5)


def upload_file_to_container(container_name, file_path, blob_client=None, use_full_path=False, node_path=None) -> batch_models.ResourceFile:
    """
    Uploads a local file to an Azure Blob storage container.
    :param blob_client: A blob service client.
    :type blocblob_clientk_blob_client: `azure.storage.blob.BlockBlobService`
    :param str container_name: The name of the Azure Blob storage container.
    :param str file_path: The local path to the file.
    :param str node_path: Path on the local node. By default will be the same as file_path
    :rtype: `azure.batch.models.ResourceFile`
    :return: A ResourceFile initialized with a SAS URL appropriate for Batch
    tasks.
    """
    file_path = normalize_path(file_path)
    blob_name = None
    if use_full_path:
        blob_name = file_path
    else:
        blob_name = os.path.basename(file_path)

    if not node_path:
        node_path = blob_name

    blob_client.create_container(container_name,
                                 fail_on_exist=False)

    blob_client.create_blob_from_path(container_name,
                                      blob_name,
                                      file_path)

    sas_token = blob_client.generate_blob_shared_access_signature(
        container_name,
        blob_name,
        permission=blob.BlobPermissions.READ,
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2))

    sas_url = blob_client.make_blob_url(container_name,
                                        blob_name,
                                        sas_token=sas_token)

    return batch_models.ResourceFile(file_path=node_path,
                                     blob_source=sas_url)


def print_configuration(config):
    """
    Prints the configuration being used as a dictionary
    :param config: The configuration.
    :type config: `configparser.ConfigParser`
    """
    configuration_dict = {s: dict(config.items(s)) for s in
                          config.sections() + ['DEFAULT']}

    log.info("")
    log.info("Configuration is:")
    log.info(configuration_dict)


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


def get_master_node_id(pool_id, batch_client):
    return get_master_node_id_from_pool(batch_client.pool.get(pool_id))


def create_pool_if_not_exist(pool, batch_client):
    """
    Creates the specified pool if it doesn't already exist
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param pool: The pool to create.
    :type pool: `batchserviceclient.models.PoolAddParameter`
    """
    try:
        batch_client.pool.add(pool)
    except batch_models.BatchErrorException as e:
        if e.error.code == "PoolExists":
            raise error.AztkError("A cluster with the same id already exists. Use a different id or delete the existing cluster by running \'aztk spark cluster delete --id {0}\'".format(pool.id))
        else:
            raise
    return True


def wait_for_all_nodes_state(pool, node_state, batch_client):
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
    log.info('Waiting for all nodes in pool %s to reach desired state...', pool.id)
    while True:
        # refresh pool to ensure that there is no resize error
        pool = batch_client.pool.get(pool.id)
        if pool.resize_errors is not None:
            raise RuntimeError(
                'resize error encountered for pool {}: {!r}'.format(
                    pool.id, pool.resize_errors))
        nodes = list(batch_client.compute_node.list(pool.id))

        totalNodes = pool.target_dedicated_nodes + pool.target_low_priority_nodes
        if (len(nodes) >= totalNodes and
                all(node.state in node_state for node in nodes)):
            return nodes
        time.sleep(1)


def select_latest_verified_vm_image_with_node_agent_sku(
        publisher, offer, sku_starts_with, batch_client):
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
        container_name, blob_name, permission, blob_client, expiry=None,
        timeout=None):
    """
    Create a blob sas token
    :param blob_client: The storage block blob client to use.
    :type blob_client: `azure.storage.blob.BlockBlobService`
    :param str container_name: The name of the container to upload the blob to.
    :param str blob_name: The name of the blob to upload the local file to.
    :param expiry: The SAS expiry time.
    :type expiry: `datetime.datetime`
    :param int timeout: timeout in minutes from now for expiry,
        will only be used if expiry is not specified
    :return: A SAS token
    :rtype: str
    """
    if expiry is None:
        if timeout is None:
            timeout = 30
        expiry = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=timeout)
    return blob_client.generate_blob_shared_access_signature(
        container_name, blob_name, permission=permission, expiry=expiry)


def upload_blob_and_create_sas(
        container_name, blob_name, file_name, expiry, blob_client,
        timeout=None):
    """
    Uploads a file from local disk to Azure Storage and creates a SAS for it.
    :param blob_client: The storage block blob client to use.
    :type blob_client: `azure.storage.blob.BlockBlobService`
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
    blob_client.create_container(
        container_name,
        fail_on_exist=False)

    blob_client.create_blob_from_path(
        container_name,
        blob_name,
        file_name)

    sas_token = create_sas_token(
        container_name,
        blob_name,
        permission=blob.BlobPermissions.READ,
        blob_client=None,
        expiry=expiry,
        timeout=timeout)

    sas_url = blob_client.make_blob_url(
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


def get_connection_info(pool_id, node_id, batch_client):
    """
    Get connection info of specified node in pool
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param str pool_id: The pool id to look up
    :param str node_id: The node id to look up
    """
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
    log.error("-------------------------------------------")
    log.error("Exception encountered:")
    if batch_exception.error and \
            batch_exception.error.message and \
            batch_exception.error.message.value:
        log.error(batch_exception.error.message.value)
        if batch_exception.error.values:
            log.error('')
            for mesg in batch_exception.error.values:
                log.error("%s:\t%s", mesg.key, mesg.value)
    log.error("-------------------------------------------")


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


def normalize_path(path: str)-> str:
    """
    Convert a path in a path that will work well with blob storage and unix
    It will replace \ with / and remove relative .
    """
    path = os.path.abspath(os.path.expanduser(path))
    path = path.replace('\\', '/')
    if path.startswith('./'):
        return path[2:]
    else:
        return path


def get_file_properties(job_id: str, task_id: str, file_path: str, batch_client):
    raw = batch_client.file.get_properties_from_task(
        job_id, task_id, file_path, raw=True)

    return batch_models.FileProperties(
        content_length=raw.headers["Content-Length"],
        last_modified=raw.headers["Last-Modified"],
        creation_time=raw.headers["ocp-creation-time"],
        file_mode=raw.headers["ocp-batch-file-mode"],
    )


def read_stream_as_string(stream, encoding="utf-8"):
    """
        Read stream as string
        :param stream: input stream generator
        :param str encoding: The encoding of the file. The default is utf-8.
        :return: The file content.
        :rtype: str
    """
    output = io.BytesIO()
    try:
        for data in stream:
            output.write(data)
        return output.getvalue().decode(encoding)
    finally:
        output.close()
    raise RuntimeError('could not write data to stream or decode bytes')
