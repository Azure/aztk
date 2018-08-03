from aztk import models
from aztk.utils import constants


def list_clusters(cluster_client, software_metadata_key):
    """
        List all the cluster on your account.
    """
    pools = cluster_client.batch_client.pool.list()
    software_metadata = (constants.AZTK_SOFTWARE_METADATA_KEY, software_metadata_key)
    cluster_metadata = (constants.AZTK_MODE_METADATA_KEY, constants.AZTK_CLUSTER_MODE_METADATA)

    aztk_clusters = []
    for pool in [pool for pool in pools if pool.metadata]:
        pool_metadata = [(metadata.name, metadata.value) for metadata in pool.metadata]
        if all([metadata in pool_metadata for metadata in [software_metadata, cluster_metadata]]):
            aztk_clusters.append(models.Cluster(pool))
    return aztk_clusters
