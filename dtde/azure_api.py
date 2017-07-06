from . import config, util

global_config = config.get()

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
    return blob_client;

def __load_batch_client():
    # Get configuration
    batch_account_key = global_config.get('Batch', 'batchaccountkey')
    batch_account_name = global_config.get('Batch', 'batchaccountname')
    batch_service_url = global_config.get('Batch', 'batchserviceurl')

    # create batch client
    batch_client = util.create_batch_client(
        batch_account_key,
        batch_account_name,
        batch_service_url)

def __load_blob_client():
    # Get configuration
    storage_account_key = global_config.get('Storage', 'storageaccountkey')
    storage_account_name = global_config.get('Storage', 'storageaccountname')
    storage_account_suffix = global_config.get('Storage', 'storageaccountsuffix')

    # create storage client
    blob_client = util.create_blob_client(
        storage_account_key,
        storage_account_name,
        storage_account_suffix)