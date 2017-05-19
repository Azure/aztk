from . import util, constants

import random
from datetime import datetime, timedelta
import azure.batch.models as batch_models

def app_submit_cmd(webui_port, app_file_name):
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
            '$AZ_BATCH_TASK_WORKING_DIR/' + app_file_name
    ]

def submit_app(
        batch_client,
        blob_client,
        pool_id,
        app_id,
        app_file_path,
        app_file_name,
        wait):

    """
    Submit a spark app 
    """

    # Upload app resource files to blob storage
    app_resource_file = \
        util.upload_file_to_container(
            blob_client, container_name = app_id, file_path = app_file_path)

    # create command to submit task
    cmd = app_submit_cmd(constants._WEBUI_PORT, app_file_name)
 
    # Get pool size
    pool = batch_client.pool.get(pool_id)
    pool_size = pool.target_dedicated

    # Affinitize task to master node
    master_node_affinity_id = util.get_master_node_id(batch_client, pool_id)

    # Create task
    task = batch_models.TaskAddParameter(
        id=app_id,
        affinity_info=batch_models.AffinityInformation(
            affinity_id=master_node_affinity_id),
        command_line=util.wrap_commands_in_shell(cmd),
        resource_files = [app_resource_file],
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
