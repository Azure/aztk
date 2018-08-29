from azure import batch

from aztk.models import ClusterConfiguration
from core import config, log

# from aztk.models import SchedulingTarget
SchedulingTarget = "SchedulingTarget"    # this code isn't used anywhere until scheduling_target reenabled


def disable_scheduling(batch_client: batch.BatchServiceClient):
    """
    Disable scheduling for the current node
    """
    pool_id = config.pool_id
    node_id = config.node_id

    node = batch_client.compute_node.get(pool_id, node_id)
    if node.scheduling_state == batch.models.SchedulingState.enabled:
        batch_client.compute_node.disable_scheduling(pool_id, node_id)
        log.info("Disabled task scheduling for this node")
    else:
        log.info("Task scheduling is already disabled for this node")


def enable_scheduling(batch_client: batch.BatchServiceClient):
    """
    Disable scheduling for the current node
    """
    pool_id = config.pool_id
    node_id = config.node_id

    node = batch_client.compute_node.get(pool_id, node_id)
    if node.scheduling_state == batch.models.SchedulingState.disabled:
        batch_client.compute_node.disable_scheduling(pool_id, node_id)
        log.info("Enabled task scheduling for this node")
    else:
        log.info("Task scheduling is already enabled for this node")


def setup_node_scheduling(batch_client: batch.BatchServiceClient, cluster_config: ClusterConfiguration,
                          is_master: bool):

    is_dedicated = config.is_dedicated
    enable = False
    log.info("Resolving scheduling for this node")
    log.info("  Scheduling target: %s", cluster_config.scheduling_target and cluster_config.scheduling_target.value)
    log.info("  Is node dedicated: %s", str(is_dedicated))
    log.info("  Is node master:    %s", str(is_master))

    if cluster_config.scheduling_target == SchedulingTarget.Any or cluster_config.scheduling_target is None:
        enable = True
    elif cluster_config.scheduling_target == SchedulingTarget.Dedicated and is_dedicated:
        enable = True
    elif cluster_config.scheduling_target == SchedulingTarget.Master and is_master:
        enable = True

    if enable:
        log.info("Scheduling will be enabled on this node as it satisfies the right conditions")
        enable_scheduling(batch_client)
    else:
        log.info("Scheduling will be disabled on this node as it does NOT satisfy the right conditions")
        disable_scheduling(batch_client)
