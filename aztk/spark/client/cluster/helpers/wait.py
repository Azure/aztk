import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk.utils import helpers


def wait_for_application_to_complete(core_cluster_operations, id, application_name):
    try:
        return core_cluster_operations.wait(id, application_name)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
