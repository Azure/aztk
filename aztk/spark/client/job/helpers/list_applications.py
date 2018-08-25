import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.spark import models
from aztk.utils import helpers

from .get_recent_job import get_recent_job


def _list_applications(core_job_operations, job_id):
    recent_run_job = get_recent_job(core_job_operations, job_id)
    # get application names from Batch job metadata
    applications = {}
    for metadata_item in recent_run_job.metadata:
        if metadata_item.name == "applications":
            for app_name in metadata_item.value.split("\n"):
                applications[app_name] = None

    # get tasks from Batch job
    for task in core_job_operations.batch_client.task.list(recent_run_job.id):
        if task.id != job_id:
            applications[task.id] = task

    return applications


def list_applications(core_job_operations, job_id):
    try:
        applications = _list_applications(core_job_operations, job_id)
        for item in applications:
            if applications[item]:
                applications[item] = models.Application(applications[item])
        return applications
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
