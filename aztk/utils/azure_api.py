import re

import azure.batch.batch_auth as batch_auth
import azure.batch.batch_service_client as batch
import azure.storage.blob as blob
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.batch import BatchManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.common import CloudStorageAccount

from aztk import error
from aztk.version import __version__

RESOURCE_ID_PATTERN = re.compile("^/subscriptions/(?P<subscription>[^/]+)"
                                 "/resourceGroups/(?P<resourcegroup>[^/]+)"
                                 "/providers/[^/]+"
                                 "/[^/]+Accounts/(?P<account>[^/]+)$")


def validate_secrets(secrets):
    if secrets.service_principal:
        if not RESOURCE_ID_PATTERN.match(secrets.service_principal.batch_account_resource_id):
            raise error.AzureApiInitError("ServicePrincipal batch_account_resource_id is not in expected format")

        if not RESOURCE_ID_PATTERN.match(secrets.service_principal.storage_account_resource_id):
            raise error.AzureApiInitError("ServicePrincipal storage_account_resource_id is not in expected format")


def make_batch_client(secrets):
    """
        Creates a batch client object
        :param str batch_account_key: batch account key
        :param str batch_account_name: batch account name
        :param str batch_service_url: batch service url
    """
    # Validate the given config
    credentials = None

    if secrets.shared_key:
        # Set up SharedKeyCredentials
        base_url = secrets.shared_key.batch_service_url
        credentials = batch_auth.SharedKeyCredentials(secrets.shared_key.batch_account_name,
                                                      secrets.shared_key.batch_account_key)
    else:
        # Set up ServicePrincipalCredentials
        arm_credentials = ServicePrincipalCredentials(
            client_id=secrets.service_principal.client_id,
            secret=secrets.service_principal.credential,
            tenant=secrets.service_principal.tenant_id,
            resource="https://management.core.windows.net/",
        )
        m = RESOURCE_ID_PATTERN.match(secrets.service_principal.batch_account_resource_id)
        arm_batch_client = BatchManagementClient(arm_credentials, m.group("subscription"))
        account = arm_batch_client.batch_account.get(m.group("resourcegroup"), m.group("account"))
        base_url = "https://{0}/".format(account.account_endpoint)
        credentials = ServicePrincipalCredentials(
            client_id=secrets.service_principal.client_id,
            secret=secrets.service_principal.credential,
            tenant=secrets.service_principal.tenant_id,
            resource="https://batch.core.windows.net/",
        )

    # Set up Batch Client
    batch_client = batch.BatchServiceClient(credentials, base_url=base_url)

    # Set retry policy
    batch_client.config.retry_policy.retries = 5
    batch_client.config.add_user_agent("aztk/{}".format(__version__))

    return batch_client


def make_blob_client(secrets):
    """
        Creates a blob client object
        :param str storage_account_key: storage account key
        :param str storage_account_name: storage account name
        :param str storage_account_suffix: storage account suffix
    """

    if secrets.shared_key:
        # Set up SharedKeyCredentials
        blob_client = blob.BlockBlobService(
            account_name=secrets.shared_key.storage_account_name,
            account_key=secrets.shared_key.storage_account_key,
            endpoint_suffix=secrets.shared_key.storage_account_suffix,
        )
    else:
        # Set up ServicePrincipalCredentials
        arm_credentials = ServicePrincipalCredentials(
            client_id=secrets.service_principal.client_id,
            secret=secrets.service_principal.credential,
            tenant=secrets.service_principal.tenant_id,
            resource="https://management.core.windows.net/",
        )
        m = RESOURCE_ID_PATTERN.match(secrets.service_principal.storage_account_resource_id)
        accountname = m.group("account")
        subscription = m.group("subscription")
        resourcegroup = m.group("resourcegroup")
        mgmt_client = StorageManagementClient(arm_credentials, subscription)
        key = (retry_function(
            mgmt_client.storage_accounts.list_keys,
            10,
            1,
            Exception,
            resource_group_name=resourcegroup,
            account_name=accountname,
        ).keys[0].value)
        storage_client = CloudStorageAccount(accountname, key)
        blob_client = storage_client.create_block_blob_service()

    return blob_client


def retry_function(function, retry_attempts: int, retry_interval: int, exception: Exception, *args, **kwargs):
    import time

    for i in range(retry_attempts):
        try:
            return function(*args, **kwargs)
        except exception as e:
            if i == retry_attempts - 1:
                raise e
            time.sleep(retry_interval)
