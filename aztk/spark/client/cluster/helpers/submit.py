import azure.batch.models as batch_models
import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.error import AztkError
from aztk.spark import models
from aztk.utils import helpers


def __get_node(core_cluster_operations, node_id: str, cluster_id: str) -> batch_models.ComputeNode:
    return core_cluster_operations.batch_client.compute_node.get(cluster_id, node_id)


def affinitize_task_to_master(core_cluster_operations, spark_cluster_operations, cluster_id, task):
    cluster = spark_cluster_operations.get(cluster_id)
    if cluster.master_node_id is None:
        raise AztkError("Master has not yet been selected. Please wait until the cluster is finished provisioning.")
    master_node = core_cluster_operations.batch_client.compute_node.get(
        pool_id=cluster_id, node_id=cluster.master_node_id)
    task.affinity_info = batch_models.AffinityInformation(affinity_id=master_node.affinity_id)
    return task


def submit_application(core_cluster_operations,
                       spark_cluster_operations,
                       cluster_id,
                       application,
                       remote: bool = False,
                       wait: bool = False):
    """
    Submit a spark app
    """
    task = spark_cluster_operations._generate_application_task(core_cluster_operations, cluster_id, application, remote)
    task = affinitize_task_to_master(core_cluster_operations, spark_cluster_operations, cluster_id, task)

    # Add task to batch job (which has the same name as cluster_id)
    job_id = cluster_id
    core_cluster_operations.batch_client.task.add(job_id=job_id, task=task)

    if wait:
        helpers.wait_for_task_to_complete(
            job_id=job_id, task_id=task.id, batch_client=core_cluster_operations.batch_client)


def submit(
        core_cluster_operations,
        spark_cluster_operations,
        cluster_id: str,
        application: models.ApplicationConfiguration,
        remote: bool = False,
        wait: bool = False,
):
    try:
        submit_application(core_cluster_operations, spark_cluster_operations, cluster_id, application, remote, wait)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
