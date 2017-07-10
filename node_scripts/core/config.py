import os
import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth

account_name = os.environ["AZ_BATCH_ACCOUNT_NAME"]
account_key = os.environ["ACCOUNT_KEY"]
account_url = os.environ["ACCOUNT_URL"]
pool_id = os.environ["AZ_BATCH_POOL_ID"]
node_id = os.environ["AZ_BATCH_NODE_ID"]
is_dedicated = os.environ["AZ_BATCH_NODE_IS_DEDICATED"]

# TODO save this as env/metadata
master_ui_port = 8082
webui_port = 4040
jupyter_port = 7777

def get_client() -> batch.BatchServiceClient:
    credentials = batchauth.SharedKeyCredentials(
        account_name,
        account_key)
    return batch.BatchServiceClient(credentials, base_url=account_url)


batch_client = get_client()

print("Pool id is", pool_id)
print("Node id is", node_id)
print("Account name", account_name)
print("Is dedicated", is_dedicated)
