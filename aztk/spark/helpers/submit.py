from typing import List

import azure.batch.models as batch_models
from aztk.utils import constants, helpers
from aztk.utils.command_builder import CommandBuilder

'''
Submit helper methods
'''


def __get_node(spark_client, node_id: str, cluster_id: str) -> batch_models.ComputeNode:
    return spark_client.batch_client.compute_node.get(cluster_id, node_id)


def __app_submit_cmd(
        spark_client,
        cluster_id: str,
        name: str,
        app: str,
        app_args: str,
        main_class: str,
        jars: List[str],
        py_files: List[str],
        files: List[str],
        driver_java_options: str,
        driver_library_path: str,
        driver_class_path: str,
        driver_memory: str,
        executor_memory: str,
        driver_cores: str,
        executor_cores: str):
    cluster = spark_client.get_cluster(cluster_id)
    master_id = cluster.master_node_id
    master_ip = __get_node(spark_client, master_id, cluster_id).ip_address

    spark_home = constants.DOCKER_SPARK_HOME

    # set file paths to correct path on container
    files_path = '/batch/workitems/{0}/{1}/{2}/wd/'.format(cluster_id, "job-1", name)
    jars = [files_path + jar for jar in jars]
    py_files = [files_path + py_file for py_file in py_files]
    files = [files_path + f for f in files]

    # 2>&1 redirect stdout and stderr to be in the same file
    spark_submit_cmd = CommandBuilder(
        '{0}/bin/spark-submit'.format(spark_home))
    spark_submit_cmd.add_option(
        '--master', 'spark://{0}:7077'.format(master_ip))
    spark_submit_cmd.add_option('--name', name)
    spark_submit_cmd.add_option('--class', main_class)
    spark_submit_cmd.add_option('--jars', jars and ','.join(jars))
    spark_submit_cmd.add_option('--py-files', py_files and ','.join(py_files))
    spark_submit_cmd.add_option('--files', files and ','.join(files))
    spark_submit_cmd.add_option('--driver-java-options', driver_java_options)
    spark_submit_cmd.add_option('--driver-library-path', driver_library_path)
    spark_submit_cmd.add_option('--driver-class-path', driver_class_path)
    spark_submit_cmd.add_option('--driver-memory', driver_memory)
    spark_submit_cmd.add_option('--executor-memory', executor_memory)
    spark_submit_cmd.add_option('--driver-cores', driver_cores)
    spark_submit_cmd.add_option('--executor-cores', executor_cores)

    spark_submit_cmd.add_argument(
        '/batch/workitems/{0}/{1}/{2}/wd/'.format(cluster_id, "job-1", name) +
        app + ' ' + ' '.join(['\'' + app_arg + '\'' for app_arg in app_args if app_args]))

    if cluster.gpu_enabled:
        docker_exec_cmd = CommandBuilder('sudo nvidia-docker exec')
    else:
        docker_exec_cmd = CommandBuilder('sudo docker exec')
    
    docker_exec_cmd.add_option('-i', constants.DOCKER_SPARK_CONTAINER_NAME)
    docker_exec_cmd.add_argument('/bin/bash  >> {0} 2>&1 -c \"cd '.format(
        constants.SPARK_SUBMIT_LOGS_FILE) + files_path + '; ' + spark_submit_cmd.to_str() + '\"')

    return [
        docker_exec_cmd.to_str()
    ]


def submit_application(spark_client, cluster_id, application, wait: bool = False):
    """
    Submit a spark app
    """

    resource_files = []

    app_resource_file = helpers.upload_file_to_container(container_name=application.name,
                                                         file_path=application.application,
                                                         blob_client=spark_client.blob_client,
                                                         use_full_path=False)

    # Upload application file
    resource_files.append(app_resource_file)

    # Upload dependent JARS
    jar_resource_file_paths = []
    for jar in application.jars:
        current_jar_resource_file_path = helpers.upload_file_to_container(container_name=application.name,
                                                                          file_path=jar,
                                                                          blob_client=spark_client.blob_client,
                                                                          use_full_path=False)
        jar_resource_file_paths.append(current_jar_resource_file_path)
        resource_files.append(current_jar_resource_file_path)

    # Upload dependent python files
    py_files_resource_file_paths = []
    for py_file in application.py_files:
        current_py_files_resource_file_path = helpers.upload_file_to_container(container_name=application.name,
                                                                               file_path=py_file,
                                                                               blob_client=spark_client.blob_client,
                                                                               use_full_path=False)
        py_files_resource_file_paths.append(
            current_py_files_resource_file_path)
        resource_files.append(current_py_files_resource_file_path)

    # Upload other dependent files
    files_resource_file_paths = []
    for file in application.files:
        files_resource_file_path = helpers.upload_file_to_container(container_name=application.name,
                                                                    file_path=file,
                                                                    blob_client=spark_client.blob_client,
                                                                    use_full_path=False)
        files_resource_file_paths.append(files_resource_file_path)
        resource_files.append(files_resource_file_path)

    # create command to submit task
    cmd = __app_submit_cmd(
        spark_client=spark_client,
        cluster_id=cluster_id,
        name=application.name,
        app=app_resource_file.file_path,
        app_args=application.application_args,
        main_class=application.main_class,
        jars=[jar_resource_file_path.file_path for jar_resource_file_path in jar_resource_file_paths],
        py_files=[py_files_resource.file_path for py_files_resource in py_files_resource_file_paths],
        files=[file_resource_file_path.file_path for file_resource_file_path in files_resource_file_paths],
        driver_java_options=application.driver_java_options,
        driver_library_path=application.driver_library_path,
        driver_class_path=application.driver_class_path,
        driver_memory=application.driver_memory,
        executor_memory=application.executor_memory,
        driver_cores=application.driver_cores,
        executor_cores=application.executor_cores)

    # Get cluster size
    cluster = spark_client.get_cluster(cluster_id)

    # Affinitize task to master node
    # master_node_affinity_id = helpers.get_master_node_id(cluster_id, spark_client.batch_client)
    rls = spark_client.get_remote_login_settings(cluster.id, cluster.master_node_id)

    # Create task
    task = batch_models.TaskAddParameter(
        id=application.name,
        affinity_info=batch_models.AffinityInformation(
            affinity_id=cluster.master_node_id),
        command_line=helpers.wrap_commands_in_shell(cmd),
        resource_files=resource_files,
        user_identity=batch_models.UserIdentity(
            auto_user=batch_models.AutoUserSpecification(
                scope=batch_models.AutoUserScope.task,
                elevation_level=batch_models.ElevationLevel.admin))
    )

    # Add task to batch job (which has the same name as cluster_id)
    job_id = cluster_id
    spark_client.batch_client.task.add(job_id=job_id, task=task)

    if wait:
        helpers.wait_for_task_to_complete(job_id=job_id, task_id=task.id, batch_client=spark_client.batch_client)
