from datetime import timedelta
from typing import List
from dtde.core import CommandBuilder
import azure.batch.models as batch_models
from . import azure_api, util

def app_submit_cmd(
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
    spark_submit_cmd = CommandBuilder('$SPARK_HOME/bin/spark-submit')

    spark_submit_cmd.add_option('--name', name)
    spark_submit_cmd.add_option('--master', 'spark://${MASTER_NODE%:*}:7077')
    spark_submit_cmd.add_option('--class', main_class)
    spark_submit_cmd.add_option('--class', main_class)
    spark_submit_cmd.add_option('--jars', jars and ','.join(jars))
    spark_submit_cmd.add_option('--py-files', py_files and ','.join(py_files))
    spark_submit_cmd.add_option('--jars', files and ','.join(files))
    spark_submit_cmd.add_option('--driver-java-options', driver_java_options)
    spark_submit_cmd.add_option('--driver-library-path', driver_library_path)
    spark_submit_cmd.add_option('--driver-class-path', driver_class_path)
    spark_submit_cmd.add_option('--driver-memory', driver_memory)
    spark_submit_cmd.add_option('--executor-memory', executor_memory)
    spark_submit_cmd.add_option('--driver-cores', driver_cores)
    spark_submit_cmd.add_option('--executor-cores', executor_cores)
    spark_submit_cmd.add_argument(
        '$AZ_BATCH_TASK_WORKING_DIR/' + app + ' ' + ' '.join(app_args))

    return [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',

        # set the runtime to python 3
        'export PYSPARK_PYTHON=/usr/bin/python3',
        'export PYSPARK_DRIVER_PYTHON=python3',

        # get master node ip
        'export MASTER_NODE=$(cat $SPARK_HOME/conf/master)',
        'echo "Master node ip is $MASTER_NODE"',
        spark_submit_cmd.to_str(),
    ]


def submit_app(
        pool_id,
        name,
        app,
        app_args,
        wait,
        main_class,
        jars,
        py_files,
        files,
        driver_java_options,
        driver_library_path,
        driver_class_path,
        driver_memory,
        executor_memory,
        driver_cores,
        executor_cores):
    """
    Submit a spark app
    """
    batch_client = azure_api.get_batch_client()

    resource_files = []

    # Upload application file
    resource_files.append(
        util.upload_file_to_container(container_name=name, file_path=app, use_full_path=True))

    # Upload dependent JARS
    for jar in jars:
        resource_files.append(
            util.upload_file_to_container(container_name=name, file_path=jar, use_full_path=True))

    # Upload dependent python files
    for py_file in py_files:
        resource_files.append(
            util.upload_file_to_container(container_name=name, file_path=py_file, use_full_path=True))

    # Upload other dependent files
    for file in files:
        resource_files.append(
            util.upload_file_to_container(container_name=name, file_path=file, use_full_path=True))

    # create command to submit task
    cmd = app_submit_cmd(
        name=name,
        app=app,
        app_args=app_args,
        main_class=main_class,
        jars=jars,
        py_files=py_files,
        files=files,
        driver_java_options=driver_java_options,
        driver_library_path=driver_library_path,
        driver_class_path=driver_class_path,
        driver_memory=driver_memory,
        executor_memory=executor_memory,
        driver_cores=driver_cores,
        executor_cores=executor_cores)

    # Get pool size
    pool = batch_client.pool.get(pool_id)
    pool_size = util.get_cluster_total_target_nodes(pool)

    # Affinitize task to master node
    master_node_affinity_id = util.get_master_node_id(pool_id)

    # Create task
    task = batch_models.TaskAddParameter(
        id=name,
        affinity_info=batch_models.AffinityInformation(
            affinity_id=master_node_affinity_id),
        command_line=util.wrap_commands_in_shell(cmd),
        resource_files=resource_files,
        user_identity=batch_models.UserIdentity(
            auto_user=batch_models.AutoUserSpecification(
                scope=batch_models.AutoUserScope.task,
                elevation_level=batch_models.ElevationLevel.admin))
    )

    # Add task to batch job (which has the same name as pool_id)
    job_id = pool_id
    batch_client.task.add(job_id=job_id, task=task)

    # Wait for the app to finish
    if wait == True:
        util.wait_for_tasks_to_complete(
            job_id,
            timedelta(minutes=60))
