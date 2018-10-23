from azure.batch.models import BatchErrorException

from aztk import error
from aztk.utils import helpers


def get_configuration(core_cluster_operations, cluster_id: str):
    try:
        return core_cluster_operations.get_cluster_configuration(cluster_id)
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
