from azure import batch

from aztk.utils import constants

from .master_state import MasterState


class Cluster:
    """
    Aztk Cluster representation

    Attributes:
        id (str): Id of the cluster
        master_state (MasterState): State of the master
        vm_size (str): VM size used for this cluster

        current_dedicated_nodes (int): Current number of dedicated nodes
        target_dedicated_nodes (int): Target number of dedicated nodes

        current_low_pri_nodes (int): Current number of low priority nodes
        target_low_pri_nodes (int): Target number of low priority nodes
    """
    def __init__(self,
                 pool: batch.models.CloudPool,
                 nodeCounts: batch.models.PoolNodeCounts,
                 nodes: batch.models.ComputeNodePaged = None):
        self.id = pool.id
        self.pool = pool
        self.nodes = nodes
        self.nodeCounts = nodeCounts
        self.vm_size = pool.vm_size
        if pool.state.value is batch.models.PoolState.active:
            self.visible_state = pool.allocation_state.value
        else:
            self.visible_state = pool.state.value
        self.total_current_nodes = pool.current_dedicated_nodes + \
            pool.current_low_priority_nodes
        self.total_target_nodes = pool.target_dedicated_nodes + \
            pool.target_low_priority_nodes
        self.current_dedicated_nodes = pool.current_dedicated_nodes
        self.current_low_pri_nodes = pool.current_low_priority_nodes
        self.target_dedicated_nodes = pool.target_dedicated_nodes
        self.target_low_pri_nodes = pool.target_low_priority_nodes
        self.master_node_id = _get_master_node_id(pool)
        self.master_state = self._compute_cluster_state()

    def _compute_cluster_state(self) -> MasterState:
        potential_master_count = _count_potential_master(self.pool)
        if potential_master_count == 0:
            return MasterState.Allocating
        elif self.master_node_id is None:
            return MasterState.Booting

def _count_potential_master(pool: batch.models.CloudPool) -> int:
    """
    Get the number of nodes that currently can be the master
    """
    if pool.target_dedicated_nodes == 0:
        return pool.current_low_priority_nodes
    return pool.current_dedicated_nodes


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
