from aztk_sdk.utils.command_builder import CommandBuilder
from aztk_sdk.utils import helpers
from aztk_sdk.utils import constants
import azure.batch.models as batch_models
POOL_ADMIN_USER_IDENTITY = batch_models.UserIdentity(
    auto_user=batch_models.AutoUserSpecification(
        scope=batch_models.AutoUserScope.pool,
        elevation_level=batch_models.ElevationLevel.admin))

'''
Cluster create helper methods
'''
def __docker_run_cmd(docker_repo: str = None) -> str:
    """
        Build the docker run command by setting up the environment variables
    """

    cmd = CommandBuilder('docker run')
    cmd.add_option('--net', 'host')
    cmd.add_option('--name', constants.DOCKER_SPARK_CONTAINER_NAME)
    cmd.add_option('-v', '/mnt/batch/tasks:/batch')

    cmd.add_option('-e', 'DOCKER_WORKING_DIR=/batch/startup/wd')
    cmd.add_option('-e', 'AZ_BATCH_ACCOUNT_NAME=$AZ_BATCH_ACCOUNT_NAME')
    cmd.add_option('-e', 'BATCH_ACCOUNT_KEY=$BATCH_ACCOUNT_KEY')
    cmd.add_option('-e', 'BATCH_ACCOUNT_URL=$BATCH_ACCOUNT_URL')
    cmd.add_option('-e', 'STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT_NAME')
    cmd.add_option('-e', 'STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY')
    cmd.add_option('-e', 'STORAGE_ACCOUNT_SUFFIX=$STORAGE_ACCOUNT_SUFFIX')
    cmd.add_option('-e', 'AZ_BATCH_POOL_ID=$AZ_BATCH_POOL_ID')
    cmd.add_option('-e', 'AZ_BATCH_NODE_ID=$AZ_BATCH_NODE_ID')
    cmd.add_option(
        '-e', 'AZ_BATCH_NODE_IS_DEDICATED=$AZ_BATCH_NODE_IS_DEDICATED')
    cmd.add_option('-e', 'SPARK_WEB_UI_PORT=$SPARK_WEB_UI_PORT')
    cmd.add_option('-e', 'SPARK_WORKER_UI_PORT=$SPARK_WORKER_UI_PORT')
    cmd.add_option('-e', 'SPARK_JUPYTER_PORT=$SPARK_JUPYTER_PORT')
    cmd.add_option('-e', 'SPARK_JOB_UI_PORT=$SPARK_JOB_UI_PORT')
    cmd.add_option('-p', '8080:8080')
    cmd.add_option('-p', '7077:7077')
    cmd.add_option('-p', '4040:4040')
    cmd.add_option('-p', '8888:8888')
    cmd.add_option('-d', docker_repo)
    cmd.add_argument('/bin/bash /batch/startup/wd/docker_main.sh')
    return cmd.to_str()

def __get_docker_credentials(spark_client):
    creds = []

    if spark_client.secrets_config.docker_endpoint:
        creds.append(batch_models.EnvironmentSetting(
            name="DOCKER_ENDPOINT", value=spark_client.secrets_config.docker_endpoint))
    if spark_client.secrets_config.docker_username:
        creds.append(batch_models.EnvironmentSetting(
            name="DOCKER_USERNAME", value=spark_client.secrets_config.docker_username))
    if spark_client.secrets_config.docker_password:
        creds.append(batch_models.EnvironmentSetting(
            name="DOCKER_PASSWORD", value=spark_client.secrets_config.docker_password))

    return creds

def __cluster_install_cmd(zip_resource_file: batch_models.ResourceFile,
                            docker_repo: str = None):
    """
        For Docker on ubuntu 16.04 - return the command line
        to be run on the start task of the pool to setup spark.
    """
    docker_repo = docker_repo or constants.DEFAULT_DOCKER_REPO

    ret = [
        'apt-get -y clean',
        'apt-get -y update',
        'apt-get install --fix-missing',
        'apt-get -y install unzip',
        'unzip $AZ_BATCH_TASK_WORKING_DIR/{0}'.format(
            zip_resource_file.file_path),
        'chmod 777 $AZ_BATCH_TASK_WORKING_DIR/setup_node.sh',
        '/bin/bash $AZ_BATCH_TASK_WORKING_DIR/setup_node.sh {0} {1} "{2}"'.format(
            constants.DOCKER_SPARK_CONTAINER_NAME,
            docker_repo,
            __docker_run_cmd(docker_repo)),
    ]

    return ret

def generate_cluster_start_task(
        spark_client,
        zip_resource_file: batch_models.ResourceFile,
        docker_repo: str = None):
    """
        This will return the start task object for the pool to be created.
        :param cluster_id str: Id of the cluster(Used for uploading the resource files)
        :param zip_resource_file: Resource file object pointing to the zip file containing scripts to run on the node
    """

    resource_files = [zip_resource_file]

    spark_web_ui_port = constants.DOCKER_SPARK_WEB_UI_PORT
    spark_worker_ui_port = constants.DOCKER_SPARK_WORKER_UI_PORT
    spark_jupyter_port = constants.DOCKER_SPARK_JUPYTER_PORT
    spark_job_ui_port = constants.DOCKER_SPARK_JOB_UI_PORT

    # TODO use certificate
    environment_settings = [
        batch_models.EnvironmentSetting(
            name="BATCH_ACCOUNT_KEY", value=spark_client.batch_config.account_key),
        batch_models.EnvironmentSetting(
            name="BATCH_ACCOUNT_URL", value=spark_client.batch_config.account_url),
        batch_models.EnvironmentSetting(
            name="STORAGE_ACCOUNT_NAME", value=spark_client.blob_config.account_name),
        batch_models.EnvironmentSetting(
            name="STORAGE_ACCOUNT_KEY", value=spark_client.blob_config.account_key),
        batch_models.EnvironmentSetting(
            name="STORAGE_ACCOUNT_SUFFIX", value=spark_client.blob_config.account_suffix),
        batch_models.EnvironmentSetting(
            name="SPARK_WEB_UI_PORT", value=spark_web_ui_port),
        batch_models.EnvironmentSetting(
            name="SPARK_WORKER_UI_PORT", value=spark_worker_ui_port),
        batch_models.EnvironmentSetting(
            name="SPARK_JUPYTER_PORT", value=spark_jupyter_port),
        batch_models.EnvironmentSetting(
            name="SPARK_JOB_UI_PORT", value=spark_job_ui_port),
    ] + __get_docker_credentials(spark_client)

    # start task command
    command = __cluster_install_cmd(zip_resource_file, docker_repo)

    return batch_models.StartTask(
        command_line=helpers.wrap_commands_in_shell(command),
        resource_files=resource_files,
        environment_settings=environment_settings,
        user_identity=POOL_ADMIN_USER_IDENTITY,
        wait_for_success=True)
