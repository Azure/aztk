import time

import azure.batch.models as batch_models
from azure.batch.models import BatchErrorException

from aztk import error
from aztk.utils import helpers


def _wait_until_job_finished(core_job_operations, job_id):
    job_state = core_job_operations.batch_client.job_schedule.get(job_id).state

    while job_state not in [batch_models.JobScheduleState.completed, batch_models.JobScheduleState.terminating]:
        time.sleep(3)
        job_state = core_job_operations.batch_client.job_schedule.get(job_id).state


def wait_until_job_finished(core_job_operations, job_id):
    try:
        _wait_until_job_finished(core_job_operations, job_id)
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
