import azure.batch.models as batch_models
from msrest.exceptions import ClientRequestError

from aztk.utils import BackOffPolicy, retry


def delete_pool_and_job(core_cluster_operations, pool_id: str, keep_logs: bool = False):
    """
        Delete a pool and it's associated job
        :param cluster_id: the pool to add the user to
        :return bool: deleted the pool if exists and job if exists
    """
    # job id is equal to pool id
    job_id = pool_id
    job_exists = True

    try:
        core_cluster_operations.batch_client.job.get(job_id)
    except batch_models.batch_error.BatchErrorException:
        job_exists = False

    pool_exists = core_cluster_operations.batch_client.pool.exists(pool_id)

    if job_exists:
        delete_batch_object(core_cluster_operations.batch_client.job.delete, job_id)

    if pool_exists:
        delete_batch_object(core_cluster_operations.batch_client.pool.delete, pool_id)

    if not keep_logs:
        cluster_data = core_cluster_operations.get_cluster_data(pool_id)
        cluster_data.delete_container(pool_id)

    return job_exists or pool_exists


@retry(retry_count=4, retry_interval=1, backoff_policy=BackOffPolicy.exponential, exceptions=(ClientRequestError))
def delete_batch_object(function, *args, **kwargs):
    return function(*args, **kwargs)
