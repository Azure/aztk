import os
import re

import azure.batch.batch_auth as batchauth
import azure.batch.batch_service_client as batch
import azure.storage.blob as blob
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.batch import BatchManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.common import CloudStorageAccount

from core import log

RESOURCE_ID_PATTERN = re.compile("^/subscriptions/(?P<subscription>[^/]+)"
                                 "/resourceGroups/(?P<resourcegroup>[^/]+)"
                                 "/providers/[^/]+"
                                 "/[^/]+Accounts/(?P<account>[^/]+)$")

batch_account_name = os.environ.get("AZ_BATCH_ACCOUNT_NAME")
batch_account_key = os.environ.get("BATCH_ACCOUNT_KEY")
batch_service_url = os.environ.get("BATCH_SERVICE_URL")
tenant_id = os.environ.get("SP_TENANT_ID")
client_id = os.environ.get("SP_CLIENT_ID")
credential = os.environ.get("SP_CREDENTIAL")
batch_resource_id = os.environ.get("SP_BATCH_RESOURCE_ID")
storage_resource_id = os.environ.get("SP_STORAGE_RESOURCE_ID")

cluster_id = os.environ.get("AZTK_CLUSTER_ID")
pool_id = os.environ["AZ_BATCH_POOL_ID"]
node_id = os.environ["AZ_BATCH_NODE_ID"]
is_dedicated = os.environ["AZ_BATCH_NODE_IS_DEDICATED"] == "true"

spark_web_ui_port = os.environ["SPARK_WEB_UI_PORT"]
spark_worker_ui_port = os.environ["SPARK_WORKER_UI_PORT"]
spark_job_ui_port = os.environ["SPARK_JOB_UI_PORT"]

storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
storage_account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
storage_account_suffix = os.environ.get("STORAGE_ACCOUNT_SUFFIX")


def get_blob_client() -> blob.BlockBlobService:
    if not storage_resource_id:
        return blob.BlockBlobService(
            account_name=storage_account_name, account_key=storage_account_key, endpoint_suffix=storage_account_suffix)
    else:
        credentials = ServicePrincipalCredentials(
            client_id=client_id, secret=credential, tenant=tenant_id, resource="https://management.core.windows.net/")
        m = RESOURCE_ID_PATTERN.match(storage_resource_id)
        accountname = m.group("account")
        subscription = m.group("subscription")
        resourcegroup = m.group("resourcegroup")
        mgmt_client = StorageManagementClient(credentials, subscription)
        key = (mgmt_client.storage_accounts.list_keys(resource_group_name=resourcegroup, account_name=accountname)
               .keys[0].value)
        storage_client = CloudStorageAccount(accountname, key)
        return storage_client.create_block_blob_service()


def get_batch_client() -> batch.BatchServiceClient:
    if not batch_resource_id:
        base_url = batch_service_url
        credentials = batchauth.SharedKeyCredentials(batch_account_name, batch_account_key)
    else:
        credentials = ServicePrincipalCredentials(
            client_id=client_id, secret=credential, tenant=tenant_id, resource="https://management.core.windows.net/")
        m = RESOURCE_ID_PATTERN.match(batch_resource_id)
        batch_client = BatchManagementClient(credentials, m.group("subscription"))
        account = batch_client.batch_account.get(m.group("resourcegroup"), m.group("account"))
        base_url = "https://%s/" % account.account_endpoint
        credentials = ServicePrincipalCredentials(
            client_id=client_id, secret=credential, tenant=tenant_id, resource="https://batch.core.windows.net/")

    return batch.BatchServiceClient(credentials, base_url=base_url)


batch_client = get_batch_client()
blob_client = get_blob_client()

log.info("Pool id is %s", pool_id)
log.info("Node id is %s", node_id)
log.info("Batch account name %s", batch_account_name)
log.info("Is dedicated %s", is_dedicated)
