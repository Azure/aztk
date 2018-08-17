import time

import azure
import azure.batch.models as batch_models
import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk import models as base_models
from aztk.spark import models
from aztk.utils import constants, helpers

output_file = constants.TASK_WORKING_DIR + "/" + constants.SPARK_SUBMIT_LOGS_FILE


def __check_task_node_exist(batch_client, cluster_id: str, task: batch_models.CloudTask) -> bool:
    try:
        batch_client.compute_node.get(cluster_id, task.node_info.node_id)
        return True
    except batch_error.BatchErrorException:
        return False


def __wait_for_app_to_be_running(batch_client, cluster_id: str, application_name: str) -> batch_models.CloudTask:
    """
        Wait for the batch task to leave the waiting state into running(or completed if it was fast enough)
    """
    while True:
        task = batch_client.task.get(cluster_id, application_name)

        if task.state is batch_models.TaskState.active or task.state is batch_models.TaskState.preparing:
            # TODO: log
            time.sleep(5)
        else:
            return task


def __get_output_file_properties(batch_client, cluster_id: str, application_name: str):
    while True:
        try:
            file = helpers.get_file_properties(cluster_id, application_name, output_file, batch_client)
            return file
        except batch_error.BatchErrorException as e:
            if e.response.status_code == 404:
                # TODO: log
                time.sleep(5)
                continue
            else:
                raise e


def get_log_from_storage(blob_client, container_name, application_name, task):
    try:
        blob = blob_client.get_blob_to_text(container_name, application_name + "/" + constants.SPARK_SUBMIT_LOGS_FILE)
    except azure.common.AzureMissingResourceHttpError:
        raise error.AztkError("Logs not found in your storage account. They were either deleted or never existed.")
    base_model = base_models.ApplicationLog(
        name=application_name,
        cluster_id=container_name,
        application_state=task.state.name,
        log=blob.content,
        total_bytes=blob.properties.content_length,
        exit_code=task.execution_info.exit_code,
    )
    return models.ApplicationLog(base_model)


def get_log(batch_client, blob_client, cluster_id: str, application_name: str, tail=False, current_bytes: int = 0):
    job_id = cluster_id
    task_id = application_name

    task = __wait_for_app_to_be_running(batch_client, cluster_id, application_name)

    if not __check_task_node_exist(batch_client, cluster_id, task):
        return get_log_from_storage(blob_client, cluster_id, application_name, task)

    file = __get_output_file_properties(batch_client, cluster_id, application_name)
    target_bytes = file.content_length

    if target_bytes != current_bytes:
        ocp_range = None

        if tail:
            ocp_range = "bytes={0}-{1}".format(current_bytes, target_bytes - 1)

        stream = batch_client.file.get_from_task(
            job_id, task_id, output_file, batch_models.FileGetFromTaskOptions(ocp_range=ocp_range))
        content = helpers.read_stream_as_string(stream)
        base_model = base_models.ApplicationLog(
            name=application_name,
            cluster_id=cluster_id,
            application_state=task.state.name,
            log=content,
            total_bytes=target_bytes,
            exit_code=task.execution_info.exit_code,
        )
        return models.ApplicationLog(base_model)
    else:
        base_model = base_models.ApplicationLog(
            name=application_name,
            cluster_id=cluster_id,
            application_state=task.state.name,
            log="",
            total_bytes=target_bytes,
            exit_code=task.execution_info.exit_code,
        )
        return models.ApplicationLog(base_model)
