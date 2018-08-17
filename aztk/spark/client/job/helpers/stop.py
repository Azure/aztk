import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.utils import helpers

from .get_recent_job import get_recent_job


def _stop(core_job_operations, job_id):
    # terminate currently running job and tasks
    recent_run_job = get_recent_job(core_job_operations, job_id)
    core_job_operations.batch_client.job.terminate(recent_run_job.id)
    # terminate job_schedule
    core_job_operations.batch_client.job_schedule.terminate(job_id)


def stop(self, job_id):
    try:
        return _stop(self, job_id)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
