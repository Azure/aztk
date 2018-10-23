from azure.batch.models import BatchErrorException

from aztk import error
from aztk.spark import models
from aztk.utils import helpers


def get_cluster(core_cluster_operations, cluster_id: str):
    try:
        cluster = core_cluster_operations.get(cluster_id)
        return models.Cluster(cluster)
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
