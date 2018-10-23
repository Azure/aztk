from azure.batch.models import BatchErrorException

from aztk import error
from aztk.utils import helpers


def delete_cluster(core_cluster_operations, cluster_id: str, keep_logs: bool = False):
    try:
        return core_cluster_operations.delete(cluster_id, keep_logs)
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
