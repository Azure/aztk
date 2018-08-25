# TODO: return Cluster instead of (pool, nodes)
from aztk import models


def get_pool_details(core_cluster_operations, cluster_id: str):
    """
        Print the information for the given cluster
        :param cluster_id: Id of the cluster
        :return pool: CloudPool, nodes: ComputeNodePaged
    """
    pool = core_cluster_operations.batch_client.pool.get(cluster_id)
    nodes = core_cluster_operations.batch_client.compute_node.list(pool_id=cluster_id)
    return models.Cluster(pool, nodes)
