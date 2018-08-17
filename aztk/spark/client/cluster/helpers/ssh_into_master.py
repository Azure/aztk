import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.utils import helpers


def ssh_into_master(
        spark_cluster_operations,
        core_cluster_operations,
        cluster_id,
        username,
        ssh_key=None,
        password=None,
        port_forward_list=None,
        internal=False,
):
    try:
        master_node_id = spark_cluster_operations.get(cluster_id).master_node_id
        core_cluster_operations.ssh_into_node(cluster_id, master_node_id, username, ssh_key, password,
                                              port_forward_list, internal)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
