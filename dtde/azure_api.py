import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth
import azure.storage.blob as blob
from . import config
from .version import __version__


global_config = None

batch_client = None
batch_config = None
blob_client = None


class AzureApiInitError(Exception):
    pass


class BatchConfig:
    def __init__(self, account_key: str, account_name: str, account_url: str):
        self.account_key = account_key
        self.account_name = account_name
        self.account_url = account_url


def get_batch_client():
    """
        :returns: the batch client singleton
    """
    if not batch_client:
        __load_batch_client()
    return batch_client


def get_blob_client():
    """
        :returns: the batch client singleton
    """
    if not blob_client:
        __load_blob_client()
    return blob_client


def create_batch_client(
        batch_account_key: str,
        batch_account_name: str,
        batch_service_url: str):
    """
        Creates a batch client object
        :param str batch_account_key: batch account key
        :param str batch_account_name: batch account name
        :param str batch_service_url: batch service url
    """
    # Set up SharedKeyCredentials
    credentials = batch_auth.SharedKeyCredentials(
        batch_account_name,
        batch_account_key)

    # Set up Batch Client
    batch_client = batch.BatchServiceClient(
        credentials,
        base_url=batch_service_url)

    # Set retry policy
    batch_client.config.retry_policy.retries = 5
    batch_client.config.add_user_agent('dtde/{}'.format(__version__))

    return batch_client


def create_blob_client(
        storage_account_key: str,
        storage_account_name: str,
        storage_account_suffix: str):
    """
        Creates a blob client object
        :param str storage_account_key: storage account key
        :param str storage_account_name: storage account name
        :param str storage_account_suffix: storage account suffix
    """
    # Set up BlockBlobStorage
    blob_client = blob.BlockBlobService(
        account_name=storage_account_name,
        account_key=storage_account_key,
        endpoint_suffix=storage_account_suffix)

    return blob_client


def get_batch_config() -> BatchConfig:
    if not batch_config:
        __load_batch_config()

    return batch_config


def __load_batch_config():
    global_config = config.get()

    global batch_config

    if not global_config.has_option('Batch', 'batchaccountkey'):
        raise AzureApiInitError("Batch account key is not set in config")

    if not global_config.has_option('Batch', 'batchaccountname'):
        raise AzureApiInitError("Batch account name is not set in config")

    if not global_config.has_option('Batch', 'batchserviceurl'):
        raise AzureApiInitError("Batch account url is not set in config")

    # Get configuration
    account_key = global_config.get('Batch', 'batchaccountkey')
    account_name = global_config.get('Batch', 'batchaccountname')
    account_url = global_config.get('Batch', 'batchserviceurl')

    batch_config = BatchConfig(
        account_key=account_key, account_name=account_name, account_url=account_url)


def __load_batch_client():
    global batch_client

    config = get_batch_config()

    # create batch client
    batch_client = create_batch_client(
        config.account_key,
        config.account_name,
        config.account_url)


def __load_blob_client():
    global_config = config.get()
    global blob_client

    if not global_config.has_option('Storage', 'storageaccountkey'):
        raise AzureApiInitError("Storage account key is not set in config")

    if not global_config.has_option('Storage', 'storageaccountname'):
        raise AzureApiInitError("Storage account name is not set in config")

    if not global_config.has_option('Storage', 'storageaccountsuffix'):
        raise AzureApiInitError("Storage account suffix is not set in config")

    # Get configuration
    storage_account_key = global_config.get('Storage', 'storageaccountkey')
    storage_account_name = global_config.get('Storage', 'storageaccountname')
    storage_account_suffix = global_config.get(
        'Storage', 'storageaccountsuffix')

    # create storage client
    blob_client = create_blob_client(
        storage_account_key,
        storage_account_name,
        storage_account_suffix)
