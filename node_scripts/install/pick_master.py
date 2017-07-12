"""
    This is the code that all nodes will run in their start task to try to allocate the master
"""

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels
import azure.batch.models.batch_error as batcherror
from core import config


master_node_metadata_key = "_spark_master_node"


class CannotAllocateMasterError(Exception):
    pass


def get_master_node_id(pool: batchmodels.CloudPool):
    """
        :returns: the id of the node that is the assigned master of this pool
    """
    if pool.metadata is None:
        return None

    for metadata in pool.metadata:
        if metadata.name == master_node_metadata_key:
            return metadata.value

    return None


def try_assign_self_as_master(client: batch.BatchServiceClient, pool: batchmodels.CloudPool):
    currentMetadata = pool.metadata or []
    newMetadata = currentMetadata + \
        [{"name": master_node_metadata_key, "value": config.node_id}]

    try:
        client.pool.patch(config.pool_id, batchmodels.PoolPatchParameter(
            metadata=newMetadata
        ), batchmodels.PoolPatchOptions(
            if_match=pool.e_tag,
        ))
        return True
    except batcherror.BatchErrorException:
        print("Failed to gain power!")
        return False


def find_master(client: batch.BatchServiceClient) -> bool:
    """
        Try to set a master for the cluster. If the node is dedicated it will try to assign itself if none already claimed it.
        :returns bool: If the node is the master it returns true otherwise returns false
    """
    # If not dedicated the node cannot be a master
    # TODO enable when inter node communication is working with low pri and dedicated together.
    # if not config.is_dedicated:
    # return False

    for i in range(0, 5):
        pool = client.pool.get(config.pool_id)
        master = get_master_node_id(pool)

        if master:
            if master == config.node_id:
                print("Node is already the master '{0}'".format(master))
                return True
            else:
                print("Pool already has a master '{0}'. This node will be a worker".format(master))
                return False
        else:
            print("Pool has no master. Fighting for the throne! ({0}/5)".format(i + 1))
            result = try_assign_self_as_master(client, pool)

            if result:
                print("The battle has been won! Node {0} is the new master.".format(config.node_id))
                return True

    raise CannotAllocateMasterError("Unable to assign node as a master in 5 tries")
