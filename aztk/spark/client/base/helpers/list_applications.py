import azure.batch.models as batch_models
from azure.batch.models import BatchErrorException

from aztk import error
from aztk.spark.models import Application, SchedulingTarget
from aztk.utils import helpers


def list_applications(core_operations, cluster_id):
    try:
        scheduling_target = core_operations.get_cluster_configuration(cluster_id).scheduling_target
        if scheduling_target is not SchedulingTarget.Any:
            tasks = core_operations.list_task_table_entries(cluster_id)
        else:
            tasks = core_operations.list_batch_tasks(cluster_id)
        return [Application(task) for task in tasks]
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
