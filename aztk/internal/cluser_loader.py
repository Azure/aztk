from azure import batch
from aztk.models import Cluster, MasterState
from aztk.utils import constants

def load_cluster(client: batch.BatchServiceClient, cluster_id: str) -> Cluster:
    pool = client.pool.get(cluster_id)
    job = client.pool.get(cluster_id)
    nodeCounts = client.account.get_pool_node_counts()][0]
    master_node_id = _get_master_node_id(pool)
    master_node = None
    if master_node_id:
        master_node = client.compute_node.get(cluster_id, master_node_id)

    return Cluster(
        id=cluster_id,
        master_node=master_node,
    )


def _compute_cluster_state(pool, master_node, nodeCounts) -> MasterState:
    potential_master_count = _get_potential_master_counts(pool, nodeCounts)


def _get_potential_master_counts(pool, nodeCounts) -> batch.models.NodeCount:
    """
    Get the number of nodes that currently can be the master
    """
    if pool.target_dedicated_nodes == 0:
        return nodeCounts.low_priority
    return nodeCounts.dedicated


def _get_master_node_id(pool: batch.models.CloudPool):
    """
        :returns: the id of the node that is the assigned master of this pool
    """
    if pool.metadata is None:
        return None

    for metadata in pool.metadata:
        if metadata.name == constants.MASTER_NODE_METADATA_KEY:
            return metadata.value

    return None
