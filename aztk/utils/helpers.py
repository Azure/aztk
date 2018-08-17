from __future__ import print_function

import datetime
import io
import logging
import os
import re
import time

import azure.batch.models as batch_models
import azure.common
import azure.storage.blob as blob
import yaml

import aztk.models
from aztk import error

_STANDARD_OUT_FILE_NAME = "stdout.txt"
_STANDARD_ERROR_FILE_NAME = "stderr.txt"


def is_gpu_enabled(vm_size: str):
    return bool(re.search("nv|nc", vm_size, flags=re.IGNORECASE))


def get_cluster(cluster_id, batch_client):
    pool = batch_client.pool.get(cluster_id)
    nodes = batch_client.compute_node.list(pool_id=cluster_id)

    return aztk.models.Cluster(pool, nodes)


def wait_for_tasks_to_complete(job_id, batch_client):
    """
    Waits for all the tasks in a particular job to complete.
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param str job_id: The id of the job to monitor.
    """
    while True:
        tasks = batch_client.task.list(job_id)

        incomplete_tasks = [task for task in tasks if task.state != batch_models.TaskState.completed]
        if not incomplete_tasks:
            return
        time.sleep(5)


def wait_for_task_to_complete(job_id: str, task_id: str, batch_client):
    """
    Waits for a particular task in a job to complete.
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param str job_id: The id of the job to monitor.
    :param str job_id: The id of the task to monitor.
    """
    while True:
        task = batch_client.task.get(job_id=job_id, task_id=task_id)
        if task.state != batch_models.TaskState.completed:
            time.sleep(5)
        else:
            return


def upload_text_to_container(container_name: str, application_name: str, content: str, file_path: str,
                             blob_client=None) -> batch_models.ResourceFile:
    blob_name = file_path
    blob_path = application_name + "/" + blob_name    # + '/' + time_stamp + '/' + blob_name
    blob_client.create_container(container_name, fail_on_exist=False)
    blob_client.create_blob_from_text(container_name, blob_path, content)

    sas_token = blob_client.generate_blob_shared_access_signature(
        container_name,
        blob_path,
        permission=blob.BlobPermissions.READ,
        expiry=datetime.datetime.utcnow() + datetime.timedelta(days=365),
    )

    sas_url = blob_client.make_blob_url(container_name, blob_path, sas_token=sas_token)

    return batch_models.ResourceFile(file_path=blob_name, blob_source=sas_url)


def upload_file_to_container(container_name,
                             application_name,
                             file_path,
                             blob_client=None,
                             use_full_path=False,
                             node_path=None) -> batch_models.ResourceFile:
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
        blob_name = file_path.strip("/")
    else:
        blob_name = os.path.basename(file_path)
        blob_path = application_name + "/" + blob_name

    if not node_path:
        node_path = blob_name

    blob_client.create_container(container_name, fail_on_exist=False)

    blob_client.create_blob_from_path(container_name, blob_path, file_path)

    sas_token = blob_client.generate_blob_shared_access_signature(
        container_name,
        blob_path,
        permission=blob.BlobPermissions.READ,
        expiry=datetime.datetime.utcnow() + datetime.timedelta(days=7),
    )

    sas_url = blob_client.make_blob_url(container_name, blob_path, sas_token=sas_token)

    return batch_models.ResourceFile(file_path=node_path, blob_source=sas_url)


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
            raise error.AztkError(
                "A cluster with the same id already exists. Use a different id or delete the existing cluster")
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
    while True:
        # refresh pool to ensure that there is no resize error
        pool = batch_client.pool.get(pool.id)
        if pool.resize_errors is not None:
            raise RuntimeError("resize error encountered for pool {}: {!r}".format(pool.id, pool.resize_errors))
        nodes = list(batch_client.compute_node.list(pool.id))

        totalNodes = pool.target_dedicated_nodes + pool.target_low_priority_nodes
        if len(nodes) >= totalNodes and all(node.state in node_state for node in nodes):
            return nodes
        time.sleep(1)


