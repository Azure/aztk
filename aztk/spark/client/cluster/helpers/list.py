import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk import models as base_models
from aztk.spark import models
from aztk.utils import helpers


def list_clusters(core_cluster_operations):
    try:
        software_metadata_key = base_models.Software.spark
        return [models.Cluster(cluster) for cluster in core_cluster_operations.list(software_metadata_key)]
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
