import azure.batch.models as batch_models


class Cluster:
    def __init__(self, pool: batch_models.CloudPool, nodes: batch_models.ComputeNodePaged = None):
        self.id = pool.id
        self.pool = pool
        self.nodes = nodes
        self.vm_size = pool.vm_size
        if pool.state.value is batch_models.PoolState.active:
            self.visible_state = pool.allocation_state.value
        else:
            self.visible_state = pool.state.value
        self.total_current_nodes = pool.current_dedicated_nodes + pool.current_low_priority_nodes
        self.total_target_nodes = pool.target_dedicated_nodes + pool.target_low_priority_nodes
        self.current_dedicated_nodes = pool.current_dedicated_nodes
        self.current_low_pri_nodes = pool.current_low_priority_nodes
        self.target_dedicated_nodes = pool.target_dedicated_nodes
        self.target_low_pri_nodes = pool.target_low_priority_nodes
