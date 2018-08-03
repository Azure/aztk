import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.spark import models
from aztk.utils import helpers


def get_cluster(core_cluster_operations, cluster_id: str):
    try:
        cluster = core_cluster_operations.get(cluster_id)
        return models.Cluster(cluster)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
