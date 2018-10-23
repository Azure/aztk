import azure.batch.models as batch_models
from azure.batch.models import BatchErrorException

from aztk import error
from aztk.spark import models
from aztk.utils import helpers


def _get_application_log(core_job_operations, spark_job_operations, job_id, application_name):
    scheduling_target = core_job_operations.get_cluster_configuration(job_id).scheduling_target
    if scheduling_target is not models.SchedulingTarget.Any:
        return core_job_operations.get_application_log(job_id, application_name)

    # TODO: change where the logs are uploaded so they aren't overwritten on scheduled runs
    #           current: job_id, application_name/output.log
    #           new: job_id, recent_run_job.id/application_name/output.log
    recent_run_job = core_job_operations.get_recent_job(job_id)
    try:
        task = core_job_operations.get_batch_task(id=recent_run_job.id, task_id=application_name)
    except batch_models.BatchErrorException as e:
        # task may not exist since it may not yet be scheduled
        # see if the task is written to metadata of pool
        applications = spark_job_operations.list_applications(job_id)

        for application in applications:
            if applications[application] is None and application == application_name:
                raise error.AztkError("The application {0} has not yet been created.".format(application))
        raise error.AztkError("The application {0} does not exist".format(application_name))
    else:
        if task.state in (
                batch_models.TaskState.active,
                batch_models.TaskState.running,
                batch_models.TaskState.preparing,
        ):
            raise error.AztkError("The application {0} has not yet finished executing.".format(application_name))

        return core_job_operations.get_application_log(job_id, application_name)


def get_job_application_log(core_job_operations, spark_job_operations, job_id, application_name):
    try:
        return models.ApplicationLog(
            _get_application_log(core_job_operations, spark_job_operations, job_id, application_name))
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
