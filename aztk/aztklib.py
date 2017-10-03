from aztk.clusterlib import Cluster
from aztk.joblib import Job
import aztk.azure_api as azure_api
import aztk.config as config
import aztk.error as error


class Aztk:
    def __init__(self):
        secrets_config = config.SecretsConfig()
        secrets_config.load_secrets_config()

        blob_config = azure_api.BlobConfig(
            account_key=secrets_config.storage_account_key,
            account_name=secrets_config.storage_account_name,
            account_suffix=secrets_config.storage_account_suffix
        )
        batch_config = azure_api.BatchConfig(
            account_key=secrets_config.batch_account_key,
            account_name=secrets_config.batch_account_name,
            account_url=secrets_config.batch_service_url
        )

        self.batch_client = azure_api.make_batch_client(batch_config)
        self.blob_client = azure_api.make_blob_client(blob_config)

        self.cluster = Cluster(
            batch_client=self.batch_client,
            blob_client=self.blob_client,
            batch_config=batch_config,
            blob_config=blob_config,
            secrets_config=secrets_config
        )
        self.job = Job(
            batch_client=self.batch_client,
            blob_client=self.blob_client
        )
