import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth
import azure.storage.blob as blob
from . import config
from .version import __version__


global_config = None

batch_client = None
batch_config = None
blob_config = None
blob_client = None


class AzureApiInitError(Exception):
    pass


class BatchConfig:
    def __init__(self, account_key: str, account_name: str, account_url: str):
        self.account_key = account_key
        self.account_name = account_name
        self.account_url = account_url


class BlobConfig:
    def __init__(self, account_key: str, account_name: str, account_suffix: str):
        self.account_key = account_key
        self.account_name = account_name
        self.account_suffix = account_suffix


def get_batch_client():
    """
        :returns: the batch client singleton
    """
    if not batch_client:
        __load_batch_client()
    return batch_client


def get_blob_client():
    """
        :returns: the blob client singleton
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
    secrets_config = config.SecretsConfig()
    secrets_config.load_secrets_config()

    global batch_config

    if secrets_config.batch_account_key is None:
        raise AzureApiInitError("Batch account key is not set in secrets.yaml config")
    if secrets_config.batch_account_name is None:
        raise AzureApiInitError("Batch account name is not set in secrets.yaml config")
    if secrets_config.batch_service_url is None:
        raise AzureApiInitError("Batch service url is not set in secrets.yaml config")

    # Get configuration
    account_key = secrets_config.batch_account_key
    account_name = secrets_config.batch_account_name
    account_url = secrets_config.batch_service_url

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


def get_blob_config() -> BlobConfig:
    if not blob_config:
        __load_blob_config()

    return blob_config

def __load_blob_config():
    secrets_config = config.SecretsConfig()
    secrets_config.load_secrets_config()

    global blob_config

    if secrets_config.storage_account_key is None:
        raise AzureApiInitError("Storage account key is not set in secrets.yaml config")
    if secrets_config.storage_account_name is None:
        raise AzureApiInitError("Storage account name is not set in secrets.yaml config")
    if secrets_config.storage_account_suffix is None:
        raise AzureApiInitError("Storage account suffix is not set in secrets.yaml config")

    # Get configuration
    storage_account_key = secrets_config.storage_account_key
    storage_account_name = secrets_config.storage_account_name
    storage_account_suffix = secrets_config.storage_account_suffix

    blob_config = BlobConfig(
        account_key=storage_account_key,
        account_name=storage_account_name,
        account_suffix=storage_account_suffix)


def __load_blob_client():
    global blob_client

    blob_config = get_blob_config()

    # create storage client
    blob_client = create_blob_client(
        blob_config.account_key,
        blob_config.account_name,
        blob_config.account_suffix)


