from azure.batch.models import BatchErrorException

from aztk import error
from aztk.spark import models
from aztk.utils import helpers


def get_remote_login_settings(core_cluster_operations, id: str, node_id: str):
    try:
        return models.RemoteLogin(core_cluster_operations.get_remote_login_settings(id, node_id))
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
