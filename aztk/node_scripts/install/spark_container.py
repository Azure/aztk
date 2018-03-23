import subprocess

from aztk.internal import DockerCmd
from aztk.utils import constants

def start_spark_container(
        docker_repo: str = None,
        gpu_enabled: bool = False,
        file_mounts = None,
        plugins = None,
        mixed_mode = False):

    cmd = DockerCmd(
        name=constants.DOCKER_SPARK_CONTAINER_NAME,
        docker_repo=docker_repo,
        cmd="/bin/bash /mnt/batch/tasks/startup/wd/aztk/node_scripts/docker_main.sh",
        gpu_enabled=gpu_enabled)

    if file_mounts:
        for mount in file_mounts:
            cmd.share_folder(mount.mount_path)
    cmd.share_folder('/mnt/batch/tasks')

    cmd.pass_env('AZTK_WORKING_DIR')
    cmd.pass_env('AZ_BATCH_ACCOUNT_NAME')
    cmd.pass_env('BATCH_ACCOUNT_KEY')
    cmd.pass_env('BATCH_SERVICE_URL')
    cmd.pass_env('STORAGE_ACCOUNT_NAME')
    cmd.pass_env('STORAGE_ACCOUNT_KEY')
    cmd.pass_env('STORAGE_ACCOUNT_SUFFIX')

    cmd.pass_env('SP_TENANT_ID')
    cmd.pass_env('SP_CLIENT_ID')
    cmd.pass_env('SP_CREDENTIAL')
    cmd.pass_env('SP_BATCH_RESOURCE_ID')
    cmd.pass_env('SP_STORAGE_RESOURCE_ID')

    cmd.pass_env('AZ_BATCH_POOL_ID')
    cmd.pass_env('AZ_BATCH_NODE_ID')
    cmd.pass_env('AZ_BATCH_NODE_IS_DEDICATED')

    cmd.pass_env('AZTK_WORKER_ON_MASTER')
    cmd.pass_env('AZTK_MIXED_MODE')
    cmd.pass_env('AZTK_IS_MASTER')
    cmd.pass_env('AZTK_IS_WORKER')
    cmd.pass_env('AZTK_MASTER_IP')

    cmd.pass_env('SPARK_WEB_UI_PORT')
    cmd.pass_env('SPARK_WORKER_UI_PORT')
    cmd.pass_env('SPARK_CONTAINER_NAME')
    cmd.pass_env('SPARK_SUBMIT_LOGS_FILE')
    cmd.pass_env('SPARK_JOB_UI_PORT')

    cmd.open_port(8080)       # Spark Master UI
    cmd.add_option(7077)       # Spark Master
    cmd.add_option(7337)       # Spark Shuffle Service
    cmd.add_option(4040)       # Job UI
    cmd.add_option(18080)     # Spark History Server UI
    cmd.add_option(3022)       # Docker SSH

    subprocess.call(cmd.to_str(), shell=True)
