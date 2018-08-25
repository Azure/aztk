import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.utils import helpers


def create_user(
        core_cluster_operations,
        spark_cluster_operations,
        cluster_id: str,
        username: str,
        password: str = None,
        ssh_key: str = None,
) -> str:
    try:
        cluster = spark_cluster_operations.get(cluster_id)
        master_node_id = cluster.master_node_id
        if not master_node_id:
            raise error.ClusterNotReadyError("The master has not yet been picked, a user cannot be added.")
        core_cluster_operations.create_user_on_cluster(cluster.id, cluster.nodes, username, ssh_key, password)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
