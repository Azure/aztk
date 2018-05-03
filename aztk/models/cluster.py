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
                 id: str,
                 master_node: batch.models.ComputeNode,
                 master_node_status:
                 nodeCounts: batch.models.PoolNodeCounts,
                 master_node: batch.models.ComputeNode,
                 nodes: batch.models.ComputeNodePaged = None):
        self.id = pool.id
        # self.pool = pool
        # self.nodes = nodes
        # self.nodeCounts = nodeCounts
        # self.vm_size = pool.vm_size
        # self.master_node = master_node
        # self.master_node_id = master_node and master_node.id

        # if pool.state.value is batch.models.PoolState.active:
        #     self.visible_state = pool.allocation_state.value
        # else:
        #     self.visible_state = pool.state.value
        # self.total_current_nodes = pool.current_dedicated_nodes + \
        #     pool.current_low_priority_nodes
        # self.total_target_nodes = pool.target_dedicated_nodes + \
        #     pool.target_low_priority_nodes
        # self.current_dedicated_nodes = pool.current_dedicated_nodes
        # self.current_low_pri_nodes = pool.current_low_priority_nodes
        # self.target_dedicated_nodes = pool.target_dedicated_nodes
        # self.target_low_pri_nodes = pool.target_low_priority_nodes
        # self.master_state = self._compute_cluster_state()
