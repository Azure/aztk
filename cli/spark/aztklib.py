import cli.config as config
import aztk.spark

'''
    Creates a client based on the user's local environment
    Reads the configuration file from .aztk/secrets.yaml
'''

def load_spark_client():
    secrets_config = config.SecretsConfig()
    secrets_config.load()

    return aztk.spark.Client(
        aztk.spark.models.SecretsConfiguration(
            batch_account_name=secrets_config.batch_account_name,
            batch_account_key=secrets_config.batch_account_key,
            batch_service_url=secrets_config.batch_service_url,
            storage_account_name=secrets_config.storage_account_name,
            storage_account_key=secrets_config.storage_account_key,
            storage_account_suffix=secrets_config.storage_account_suffix,
            docker_endpoint=secrets_config.docker_endpoint,
            docker_password=secrets_config.docker_password,
            docker_username=secrets_config.docker_username,
            ssh_pub_key=secrets_config.ssh_pub_key,
            ssh_priv_key=secrets_config.ssh_priv_key
        )
    )