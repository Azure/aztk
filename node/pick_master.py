"""
    This is the code that all nodes will run in their start task to try to allocate the master
"""

import os
import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels
import azure.batch.models.batch_error as batcherror

pool_id = os.environ["AZ_BATCH_POOL_ID"]
node_id = os.environ["AZ_BATCH_NODE_ID"]
account_name = os.environ["AZ_BATCH_ACCOUNT_NAME"]
account_key = os.environ["ACCOUNT_KEY"]
account_url = os.environ["ACCOUNT_URL"]

# pool_id = "sparktest"
# node_id = "abc"

print("Pool id is", node_id)
print("Node id is", node_id)
print("Account name", account_name)

master_node_metadata_key = "_spark_master_node"

def get_client():

    credentials = batchauth.SharedKeyCredentials(
        account_name,
        account_key)
    return batch.BatchServiceClient(credentials, base_url=account_url)

def get_master_node_id(pool: batchmodels.CloudPool):
    """
        :returns: the id of the node that is the assigned master of this pool
    """
    if(pool.metadata is None):
        return None

    for metadata in pool.metadata:
        if metadata.name == master_node_metadata_key:
            return metadata.value
    
    return None


def try_assign_self_as_master(client: batch.BatchServiceClient, pool: batchmodels.CloudPool):
    currentMetadata = pool.metadata or []
    newMetadata = currentMetadata + [{"name": master_node_metadata_key, "value": node_id}]

    try: 
        client.pool.patch(pool_id,  batchmodels.PoolPatchParameter(
            metadata=newMetadata
        ), batchmodels.PoolPatchOptions(
            if_match=pool.e_tag,
        ))
        return True
    except batcherror.BatchErrorException:
        print("Failed to gain power!")
        return False 

def find_master(client: batch.BatchServiceClient): 
    for i in range(0, 5): 
        pool: batchmodels.CloudPool = client.pool.get(pool_id)
        master = get_master_node_id(pool)

        if master:
            print("Pool already has a master '%s'. This node will be a worker" % master)
        else:
            print("Pool has no master. Fighting for the throne! (%i/5)" % (i + 1))
            result = try_assign_self_as_master(client, pool)

            if result: 
                print("The battle has been won! Node %s is the new master.", node_id)
                return True
            

    print("Unable to assign node as a master in 5 tries")
    return False

def run():
    client = get_client()
    result = find_master(client)

    if not result:
        exit(1)


if __name__ == "__main__":
    run()
