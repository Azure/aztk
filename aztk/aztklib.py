import aztk.config as config
import aztk_sdk.spark


class Aztk:
    def __init__(self):
        secrets_config = config.SecretsConfig()
        secrets_config.load()

        self.client = aztk_sdk.spark.Client(
            aztk_sdk.spark.models.SecretsConfiguration(
                batch_account_name=secrets_config.batch_account_name,
                batch_account_key=secrets_config.batch_account_key,
                batch_service_url=secrets_config.batch_service_url,
                storage_account_name=secrets_config.storage_account_name,
                storage_account_key=secrets_config.storage_account_key,
                storage_account_suffix=secrets_config.storage_account_suffix,
                ssh_pub_key=secrets_config.ssh_pub_key,
                ssh_priv_key=secrets_config.ssh_priv_key
            )
        )