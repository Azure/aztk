from . import util, constants

import random
from datetime import datetime, timedelta
import azure.batch.models as batch_models

def app_submit_cmd(
        webui_port, 
        app, 
        app_args, 
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

    main_class_option = '--class ' + main_class + ' ' if main_class else ''
    jars_option = '--jars "' + ','.join(jars) + '" ' if jars else ''
    py_files_option = '--py-files "' + ','.join(py_files) + '" ' if py_files else ''
    files_option = '--jars "' + ','.join(files) + '" ' if files else ''
    driver_java_options = '--driver-java-options ' + driver_java_options + ' ' if driver_java_options else ''
    driver_library_path = '--driver-library-path ' + driver_library_path + ' ' if driver_library_path else ''
    driver_class_path = '--driver-class-path ' + driver_class_path + ' ' if driver_class_path else ''
    driver_memory_option = '--driver-memory ' + driver_memory + ' ' if driver_memory else ''
    executor_memory_option = '--executor-memory ' + executor_memory + ' ' if executor_memory else ''
    driver_cores_option = '--driver-cores ' + driver_cores + ' ' if driver_cores else ''
    executor_cores_option = '--executor-cores ' + executor_cores + ' ' if executor_cores else ''

    return [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',

        # set the runtime to python 3
        'export PYSPARK_PYTHON=/usr/bin/python3',
        'export PYSPARK_DRIVER_PYTHON=python3',

        # get master node ip
        'export MASTER_NODE=$(cat $SPARK_HOME/conf/master)',

        # execute spark-submit on the specified app 
        '$SPARK_HOME/bin/spark-submit ' +
            '--master spark://${MASTER_NODE%:*}:7077 ' + 
            main_class_option +
            jars_option +
            py_files_option +
            files_option +
            driver_java_options +
            driver_library_path +
            driver_class_path +
            driver_memory_option +
            executor_memory_option +
            driver_cores_option +
            executor_cores_option +
            '$AZ_BATCH_TASK_WORKING_DIR/' + app + ' ' + ' '.join(app_args)
    ]

def submit_app(
        batch_client,
        blob_client,
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

    resource_files = []

    # Upload application file
    resource_files.append(
        util.upload_file_to_container(
            blob_client, container_name = name, file_path = app, use_full_path = True))

    # Upload dependent JARS
    for jar in jars:
        resource_files.append(
            util.upload_file_to_container(
                blob_client, container_name = name, file_path = jar, use_full_path = True))

    # Upload dependent python files 
    for py_file in py_files:
        resource_files.append(
            util.upload_file_to_container(
                blob_client, container_name = name, file_path = py_file, use_full_path = True))

    # Upload other dependent files 
    for file in files:
        resource_files.append(
            util.upload_file_to_container(
                blob_client, container_name = name, file_path = file, use_full_path = True))

    # create command to submit task
    cmd = app_submit_cmd(
        webui_port=constants._WEBUI_PORT, 
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
    master_node_affinity_id = util.get_master_node_id(batch_client, pool_id)

    # Create task
    task = batch_models.TaskAddParameter(
        id=name,
        affinity_info=batch_models.AffinityInformation(
            affinity_id=master_node_affinity_id),
        command_line=util.wrap_commands_in_shell(cmd),
        resource_files = resource_files,
        user_identity = batch_models.UserIdentity(
            auto_user= batch_models.AutoUserSpecification(
                scope= batch_models.AutoUserScope.task,
                elevation_level= batch_models.ElevationLevel.admin))
    )

    # Add task to batch job (which has the same name as pool_id)
    job_id = pool_id
    batch_client.task.add(job_id = job_id, task = task)

    # Wait for the app to finish
    if wait == True:
        util.wait_for_tasks_to_complete(
            batch_client,
            job_id,
            timedelta(minutes=60))
