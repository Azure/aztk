import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.utils import helpers


def get_configuration(core_cluster_operations, cluster_id: str):
    try:
        return core_cluster_operations.get_cluster_configuration(cluster_id)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
