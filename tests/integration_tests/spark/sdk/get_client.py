import os
from datetime import datetime

import aztk.spark
from aztk_cli import config


def get_spark_client():
    # load secrets
    # note: this assumes secrets are set up in .aztk/secrets
    tenant_id = os.environ.get("TENANT_ID")
    client_id = os.environ.get("CLIENT_ID")
    credential = os.environ.get("CREDENTIAL")
    batch_account_resource_id = os.environ.get("BATCH_ACCOUNT_RESOURCE_ID")
    storage_account_resource_id = os.environ.get("STORAGE_ACCOUNT_RESOURCE_ID")
    ssh_pub_key = os.environ.get("ID_RSA_PUB")
    ssh_private_key = os.environ.get("ID_RSA")
    keys = [
        tenant_id, client_id, credential, batch_account_resource_id, storage_account_resource_id, ssh_private_key,
        ssh_pub_key
    ]

    spark_client = None
    if all(keys):
        spark_client = aztk.spark.Client(
            aztk.spark.models.SecretsConfiguration(
                service_principal=aztk.spark.models.ServicePrincipalConfiguration(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    credential=credential,
                    batch_account_resource_id=batch_account_resource_id,
                    storage_account_resource_id=storage_account_resource_id),
                ssh_pub_key=ssh_pub_key,
                ssh_priv_key=ssh_private_key))
    else:
        # fallback to local secrets if environment variables don't exist
        spark_client = aztk.spark.Client(config.load_aztk_secrets())

    return spark_client


def get_test_suffix(prefix: str):
    # base cluster name
    dt = datetime.now()
    current_time = dt.microsecond
    base_cluster_id = "{0}-{1}".format(prefix, current_time)
    return base_cluster_id
