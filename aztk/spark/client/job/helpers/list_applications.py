from azure.batch.models import BatchErrorException

from aztk import error
from aztk.spark import models
from aztk.utils import helpers


def _list_applications(core_job_operations, job_id):
    recent_run_job = core_job_operations.get_recent_job(job_id)
    # get application names from Batch job metadata
    applications = {}
    for metadata_item in recent_run_job.metadata:
        if metadata_item.name == "applications":
            for app_name in metadata_item.value.split("\n"):
                applications[app_name] = None

    tasks = core_job_operations.list_tasks(job_id)
    for task in tasks:
        if task.id != job_id:
            applications[task.id] = task

    return applications


# TODO: this needs to be changed to return a list of aztk.model.Task
#       currently, it returns a dictionary indicating whether
#       a task has been scheduled or not
def list_applications(core_job_operations, job_id):
    try:
        applications = _list_applications(core_job_operations, job_id)
        for item in applications:
            if applications[item]:
                applications[item] = models.Application(applications[item])
        return applications
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
