import os
import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels

pool_id = "sparktest"
node_id = "abc"

master_node_metadata_key = "_spark_master_node"

def get_client():
    # account_name = os.environ["AZ_BATCH_ACCOUNT_NAME"]
    # account_key = os.environ["ACCOUNT_KEY"]
    # account_url = os.environ["ACCOUNT_URL"]

    account_name = "prodtest1"
    account_key =  "o7qjfiRHz1CrjeDLIRUGTZfepWkdJUTc1OHcNEuD4QKUdWFzJ2rAXZlLv9MCyL8ZPXsBTSxash3q+sLdQLEJXA=="
    account_url =  "https://prodtest1.brazilsouth.batch.azure.com"

    credentials = batchauth.SharedKeyCredentials(
        account_name,
        account_key)
    return batch.BatchServiceClient(credentials, base_url=account_url)

if __name__ == "__main__":
    client = get_client()
    client.pool.patch(pool_id, batchmodels.PoolPatchParameter(
        metadata=[],
    ))
    print("Cleared metadata!")
