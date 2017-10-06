import os
import yaml
import pathlib
from distutils.dir_util import copy_tree
from datetime import datetime, timedelta
from aztk.core import CommandBuilder, ssh
from subprocess import call
from typing import List
from shutil import copy, rmtree
from aztk.models import Software
import aztk.error as error
import azure.batch.models as batch_models
from . import constants, upload_node_scripts, util, log
from aztk.error import ClusterNotReadyError, AztkError
from collections import namedtuple
import aztk.config as config
import getpass
POOL_ADMIN_USER_IDENTITY = batch_models.UserIdentity(
    auto_user=batch_models.AutoUserSpecification(
        scope=batch_models.AutoUserScope.pool,
        elevation_level=batch_models.ElevationLevel.admin))


class Cluster:

    def __init__(self, batch_client, blob_client, batch_config, blob_config, secrets_config):
        self.batch_client = batch_client
        self.blob_client = blob_client
        self.batch_config = batch_config
        self.blob_config = blob_config
        self.secrets_config = secrets_config

    def cluster_install_cmd(self,
                            zip_resource_file: batch_models.ResourceFile,
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
                self.docker_run_cmd(docker_repo)),
        ]

        return ret

    def docker_run_cmd(self, docker_repo: str = None) -> str:
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
        cmd.add_option('-e', 'SPARK_MASTER_UI_PORT=$SPARK_MASTER_UI_PORT')
        cmd.add_option('-e', 'SPARK_WORKER_UI_PORT=$SPARK_WORKER_UI_PORT')
        cmd.add_option('-e', 'SPARK_JUPYTER_PORT=$SPARK_JUPYTER_PORT')
        cmd.add_option('-e', 'SPARK_WEB_UI_PORT=$SPARK_WEB_UI_PORT')
        cmd.add_option('-p', '8080:8080')
        cmd.add_option('-p', '7077:7077')
        cmd.add_option('-p', '4040:4040')
        cmd.add_option('-p', '8888:8888')
        cmd.add_option('-d', docker_repo)
        cmd.add_argument('/bin/bash /batch/startup/wd/docker_main.sh')
        return cmd.to_str()

    def generate_cluster_start_task(
            self,
            zip_resource_file: batch_models.ResourceFile,
            docker_repo: str = None):
        """
            This will return the start task object for the pool to be created.
            :param cluster_id str: Id of the cluster(Used for uploading the resource files)
            :param zip_resource_file: Resource file object pointing to the zip file containing scripts to run on the node
        """

        resource_files = [zip_resource_file]

        spark_master_ui_port = constants.DOCKER_SPARK_MASTER_UI_PORT
        spark_worker_ui_port = constants.DOCKER_SPARK_WORKER_UI_PORT
        spark_jupyter_port = constants.DOCKER_SPARK_JUPYTER_PORT
        spark_web_ui_port = constants.DOCKER_SPARK_WEB_UI_PORT

        # TODO use certificate
        environment_settings = [
            batch_models.EnvironmentSetting(
                name="BATCH_ACCOUNT_KEY", value=self.batch_config.account_key),
            batch_models.EnvironmentSetting(
                name="BATCH_ACCOUNT_URL", value=self.batch_config.account_url),
            batch_models.EnvironmentSetting(
                name="STORAGE_ACCOUNT_NAME", value=self.blob_config.account_name),
            batch_models.EnvironmentSetting(
                name="STORAGE_ACCOUNT_KEY", value=self.blob_config.account_key),
            batch_models.EnvironmentSetting(
                name="STORAGE_ACCOUNT_SUFFIX", value=self.blob_config.account_suffix),
            batch_models.EnvironmentSetting(
                name="SPARK_MASTER_UI_PORT", value=spark_master_ui_port),
            batch_models.EnvironmentSetting(
                name="SPARK_WORKER_UI_PORT", value=spark_worker_ui_port),
            batch_models.EnvironmentSetting(
                name="SPARK_JUPYTER_PORT", value=spark_jupyter_port),
            batch_models.EnvironmentSetting(
                name="SPARK_WEB_UI_PORT", value=spark_web_ui_port),
        ] + self.get_docker_credentials()

        # start task command
        command = self.cluster_install_cmd(zip_resource_file, docker_repo)

        return batch_models.StartTask(
            command_line=util.wrap_commands_in_shell(command),
            resource_files=resource_files,
            environment_settings=environment_settings,
            user_identity=POOL_ADMIN_USER_IDENTITY,
            wait_for_success=True)

    def upload_custom_script_config(self, custom_scripts=None):
        with open(os.path.join(constants.CUSTOM_SCRIPTS_DEST, 'custom-scripts.yaml'), 'w+') as f:
            f.write(yaml.dump(custom_scripts, default_flow_style=False))

    def move_custom_scripts(self, custom_scripts=None):
        if custom_scripts is None:
            return

        # remove lingering custom_scripts from a previous cluster create
        self.clean_up_custom_scripts()

        os.mkdir(os.path.join(constants.ROOT_PATH, 'node_scripts', 'custom-scripts'))
        custom_scripts_dir = os.path.join(constants.ROOT_PATH, 'node_scripts', 'custom-scripts')

        for index, custom_script in enumerate(custom_scripts):
            '''
                custom_script: {script: str, runOn: str}
            '''
            path = pathlib.Path(custom_script['script'])
            dest_file = pathlib.Path(custom_scripts_dir, path.name)
            new_file_name = str(index) + '_' + dest_file.name
            src = str(path.absolute())
            dest = str(pathlib.Path(dest_file.with_name(new_file_name)).absolute())

            if path.is_dir():
                copy_tree(src, dest)
            else:
                copy(src, dest)

            custom_scripts[index]['script'] = dest_file.with_name(new_file_name).name

        self.upload_custom_script_config(custom_scripts)

    def clean_up_custom_scripts(self):
        if os.path.exists(os.path.join(constants.ROOT_PATH, constants.CUSTOM_SCRIPTS_DEST)):
            rmtree(constants.CUSTOM_SCRIPTS_DEST)

    def get_docker_credentials(self):
        creds = []

        secrets_config = config.SecretsConfig()
        secrets_config.load_secrets_config()

        if secrets_config.docker_endpoint:
            creds.append(batch_models.EnvironmentSetting(
                name="DOCKER_ENDPOINT", value=secrets_config.docker_endpoint))
        if secrets_config.docker_username:
            creds.append(batch_models.EnvironmentSetting(
                name="DOCKER_USERNAME", value=secrets_config.docker_username))
        if secrets_config.docker_password:
            creds.append(batch_models.EnvironmentSetting(
                name="DOCKER_PASSWORD", value=secrets_config.docker_password))

        return creds

    def _get_ssh_key_or_prompt(self, ssh_key, username, password):
        # Get user ssh key, prompt for password if necessary
        ssh_key = ssh.get_user_public_key(ssh_key, self.secrets_config)
        if username is not None and password is None and ssh_key is None:
            password = getpass.getpass("Please input a password for user '{0}': ".format(username))
            confirm_password = getpass.getpass("Please confirm your password for user '{0}': ".format(username))
            if password != confirm_password:
                raise AztkError("Password confirmation did not match, please try again.")
            if not password:
                raise AztkError(
                    "Password is empty, cannot add user to cluster. Provide a ssh public key in .aztk/secrets.yaml. Or provide an ssh-key or password with commnad line parameters (--ssh-key or --password).")
        return ssh_key, password

    def create_cluster(
            self,
            custom_scripts: List[object],
            cluster_id: str,
            vm_count,
            vm_low_pri_count,
            vm_size,
            username: str,
            password: str = None,
            ssh_key: str = None,
            docker_repo: str = None,
            wait=True):
        """
            Create a spark cluster
            :param custom_scripts: List of objects containing each scripts path and execution location (master/worker/all-nodes)
            :parm cluster_id: Id of the cluster
            :param vm_count: Number of node in the cluster
            :param vm_low_pri_count: Number of low pri node in the cluster
            :param vm_size: Tier of the node(standard_a2, standard_g2, etc.)
            :param username: Optional username of user to add to the pool when ready(Need wait to be True)
            :param password: Optional password of user to add to the pool when ready(Need wait to be True)
            :param wait: If this function should wait for the cluster to be ready(Master and all slave booted)
        """
        # copy spark conf files if they exist
        config.load_spark_config()

        # move custom scripts to node_scripts/ for upload
        self.move_custom_scripts(custom_scripts)

        # upload start task scripts
        zip_resource_file = upload_node_scripts.zip_and_upload(self.blob_client)

        # clean up spark conf files
        config.cleanup_spark_config()

        # Clean up custom scripts
        self.clean_up_custom_scripts()

        # vm image
        publisher = 'Canonical'
        offer = 'UbuntuServer'
        sku = '16.04'

        # reuse pool_id as job_id
        pool_id = cluster_id
        job_id = cluster_id

        # Get a verified node agent sku
        sku_to_use, image_ref_to_use = \
            util.select_latest_verified_vm_image_with_node_agent_sku(
                publisher, offer, sku, self.batch_client)

        # Confiure the pool
        pool = batch_models.PoolAddParameter(
            id=pool_id,
            virtual_machine_configuration=batch_models.VirtualMachineConfiguration(
                image_reference=image_ref_to_use,
                node_agent_sku_id=sku_to_use),
            vm_size=vm_size,
            target_dedicated_nodes=vm_count,
            target_low_priority_nodes=vm_low_pri_count,
            start_task=self.generate_cluster_start_task(
                zip_resource_file, docker_repo),
            enable_inter_node_communication=True,
            max_tasks_per_node=1,
            metadata=[
                batch_models.MetadataItem(
                    name=constants.AZTK_SOFTWARE_METADATA_KEY, value=Software.spark),
            ])

        # Check for ssh key, if None, prompt for password
        ssh_key, password = self._get_ssh_key_or_prompt(username=username, ssh_key=ssh_key, password=password)

        # Create the pool + create user for the pool
        util.create_pool_if_not_exist(pool, self.batch_client)

        # Create job
        job = batch_models.JobAddParameter(
            id=job_id,
            pool_info=batch_models.PoolInformation(pool_id=pool_id))

        # Add job to batch
        self.batch_client.job.add(job)

        # Wait for the app to finish
        if wait:
            util.wait_for_master_to_be_ready(pool_id, self.batch_client)

            if username is not None:
                self.create_user(pool_id, username, password, ssh_key)

    def create_user(
            self,
            cluster_id: str,
            username: str,
            password: str = None,
            ssh_key: str = None) -> str:
        """
            Create a cluster user
            :param cluster_id: id of the spark cluster
            :param username: username of the user to add
            :param password: password of the user to add
        """
        # Check for ssh key, if None, prompt for password
        ssh_key, password = self._get_ssh_key_or_prompt(username=username, ssh_key=ssh_key, password=password)

        # Create new ssh user for the master node
        self.batch_client.compute_node.add_user(
            cluster_id,
            util.get_master_node_id(cluster_id, self.batch_client),
            batch_models.ComputeNodeUser(
                username,
                is_admin=True,
                password=password,
                ssh_public_key=ssh_key,
                expiry_time=datetime.now() + timedelta(days=365)))

        return (
            '*' * len(password) if password else None,
            ssh_key,
        )

    class ClusterModel:
        def __init__(self, pool, nodes=None):
            self.id = pool.id
            self.pool = pool
            self.nodes = nodes
            self.master_node_id = util.get_master_node_id_from_pool(pool)
            if pool.state.value is batch_models.PoolState.active:
                self.visible_state = pool.allocation_state.value
            else:
                self.visible_state = pool.state.value
            self.vm_size = pool.vm_size
            self.total_current_nodes = pool.current_dedicated_nodes + \
                pool.current_low_priority_nodes
            self.total_target_nodes = pool.target_dedicated_nodes + \
                pool.target_low_priority_nodes
            self.dedicated_nodes = pool.current_dedicated_nodes
            self.low_pri_nodes = pool.current_low_priority_nodes
            self.target_dedicated_nodes = pool.target_dedicated_nodes
            self.target_low_pri_nodes = pool.target_low_priority_nodes

    def pretty_node_count(self, cluster: ClusterModel) -> str:
        if cluster.pool.allocation_state is batch_models.AllocationState.resizing:
            return '{} -> {}'.format(
                cluster.total_current_nodes,
                cluster.total_target_nodes)
        else:
            return '{}'.format(cluster.total_current_nodes)

    def pretty_dedicated_node_count(self, cluster: ClusterModel)-> str:
        if (cluster.pool.allocation_state is batch_models.AllocationState.resizing
                or cluster.pool.state is batch_models.PoolState.deleting)\
                and cluster.dedicated_nodes != cluster.target_dedicated_nodes:
            return '{} -> {}'.format(
                cluster.dedicated_nodes,
                cluster.target_dedicated_nodes)
        else:
            return '{}'.format(cluster.dedicated_nodes)

    def pretty_low_pri_node_count(self, cluster: ClusterModel)-> str:
        if (cluster.pool.allocation_state is batch_models.AllocationState.resizing
                or cluster.pool.state is batch_models.PoolState.deleting)\
                and cluster.low_pri_nodes != cluster.target_low_pri_nodes:
            return '{} -> {}'.format(
                cluster.low_pri_nodes,
                cluster.target_low_pri_nodes)
        else:
            return '{}'.format(cluster.low_pri_nodes)

    def print_cluster(self, cluster: ClusterModel):
        node_count = self.pretty_node_count(cluster)

        log.info("")
        log.info("Cluster         %s", cluster.id)
        log.info("------------------------------------------")
        log.info("State:          %s", cluster.visible_state)
        log.info("Node Size:      %s", cluster.vm_size)
        log.info("Nodes:          %s", node_count)
        log.info("| Dedicated:    %s", self.pretty_dedicated_node_count(cluster))
        log.info("| Low priority: %s", self.pretty_low_pri_node_count(cluster))
        log.info("")

        print_format = '{:<36}| {:<15} | {:<21}| {:<8}'
        print_format_underline = '{:-<36}|{:-<17}|{:-<22}|{:-<8}'
        log.info(print_format.format("Nodes", "State", "IP:Port", "Master"))
        log.info(print_format_underline.format('', '', '', ''))

        if not cluster.nodes:
            return
        for node in cluster.nodes:
            ip, port = util.get_connection_info(cluster.id, node.id, self.batch_client)
            log.info(print_format.format(node.id, node.state.value, '{}:{}'.format(ip, port),
                                         '*' if node.id == cluster.master_node_id else ''))
        log.info('')

    def get_cluster(self, cluster_id: str):
        """
            Print the information for the given cluster
            :param cluster_id: Id of the cluster
        """

        pool = self.batch_client.pool.get(cluster_id)
        if pool.state is batch_models.PoolState.deleting:
            return self.ClusterModel(pool)

        nodes = self.batch_client.compute_node.list(pool_id=cluster_id)
        return self.ClusterModel(pool, nodes)

    def is_pool_running_spark(self, pool: batch_models.CloudPool):
        if pool.metadata is None:
            return False

        for metadata in pool.metadata:
            if metadata.name == constants.AZTK_SOFTWARE_METADATA_KEY:
                return metadata.value == Software.spark

        return False

    def list_clusters(self):
        """
            List all the cluster on your account.
        """

        pools = self.batch_client.pool.list()

        return [self.ClusterModel(pool) for pool in pools if self.is_pool_running_spark(pool)]

    def print_clusters(self, clusters: List[ClusterModel]):
        print_format = '{:<34}| {:<10}| {:<20}| {:<7}'
        print_format_underline = '{:-<34}|{:-<11}|{:-<21}|{:-<7}'

        log.info(print_format.format('Cluster', 'State', 'VM Size', 'Nodes'))
        log.info(print_format_underline.format('', '', '', ''))
        for cluster in clusters:
            node_count = self.pretty_node_count(cluster)

            log.info(print_format.format(cluster.id,
                                         cluster.visible_state,
                                         cluster.vm_size,
                                         node_count))

    def delete_cluster(self, cluster_id: str) -> bool:
        """
            Delete a spark cluster
            :param cluster_id: Id of the cluster to delete
        """
        # delete pool by id
        pool_id = cluster_id

        # job id is equal to pool id
        job_id = pool_id
        job_exists = True

        try:
            self.batch_client.job.get(job_id)
        except:
            job_exists = False

        pool_exists = self.batch_client.pool.exists(pool_id)

        if job_exists:
            self.batch_client.job.delete(job_id)

        if pool_exists:
            self.batch_client.pool.delete(pool_id)

        return job_exists or pool_exists

    def ssh_in_master(
            self,
            cluster_id: str,
            username: str=None,
            webui: str=None,
            jobui: str=None,
            jupyter: str=None,
            ports=None,
            host: bool=False,
            connect: bool=True):
        """
            SSH into head node of spark-app
            :param cluster_id: Id of the cluster to ssh in
            :param username: Username to use to ssh
            :param webui: Port for the spark master web ui (Local port)
            :param jobui: Port for the job web ui (Local port)
            :param jupyter: Port for jupyter(Local port)
            :param ports: an list of local and remote ports
            :type ports: [[<local-port>, <remote-port>]]
        """

        # Get master node id from task (job and task are both named pool_id)
        master_node_id = util.get_master_node_id(cluster_id, self.batch_client)

        if master_node_id is None:
            raise ClusterNotReadyError("Master node has not yet been picked!")

        # get remote login settings for the user
        remote_login_settings = self.batch_client.compute_node.get_remote_login_settings(
            cluster_id, master_node_id)

        master_node_ip = remote_login_settings.remote_login_ip_address
        master_node_port = remote_login_settings.remote_login_port

        pool = self.batch_client.pool.get(cluster_id)

        spark_master_ui_port = constants.DOCKER_SPARK_MASTER_UI_PORT
        spark_worker_ui_port = constants.DOCKER_SPARK_WORKER_UI_PORT
        spark_jupyter_port = constants.DOCKER_SPARK_JUPYTER_PORT
        spark_web_ui_port = constants.DOCKER_SPARK_WEB_UI_PORT

        ssh_command = CommandBuilder('ssh')

        # get ssh private key path if specified
        ssh_priv_key = self.secrets_config.ssh_priv_key
        if ssh_priv_key is not None:
            ssh_command.add_option("-i", ssh_priv_key)
        
        ssh_command.add_argument("-t")
        ssh_command.add_option("-L", "{0}:localhost:{1}".format(
            webui,  spark_master_ui_port), enable=bool(webui))
        ssh_command.add_option("-L", "{0}:localhost:{1}".format(
            jobui, spark_web_ui_port), enable=bool(jobui))
        ssh_command.add_option("-L", "{0}:localhost:{1}".format(
            jupyter, spark_jupyter_port), enable=bool(jupyter))

        if ports is not None:
            for port in ports:
                ssh_command.add_option(
                    "-L", "{0}:localhost:{1}".format(port[0], port[1]))

        user = username if username is not None else '<username>'
        ssh_command.add_argument(
            "{0}@{1} -p {2}".format(user, master_node_ip, master_node_port))
        
        if host is False:
            ssh_command.add_argument("\'sudo docker exec -it spark /bin/bash\'")

        command = ssh_command.to_str()

        if connect:
            call(command, shell=True)
        return '\n\t{}\n'.format(command)
