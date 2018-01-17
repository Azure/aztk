import os
import re
import logging
import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.batch import BatchManagementClient

RESOURCE_ID_PATTERN = re.compile('^/subscriptions/(?P<subscription>[^/]+)'
                                 '/resourceGroups/(?P<resourcegroup>[^/]+)'
                                 '/providers/[^/]+'
                                 '/[^/]+Accounts/(?P<account>[^/]+)$')

account_name = os.environ["AZ_BATCH_ACCOUNT_NAME"]
account_key = os.environ["BATCH_ACCOUNT_KEY"]
service_url = os.environ["BATCH_SERVICE_URL"]
tenant_id = os.environ["SP_TENANT_ID"]
client_id = os.environ["SP_CLIENT_ID"]
credential = os.environ["SP_CREDENTIAL"]
batch_resource_id = os.environ["SP_BATCH_RESOURCE_ID"]
storage_resource_id = os.environ["SP_STORAGE_RESOURCE_ID"]

pool_id = os.environ["AZ_BATCH_POOL_ID"]
node_id = os.environ["AZ_BATCH_NODE_ID"]
is_dedicated = os.environ["AZ_BATCH_NODE_IS_DEDICATED"]

spark_web_ui_port = os.environ["SPARK_WEB_UI_PORT"]
spark_worker_ui_port = os.environ["SPARK_WORKER_UI_PORT"]
spark_jupyter_port = os.environ["SPARK_JUPYTER_PORT"]
spark_job_ui_port = os.environ["SPARK_JOB_UI_PORT"]

def get_client() -> batch.BatchServiceClient:
    if not batch_resource_id:
        base_url=service_url
        credentials = batchauth.SharedKeyCredentials(
            account_name,
            account_key)
    else:
        credentials = ServicePrincipalCredentials(
            client_id=client_id,
            secret=credential,
            tenant=tenant_id,
            resource='https://management.core.windows.net/')
        m = RESOURCE_ID_PATTERN.match(batch_resource_id)
        batch_client = BatchManagementClient(credentials, m.group('subscription'))
        account = batch_client.batch_account.get(m.group('resourcegroup'), m.group('account'))
        base_url = 'https://%s/' % account.account_endpoint
        credentials = ServicePrincipalCredentials(
            client_id=client_id,
            secret=credential,
            tenant=tenant_id,
            resource='https://batch.core.windows.net/')

    return batch.BatchServiceClient(credentials, base_url=base_url)

batch_client = get_client()

logging.info("Pool id is %s", pool_id)
logging.info("Node id is %s", node_id)
logging.info("Batch account name %s", account_name)
logging.info("Is dedicated %s", is_dedicated)
