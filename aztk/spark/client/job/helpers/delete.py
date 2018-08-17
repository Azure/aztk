import azure.batch.models as batch_models
import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.utils import helpers

from .get_recent_job import get_recent_job


def _delete(core_job_operations, spark_job_operations, job_id, keep_logs: bool = False):
    recent_run_job = get_recent_job(core_job_operations, job_id)
    deleted_job_or_job_schedule = False
    # delete job
    try:
        core_job_operations.batch_client.job.delete(recent_run_job.id)
        deleted_job_or_job_schedule = True
    except batch_models.batch_error.BatchErrorException:
        pass
    # delete job_schedule
    try:
        core_job_operations.batch_client.job_schedule.delete(job_id)
        deleted_job_or_job_schedule = True
    except batch_models.batch_error.BatchErrorException:
        pass

    # delete storage container
    if keep_logs:
        cluster_data = core_job_operations.get_cluster_data(job_id)
        cluster_data.delete_container(job_id)

    return deleted_job_or_job_schedule


def delete(core_job_operations, spark_job_operations, job_id: str, keep_logs: bool = False):
    try:
        return _delete(core_job_operations, spark_job_operations, job_id, keep_logs)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
