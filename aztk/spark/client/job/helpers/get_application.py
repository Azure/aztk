import azure.batch.models as batch_models
import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.spark import models
from aztk.utils import helpers

from .get_recent_job import get_recent_job


def _get_application(spark_job_operations, job_id, application_name):
    # info about the app
    recent_run_job = get_recent_job(spark_job_operations._core_job_operations, job_id)
    try:
        return spark_job_operations._core_job_operations.batch_client.task.get(
            job_id=recent_run_job.id, task_id=application_name)
    except batch_models.batch_error.BatchErrorException:
        raise error.AztkError(
            "The Spark application {0} is still being provisioned or does not exist.".format(application_name))


def get_application(spark_job_operations, job_id, application_name):
    try:
        return models.Application(_get_application(spark_job_operations, job_id, application_name))
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
