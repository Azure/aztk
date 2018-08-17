"""
    This is the code that all nodes will run in their start task to try to allocate the master
"""
import azure.batch.batch_service_client as batch
import azure.batch.models as batchmodels
import azure.batch.models.batch_error as batcherror
from msrest.exceptions import ClientRequestError

from core import config

MASTER_NODE_METADATA_KEY = "_spark_master_node"


class CannotAllocateMasterError(Exception):
    pass


def get_master_node_id(pool: batchmodels.CloudPool):
    """
        :returns: the id of the node that is the assigned master of this pool
    """
    if pool.metadata is None:
        return None

    for metadata in pool.metadata:
        if metadata.name == MASTER_NODE_METADATA_KEY:
            return metadata.value

    return None


def try_assign_self_as_master(client: batch.BatchServiceClient, pool: batchmodels.CloudPool):
    current_metadata = pool.metadata or []
    new_metadata = current_metadata + [{"name": MASTER_NODE_METADATA_KEY, "value": config.node_id}]

    try:
        client.pool.patch(
            config.pool_id,
            batchmodels.PoolPatchParameter(metadata=new_metadata),
            batchmodels.PoolPatchOptions(if_match=pool.e_tag),
        )
        return True
    except (batcherror.BatchErrorException, ClientRequestError):
        print("Couldn't assign itself as master the pool because the pool was modified since last get.")
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
            print("Pool has no master. Trying to assign itself! ({0}/5)".format(i + 1))
            result = try_assign_self_as_master(client, pool)

            if result:
                print("Assignment was successful! Node {0} is the new master.".format(config.node_id))
                return True

    raise CannotAllocateMasterError("Unable to assign node as a master in 5 tries")