def select_latest_verified_vm_image_with_node_agent_sku(publisher, offer, sku_starts_with, batch_client):
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
    skus_to_use = [(sku, image_ref)
                   for sku in node_agent_skus
                   for image_ref in sorted(sku.verified_image_references, key=lambda item: item.sku)
                   if image_ref.publisher.lower() == publisher.lower() and image_ref.offer.lower() == offer.lower()
                   and image_ref.sku.startswith(sku_starts_with)]

    # skus are listed in reverse order, pick first for latest
    sku_to_use, image_ref_to_use = skus_to_use[0]
    return (sku_to_use.id, image_ref_to_use)


def create_sas_token(container_name, blob_name, permission, blob_client, expiry=None, timeout=None):
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
        expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)
    return blob_client.generate_blob_shared_access_signature(
        container_name, blob_name, permission=permission, expiry=expiry)


def upload_blob_and_create_sas(container_name, blob_name, file_name, expiry, blob_client, timeout=None):
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
    blob_client.create_container(container_name, fail_on_exist=False)

    blob_client.create_blob_from_path(container_name, blob_name, file_name)

    sas_token = create_sas_token(
        container_name,
        blob_name,
        permission=blob.BlobPermissions.READ,
        blob_client=None,
        expiry=expiry,
        timeout=timeout,
    )

    sas_url = blob_client.make_blob_url(container_name, blob_name, sas_token=sas_token)

    return sas_url


def wrap_commands_in_shell(commands):
    """
    Wrap commands in a shell
    :param list commands: list of commands to wrap
    :param str ostype: OS type, linux or windows
    :rtype: str
    :return: a shell wrapping commands
    """
    return "/bin/bash -c 'set -e; set -o pipefail; {}; wait'".format(";".join(commands))


def get_connection_info(pool_id, node_id, batch_client):
    """
    Get connection info of specified node in pool
    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param str pool_id: The pool id to look up
    :param str node_id: The node id to look up
    """
    rls = batch_client.compute_node.get_remote_login_settings(pool_id, node_id)
    remote_ip = rls.remote_login_ip_address
    ssh_port = str(rls.remote_login_port)
    return (remote_ip, ssh_port)


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


def normalize_path(path: str) -> str:
    """
    Convert a path in a path that will work well with blob storage and unix
    It will replace backslashes with forwardslashes and return absolute paths.
    """
    path = os.path.abspath(os.path.expanduser(path))
    path = path.replace("\\", "/")
    if path.startswith("./"):
        return path[2:]
    else:
        return path


def get_file_properties(job_id: str, task_id: str, file_path: str, batch_client):
    raw = batch_client.file.get_properties_from_task(job_id, task_id, file_path, raw=True)

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
    raise RuntimeError("could not write data to stream or decode bytes")


def format_batch_exception(batch_exception):
    """
    Returns the contents of the specified Batch exception.
    :param batch_exception:
    """
    l = []
    l.append("-------------------------------------------")
    if batch_exception.error and batch_exception.error.message and batch_exception.error.message.value:
        l.append(batch_exception.error.message.value)
        if batch_exception.error.values:
            l.append("")
            for mesg in batch_exception.error.values:
                l.append("{0}:\t{1}".format(mesg.key, mesg.value))
    l.append("-------------------------------------------")

    return "\n".join(l)


def save_cluster_config(cluster_config, blob_client):
    blob_path = "config.yaml"
    content = yaml.dump(cluster_config)
    container_name = cluster_config.cluster_id
    blob_client.create_container(container_name, fail_on_exist=False)
    blob_client.create_blob_from_text(container_name, blob_path, content)


def read_cluster_config(cluster_id: str, blob_client: blob.BlockBlobService):
    blob_path = "config.yaml"
    try:
        result = blob_client.get_blob_to_text(cluster_id, blob_path)
        return yaml.load(result.content)
    except azure.common.AzureMissingResourceHttpError:
        logging.warning("Cluster %s doesn't have cluster configuration in storage", cluster_id)
    except yaml.YAMLError:
        logging.warning("Cluster %s contains invalid cluster configuration in blob", cluster_id)


def bool_env(value: bool):
    """
    Takes a boolean value(or None) and return the serialized version to be used as an environment variable

    Examples:
        >>> bool_env(True)
        "true"

        >>> bool_env(False)
        "false"

        >>> bool_env(None)
        "false"
    """

    if value is True:
        return "true"
    else:
        return "false"
