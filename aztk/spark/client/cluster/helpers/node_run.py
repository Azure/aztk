import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.utils import helpers


def node_run(
        core_cluster_operations,
        cluster_id: str,
        node_id: str,
        command: str,
        host=False,
        internal: bool = False,
        timeout=None,
):
    try:
        return core_cluster_operations.node_run(
            cluster_id, node_id, command, internal, container_name="spark" if not host else None, timeout=timeout)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
