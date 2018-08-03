import azure.batch.models.batch_error as batch_error

from aztk import error, models
from aztk.utils import helpers


def _get_remote_login_settings(base_client, pool_id: str, node_id: str):
    """
    Get the remote_login_settings for node
    :param pool_id
    :param node_id
    :returns aztk.models.RemoteLogin
    """
    result = base_client.batch_client.compute_node.get_remote_login_settings(pool_id, node_id)
    return models.RemoteLogin(ip_address=result.remote_login_ip_address, port=str(result.remote_login_port))


def get_remote_login_settings(base_client, cluster_id: str, node_id: str):
    try:
        return _get_remote_login_settings(base_client, cluster_id, node_id)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
