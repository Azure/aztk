import os

import azure.batch.models as batch_models
import yaml

from aztk.error import AztkError
from aztk.utils import helpers
from aztk.utils.command_builder import CommandBuilder


def __get_node(spark_client, node_id: str, cluster_id: str) -> batch_models.ComputeNode:
    return spark_client.batch_client.compute_node.get(cluster_id, node_id)


def generate_task(spark_client, container_id, application, remote=False):
    resource_files = []

    # The application provided is not hosted remotely and therefore must be uploaded
    if not remote:
        app_resource_file = helpers.upload_file_to_container(
            container_name=container_id,
            application_name=application.name,
            file_path=application.application,
            blob_client=spark_client.blob_client,
            use_full_path=False,
        )

        # Upload application file
        resource_files.append(app_resource_file)

        application.application = "$AZ_BATCH_TASK_WORKING_DIR/" + os.path.basename(application.application)

    # Upload dependent JARS
    jar_resource_file_paths = []
    for jar in application.jars:
        current_jar_resource_file_path = helpers.upload_file_to_container(
            container_name=container_id,
            application_name=application.name,
            file_path=jar,
            blob_client=spark_client.blob_client,
            use_full_path=False,
        )
        jar_resource_file_paths.append(current_jar_resource_file_path)
        resource_files.append(current_jar_resource_file_path)

    # Upload dependent python files
    py_files_resource_file_paths = []
    for py_file in application.py_files:
        current_py_files_resource_file_path = helpers.upload_file_to_container(
            container_name=container_id,
            application_name=application.name,
            file_path=py_file,
            blob_client=spark_client.blob_client,
            use_full_path=False,
        )
        py_files_resource_file_paths.append(current_py_files_resource_file_path)
        resource_files.append(current_py_files_resource_file_path)

    # Upload other dependent files
    files_resource_file_paths = []
    for file in application.files:
        files_resource_file_path = helpers.upload_file_to_container(
            container_name=container_id,
            application_name=application.name,
            file_path=file,
            blob_client=spark_client.blob_client,
            use_full_path=False,
        )
        files_resource_file_paths.append(files_resource_file_path)
        resource_files.append(files_resource_file_path)

    # Upload application definition
    application.jars = [os.path.basename(jar) for jar in application.jars]
    application.py_files = [os.path.basename(py_files) for py_files in application.py_files]
    application.files = [os.path.basename(files) for files in application.files]
    application_definition_file = helpers.upload_text_to_container(
        container_name=container_id,
        application_name=application.name,
        file_path="application.yaml",
        content=yaml.dump(vars(application)),
        blob_client=spark_client.blob_client,
    )
    resource_files.append(application_definition_file)

    # create command to submit task
    task_cmd = CommandBuilder("sudo docker exec")
    task_cmd.add_argument("-i")
    task_cmd.add_option("-e", "AZ_BATCH_TASK_WORKING_DIR=$AZ_BATCH_TASK_WORKING_DIR")
    task_cmd.add_option("-e", "STORAGE_LOGS_CONTAINER={0}".format(container_id))
    task_cmd.add_argument("spark /bin/bash >> output.log 2>&1")
    task_cmd.add_argument(
        r'-c "source ~/.bashrc; '
        r"export PYTHONPATH=$PYTHONPATH:\$AZTK_WORKING_DIR; "
        r"cd \$AZ_BATCH_TASK_WORKING_DIR; "
        r'\$AZTK_WORKING_DIR/.aztk-env/.venv/bin/python \$AZTK_WORKING_DIR/aztk/node_scripts/submit.py"')

    # Create task
    task = batch_models.TaskAddParameter(
        id=application.name,
        command_line=helpers.wrap_commands_in_shell([task_cmd.to_str()]),
        resource_files=resource_files,
        constraints=batch_models.TaskConstraints(max_task_retry_count=application.max_retry_count),
        user_identity=batch_models.UserIdentity(
            auto_user=batch_models.AutoUserSpecification(
                scope=batch_models.AutoUserScope.task, elevation_level=batch_models.ElevationLevel.admin)),
    )

    return task


def affinitize_task_to_master(spark_client, cluster_id, task):
    cluster = spark_client.get_cluster(cluster_id)
    if cluster.master_node_id is None:
        raise AztkError("Master has not yet been selected. Please wait until the cluster is finished provisioning.")
    master_node = spark_client.batch_client.compute_node.get(pool_id=cluster_id, node_id=cluster.master_node_id)
    task.affinity_info = batch_models.AffinityInformation(affinity_id=master_node.affinity_id)
    return task


def submit_application(spark_client, cluster_id, application, remote: bool = False, wait: bool = False):
    """
    Submit a spark app
    """
    task = generate_task(spark_client, cluster_id, application, remote)
    task = affinitize_task_to_master(spark_client, cluster_id, task)

    # Add task to batch job (which has the same name as cluster_id)
    job_id = cluster_id
    spark_client.batch_client.task.add(job_id=job_id, task=task)

    if wait:
        helpers.wait_for_task_to_complete(job_id=job_id, task_id=task.id, batch_client=spark_client.batch_client)
