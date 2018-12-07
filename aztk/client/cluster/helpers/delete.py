from azure.batch.models import BatchErrorException
from msrest.exceptions import ClientRequestError

from aztk.utils import BackOffPolicy, retry


def delete_pool_and_job_and_table(core_cluster_operations, pool_id: str, keep_logs: bool = False):
    """
        Delete a pool and it's associated job
        :param cluster_id: the pool to add the user to
        :return bool: deleted the pool if exists and job if exists
    """
    # job id is equal to pool id
    job_exists = True

    try:
        core_cluster_operations.batch_client.job.get(pool_id)
    except BatchErrorException:
        job_exists = False

    pool_exists = core_cluster_operations.batch_client.pool.exists(pool_id)

    table_deleted = core_cluster_operations.delete_task_table(pool_id)

    if job_exists:
        delete_object(core_cluster_operations.batch_client.job.delete, pool_id)

    if pool_exists:
        delete_object(core_cluster_operations.batch_client.pool.delete, pool_id)

    if not keep_logs:
        cluster_data = core_cluster_operations.get_cluster_data(pool_id)
        cluster_data.delete_container(pool_id)

    return job_exists or pool_exists or table_deleted


@retry(retry_count=4, retry_interval=1, backoff_policy=BackOffPolicy.exponential, exceptions=(ClientRequestError))
def delete_object(function, *args, **kwargs):
    return function(*args, **kwargs)
