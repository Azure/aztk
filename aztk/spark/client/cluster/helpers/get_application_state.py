from azure.batch.models import BatchErrorException

from aztk import error
from aztk.spark.models import ApplicationState
from aztk.utils import helpers


def get_application_state(core_cluster_operations, cluster_id: str, app_name: str):
    try:
        return ApplicationState(core_cluster_operations.get_task_state(cluster_id, app_name).value)
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
