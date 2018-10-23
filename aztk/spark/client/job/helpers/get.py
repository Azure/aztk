from azure.batch.models import BatchErrorException

from aztk import error
from aztk.spark import models
from aztk.utils import helpers


def _get_job(core_job_operations, job_id):
    job = core_job_operations.batch_client.job_schedule.get(job_id)
    tasks = [app for app in core_job_operations.list_tasks(id=job_id) if app.id != job_id]
    recent_run_job = core_job_operations.get_recent_job(job_id)
    pool_prefix = recent_run_job.pool_info.auto_pool_specification.auto_pool_id_prefix
    pool = nodes = None
    for cloud_pool in core_job_operations.batch_client.pool.list():
        if pool_prefix in cloud_pool.id:
            pool = cloud_pool
            break
    if pool:
        nodes = core_job_operations.batch_client.compute_node.list(pool_id=pool.id)
    return job, tasks, pool, nodes


def get_job(core_job_operations, job_id):
    try:
        job, tasks, pool, nodes = _get_job(core_job_operations, job_id)
        return models.Job(job, tasks, pool, nodes)
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
