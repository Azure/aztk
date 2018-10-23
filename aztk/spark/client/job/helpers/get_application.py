import azure.batch.models as batch_models
from azure.batch.models import BatchErrorException

from aztk import error
from aztk.spark import models
from aztk.utils import helpers


def _get_application(core_operations, job_id, application_name):
    # info about the app
    recent_run_job = core_operations.get_recent_job(job_id)
    scheduling_target = core_operations.get_cluster_configuration(job_id).scheduling_target
    if scheduling_target is not models.SchedulingTarget.Any:
        return core_operations.get_task_from_table(job_id, application_name)
    try:
        return core_operations.get_batch_task(id=recent_run_job.id, task_id=application_name)
    except batch_models.BatchErrorException:
        raise error.AztkError(
            "The Spark application {0} is still being provisioned or does not exist.".format(application_name))


def get_application(core_operations, job_id, application_name):
    try:
        return models.Application(_get_application(core_operations, job_id, application_name))
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
