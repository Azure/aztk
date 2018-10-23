import azure.batch.models as batch_models
from azure.batch.models import BatchErrorException

from aztk import error
from aztk.spark import models
from aztk.utils import helpers


def _list_applications(core_operations, id):
    # info about the app
    scheduling_target = core_operations.get_cluster_configuration(id).scheduling_target
    if scheduling_target is not models.SchedulingTarget.Any:
        return models.Application(core_operations.list_applications(id))

    recent_run_job = core_operations.get_recent_job(id)
    return core_operations.list_batch_tasks(id=recent_run_job.id)


def list_applications(core_operations, id):
    try:
        return models.Application(_list_applications(core_operations, id))
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
