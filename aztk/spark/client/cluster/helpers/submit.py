import azure.batch.models as batch_models
import yaml
from azure.batch.models import BatchErrorException

from aztk import error
from aztk.error import AztkError
from aztk.spark import models
from aztk.utils import constants, helpers


def __get_node(core_cluster_operations, node_id: str, cluster_id: str) -> batch_models.ComputeNode:
    return core_cluster_operations.batch_client.compute_node.get(cluster_id, node_id)


def affinitize_task_to_master(core_cluster_operations, spark_cluster_operations, cluster_id, task):
    cluster = spark_cluster_operations.get(cluster_id)
    if cluster.master_node_id is None:
        raise AztkError("Master has not yet been selected. Please wait until the cluster is finished provisioning.")
    master_node = core_cluster_operations.batch_client.compute_node.get(
        pool_id=cluster_id, node_id=cluster.master_node_id)
    task.affinity_info = batch_models.AffinityInformation(affinity_id=master_node.affinity_id)
    return task


def upload_serialized_task_to_storage(blob_client, cluster_id, task):
    return helpers.upload_text_to_container(
        container_name=cluster_id,
        application_name=task.id,
        file_path="task.yaml",
        content=yaml.dump(task),
        blob_client=blob_client,
    )


def select_scheduling_target_node(spark_cluster_operations, cluster_id, scheduling_target):
    # for now, limit to only targeting master
    cluster = spark_cluster_operations.get(cluster_id)
    if not cluster.master_node_id:
        return None
    return cluster.master_node_id


def schedule_with_target(
        core_cluster_operations,
        spark_cluster_operations,
        cluster_id,
        scheduling_target,
        task,
        wait,
        internal,
):
    # upload "real" task definition to storage
    serialized_task_resource_file = upload_serialized_task_to_storage(core_cluster_operations.blob_client, cluster_id,
                                                                      task)
    # # schedule "ghost" task
    ghost_task = batch_models.TaskAddParameter(
        id=task.id,
        command_line="/bin/bash",
    )
    # tell the node to run the task
    core_cluster_operations.batch_client.task.add(cluster_id, task=ghost_task)

    task_working_dir = "/mnt/aztk/startup/tasks/workitems/{}".format(task.id)

    task_cmd = (
        r"source ~/.bashrc; "
        r"mkdir -p {0};"
        r"export PYTHONPATH=$PYTHONPATH:$AZTK_WORKING_DIR; "
        r"export AZ_BATCH_TASK_WORKING_DIR={0};"
        r"export STORAGE_LOGS_CONTAINER={1};"
        r"cd $AZ_BATCH_TASK_WORKING_DIR; "
        r'$AZTK_WORKING_DIR/.aztk-env/.venv/bin/python $AZTK_WORKING_DIR/aztk/node_scripts/scheduling/submit.py "{2}" >> {3} 2>&1'.
        format(task_working_dir, cluster_id, serialized_task_resource_file.blob_source,
               constants.SPARK_SUBMIT_LOGS_FILE))
    node_id = select_scheduling_target_node(spark_cluster_operations, cluster_id, scheduling_target)
    node_run_output = spark_cluster_operations.node_run(
        cluster_id, node_id, task_cmd, timeout=120, block=wait, internal=internal)


def get_cluster_scheduling_target(core_cluster_operations, cluster_id):
    cluster_configuration = core_cluster_operations.get_cluster_data(cluster_id).read_cluster_config()
    return cluster_configuration.scheduling_target


def submit_application(
        core_cluster_operations,
        spark_cluster_operations,
        cluster_id,
        application,
        remote: bool = False,
        wait: bool = False,
        internal: bool = False,
):
    """
    Submit a spark app
    """
    task = spark_cluster_operations._generate_application_task(core_cluster_operations, cluster_id, application, remote)
    task = affinitize_task_to_master(core_cluster_operations, spark_cluster_operations, cluster_id, task)

    scheduling_target = get_cluster_scheduling_target(core_cluster_operations, cluster_id)
    if scheduling_target is not models.SchedulingTarget.Any:
        schedule_with_target(core_cluster_operations, spark_cluster_operations, cluster_id, scheduling_target, task,
                             wait, internal)
    else:
        # Add task to batch job (which has the same name as cluster_id)
        core_cluster_operations.batch_client.task.add(job_id=cluster_id, task=task)

    if wait:
        helpers.wait_for_task_to_complete(
            job_id=cluster_id, task_id=task.id, batch_client=core_cluster_operations.batch_client)


def submit(
        core_cluster_operations,
        spark_cluster_operations,
        cluster_id: str,
        application: models.ApplicationConfiguration,
        remote: bool = False,
        wait: bool = False,
        internal: bool = False,
):
    try:
        submit_application(core_cluster_operations, spark_cluster_operations, cluster_id, application, remote, wait,
                           internal)
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
