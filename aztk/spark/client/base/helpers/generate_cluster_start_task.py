from typing import List

import azure.batch.models as batch_models

from aztk.spark import models
from aztk.utils import constants, helpers

POOL_ADMIN_USER_IDENTITY = batch_models.UserIdentity(
    auto_user=batch_models.AutoUserSpecification(
        scope=batch_models.AutoUserScope.pool, elevation_level=batch_models.ElevationLevel.admin))


def _get_aztk_environment(cluster_id, worker_on_master, mixed_mode):
    envs = []
    envs.append(batch_models.EnvironmentSetting(name="AZTK_MIXED_MODE", value=helpers.bool_env(mixed_mode)))
    envs.append(batch_models.EnvironmentSetting(name="AZTK_WORKER_ON_MASTER", value=helpers.bool_env(worker_on_master)))
    envs.append(batch_models.EnvironmentSetting(name="AZTK_CLUSTER_ID", value=cluster_id))
    return envs


def __get_docker_credentials(core_base_operations):
    creds = []
    docker = core_base_operations.secrets_configuration.docker
    if docker:
        if docker.endpoint:
            creds.append(batch_models.EnvironmentSetting(name="DOCKER_ENDPOINT", value=docker.endpoint))
        if docker.username:
            creds.append(batch_models.EnvironmentSetting(name="DOCKER_USERNAME", value=docker.username))
        if docker.password:
            creds.append(batch_models.EnvironmentSetting(name="DOCKER_PASSWORD", value=docker.password))

    return creds


def __get_secrets_env(core_base_operations):
    shared_key = core_base_operations.secrets_configuration.shared_key
    service_principal = core_base_operations.secrets_configuration.service_principal
    if shared_key:
        return [
            batch_models.EnvironmentSetting(name="BATCH_SERVICE_URL", value=shared_key.batch_service_url),
            batch_models.EnvironmentSetting(name="BATCH_ACCOUNT_KEY", value=shared_key.batch_account_key),
            batch_models.EnvironmentSetting(name="STORAGE_ACCOUNT_NAME", value=shared_key.storage_account_name),
            batch_models.EnvironmentSetting(name="STORAGE_ACCOUNT_KEY", value=shared_key.storage_account_key),
            batch_models.EnvironmentSetting(name="STORAGE_ACCOUNT_SUFFIX", value=shared_key.storage_account_suffix),
        ]
    else:
        return [
            batch_models.EnvironmentSetting(name="SP_TENANT_ID", value=service_principal.tenant_id),
            batch_models.EnvironmentSetting(name="SP_CLIENT_ID", value=service_principal.client_id),
            batch_models.EnvironmentSetting(name="SP_CREDENTIAL", value=service_principal.credential),
            batch_models.EnvironmentSetting(
                name="SP_BATCH_RESOURCE_ID", value=service_principal.batch_account_resource_id),
            batch_models.EnvironmentSetting(
                name="SP_STORAGE_RESOURCE_ID", value=service_principal.storage_account_resource_id),
        ]


def __cluster_install_cmd(
        zip_resource_file: batch_models.ResourceFile,
        gpu_enabled: bool,
        docker_repo: str = None,
        docker_run_options: str = None,
        file_mounts=None,
):
    """
        For Docker on ubuntu 16.04 - return the command line
        to be run on the start task of the pool to setup spark.
    """
    default_docker_repo = constants.DEFAULT_DOCKER_REPO if not gpu_enabled else constants.DEFAULT_DOCKER_REPO_GPU
    docker_repo = docker_repo or default_docker_repo

    shares = []

    if file_mounts:
        for mount in file_mounts:
            # Create the directory on the node
            shares.append("mkdir -p {0}".format(mount.mount_path))

            # Mount the file share
            shares.append(
                "mount -t cifs //{0}.file.core.windows.net/{2} {3} -o vers=3.0,username={0},password={1},dir_mode=0777,file_mode=0777,sec=ntlmssp".
                format(mount.storage_account_name, mount.storage_account_key, mount.file_share_path, mount.mount_path))

    setup = [
        "time("
        "apt-get -y update;"
        "apt-get -y --no-install-recommends install unzip;"
        "unzip -o $AZ_BATCH_TASK_WORKING_DIR/{0};"
        "chmod 777 $AZ_BATCH_TASK_WORKING_DIR/aztk/node_scripts/setup_host.sh;"
        ") 2>&1".format(zip_resource_file.file_path),
        '/bin/bash $AZ_BATCH_TASK_WORKING_DIR/aztk/node_scripts/setup_host.sh {0} {1} "{2}"'.format(
            constants.DOCKER_SPARK_CONTAINER_NAME,
            docker_repo,
            "" if docker_run_options is None else docker_run_options.replace('"', '\\"'),
        ),
    ]

    commands = shares + setup
    return commands


def generate_cluster_start_task(
        core_base_operations,
        zip_resource_file: batch_models.ResourceFile,
        cluster_id: str,
        gpu_enabled: bool,
        docker_repo: str = None,
        docker_run_options: str = None,
        file_shares: List[models.FileShare] = None,
        mixed_mode: bool = False,
        worker_on_master: bool = True,
):
    """
        This will return the start task object for the pool to be created.
        :param cluster_id str: Id of the cluster(Used for uploading the resource files)
        :param zip_resource_file: Resource file object pointing to the zip file containing scripts to run on the node
    """

    resource_files = [zip_resource_file]
    spark_web_ui_port = constants.DOCKER_SPARK_WEB_UI_PORT
    spark_worker_ui_port = constants.DOCKER_SPARK_WORKER_UI_PORT
    spark_job_ui_port = constants.DOCKER_SPARK_JOB_UI_PORT

    spark_container_name = constants.DOCKER_SPARK_CONTAINER_NAME
    spark_submit_logs_file = constants.SPARK_SUBMIT_LOGS_FILE

    # TODO use certificate
    environment_settings = (__get_secrets_env(core_base_operations) + [
        batch_models.EnvironmentSetting(name="SPARK_WEB_UI_PORT", value=spark_web_ui_port),
        batch_models.EnvironmentSetting(name="SPARK_WORKER_UI_PORT", value=spark_worker_ui_port),
        batch_models.EnvironmentSetting(name="SPARK_JOB_UI_PORT", value=spark_job_ui_port),
        batch_models.EnvironmentSetting(name="SPARK_CONTAINER_NAME", value=spark_container_name),
        batch_models.EnvironmentSetting(name="SPARK_SUBMIT_LOGS_FILE", value=spark_submit_logs_file),
        batch_models.EnvironmentSetting(name="AZTK_GPU_ENABLED", value=helpers.bool_env(gpu_enabled)),
    ] + __get_docker_credentials(core_base_operations) + _get_aztk_environment(cluster_id, worker_on_master,
                                                                               mixed_mode))

    # start task command
    command = __cluster_install_cmd(zip_resource_file, gpu_enabled, docker_repo, docker_run_options, file_shares)

    return batch_models.StartTask(
        command_line=helpers.wrap_commands_in_shell(command),
        resource_files=resource_files,
        environment_settings=environment_settings,
        user_identity=POOL_ADMIN_USER_IDENTITY,
        wait_for_success=True,
    )
