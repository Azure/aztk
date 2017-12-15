import os
import yaml
import typing
from cli import log
import aztk.spark


class SecretsConfig:

    def __init__(self):
        self.batch_account_name = None
        self.batch_account_key = None
        self.batch_service_url = None

        self.storage_account_name = None
        self.storage_account_key = None
        self.storage_account_suffix = None

        self.docker_endpoint = None
        self.docker_username = None
        self.docker_password = None
        self.ssh_pub_key = None
        self.ssh_priv_key = None

    def _load_secrets_config(self, path: str=aztk.utils.constants.DEFAULT_SECRETS_PATH):
        """
            Loads the secrets.yaml file in the .aztk directory
        """
        if not os.path.isfile(path):
            return

        with open(path, 'r') as stream:
            try:
                secrets_config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise aztk.error.AztkError(
                    "Error in cluster.yaml: {0}".format(err))

            self._merge_dict(secrets_config)

    def _merge_dict(self, secrets_config):
        # Ensure all necessary fields are provided
        batch = secrets_config.get('batch')
        if batch:
            self.batch_account_name = batch.get('batchaccountname')
            self.batch_account_key = batch.get('batchaccountkey')
            self.batch_service_url = batch.get('batchserviceurl')

        storage = secrets_config.get('storage')
        if storage:
            self.storage_account_name = storage.get('storageaccountname')
            self.storage_account_key = storage.get('storageaccountkey')
            self.storage_account_suffix = storage.get('storageaccountsuffix')

        docker_config = secrets_config.get('docker')
        if docker_config:
            self.docker_endpoint = docker_config.get('endpoint')
            self.docker_username = docker_config.get('username')
            self.docker_password = docker_config.get('password')

        default_config = secrets_config.get('default')
        # Check for ssh keys if they are provided
        if default_config:
            self.ssh_priv_key = default_config.get('ssh_priv_key')
            self.ssh_pub_key = default_config.get('ssh_pub_key')

    def load(self):
        # read global ~/secrets.yaml
        self._load_secrets_config(os.path.join(aztk.utils.constants.HOME_DIRECTORY_PATH, '.aztk', 'secrets.yaml'))
        # read current working directory secrets.yaml
        self._load_secrets_config()


class ClusterConfig:

    def __init__(self):
        self.uid = None
        self.vm_size = None
        self.size = 0
        self.size_low_pri = 0
        self.username = None
        self.password = None
        self.custom_scripts = None
        self.file_shares = None
        self.docker_repo = None
        self.wait = None

    def _read_config_file(self, path: str = aztk.utils.constants.DEFAULT_CLUSTER_CONFIG_PATH):
        """
            Reads the config file in the .aztk/ directory (.aztk/cluster.yaml)
        """
        if not os.path.isfile(path):
            return

        with open(path, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise aztk.error.AztkError(
                    "Error in cluster.yaml: {0}".format(err))

            if config is None:
                return

            self._merge_dict(config)

    def _merge_dict(self, config):
        if config.get('id') is not None:
            self.uid = config['id']

        if config.get('vm_size') is not None:
            self.vm_size = config['vm_size']

        if config.get('size') is not None:
            self.size = config['size']
            self.size_low_pri = 0

        if config.get('size_low_pri') is not None:
            self.size_low_pri = config['size_low_pri']
            self.size = 0

        if config.get('username') is not None:
            self.username = config['username']

        if config.get('password') is not None:
            self.password = config['password']

        if config.get('custom_scripts') not in [[None], None]:
            self.custom_scripts = config['custom_scripts']

        if config.get('azure_files') not in [[None], None]:
            self.file_shares = config['azure_files']

        if config.get('docker_repo') is not None:
            self.docker_repo = config['docker_repo']

        if config.get('wait') is not None:
            self.wait = config['wait']

    def merge(self, uid, username, size, size_low_pri, vm_size, password, wait, docker_repo):
        """
            Reads configuration file (cluster.yaml), merges with command line parameters,
            checks for errors with configuration
        """
        self._read_config_file(os.path.join(aztk.utils.constants.HOME_DIRECTORY_PATH, '.aztk', 'cluster.yaml'))
        self._read_config_file()

        self._merge_dict(
            dict(
                id=uid,
                username=username,
                size=size,
                size_low_pri=size_low_pri,
                vm_size=vm_size,
                password=password,
                wait=wait,
                custom_scripts=None,
                docker_repo=docker_repo
            )
        )

        if self.uid is None:
            raise aztk.error.AztkError(
                "Please supply an id for the cluster with a parameter (--id)")

        if self.size == 0 and self.size_low_pri == 0:
            raise aztk.error.AztkError(
                "Please supply a valid (greater than 0) size or size_low_pri value either in the cluster.yaml configuration file or with a parameter (--size or --size-low-pri)")

        if self.vm_size is None:
            raise aztk.error.AztkError(
                "Please supply a vm_size in either the cluster.yaml configuration file or with a parameter (--vm-size)")

        if self.wait is None:
            raise aztk.error.AztkError(
                "Please supply a value for wait in either the cluster.yaml configuration file or with a parameter (--wait or --no-wait)")

        if self.username is not None and self.wait is False:
            raise aztk.error.AztkError(
                "You cannot create a user '{0}' if wait is set to false. By default, we create a user in the cluster.yaml file. Please either the configure your cluster.yaml file or set the parameter (--wait)".format(self.username))


class SshConfig:

    def __init__(self):
        self.username = None
        self.cluster_id = None
        self.host = False
        self.connect = True

        # Set up ports with default values
        self.job_ui_port = '4040'
        self.job_history_ui_port = '18080'
        self.web_ui_port = '8080'
        self.jupyter_port = '8888'
        self.name_node_ui_port = '50070'
        self.rstudio_server_port = '8787'

    def _read_config_file(self, path: str = aztk.utils.constants.DEFAULT_SSH_CONFIG_PATH):
        """
            Reads the config file in the .aztk/ directory (.aztk/cluster.yaml)
        """
        if not os.path.isfile(path):
            return

        with open(path, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise aztk.error.AztkError(
                    "Error in ssh.yaml: {0}".format(err))

            if config is None:
                return

            self._merge_dict(config)

    def _merge_dict(self, config):
        if config.get('username') is not None:
            self.username = config['username']

        if config.get('cluster_id') is not None:
            self.cluster_id = config['cluster_id']

        if config.get('job_ui_port') is not None:
            self.job_ui_port = config['job_ui_port']

        if config.get('job_history_ui_port') is not None:
            self.job_history_ui_port = config['job_history_ui_port']

        if config.get('web_ui_port') is not None:
            self.web_ui_port = config['web_ui_port']

        if config.get('jupyter_port') is not None:
            self.jupyter_port = config['jupyter_port']

        if config.get('name_node_ui_port') is not None:
            self.name_node_ui_port = config['name_node_ui_port']

        if config.get('rstudio_server_port') is not None:
            self.rstudio_server_port = config['rstudio_server_port']

        if config.get('host') is not None:
            self.host = config['host']

        if config.get('connect') is not None:
            self.connect = config['connect']

    def merge(self, cluster_id, username, job_ui_port, job_history_ui_port, web_ui_port, jupyter_port, name_node_ui_port, rstudio_server_port, host, connect):
        """
            Merges fields with args object
        """
        self._read_config_file()
        self._read_config_file(os.path.join(aztk.utils.constants.HOME_DIRECTORY_PATH, '.aztk', 'ssh.yaml'))
        self._merge_dict(
            dict(
                cluster_id=cluster_id,
                username=username,
                job_ui_port=job_ui_port,
                job_history_ui_port=job_history_ui_port,
                web_ui_port=web_ui_port,
                jupyter_port=jupyter_port,
                name_node_ui_port=name_node_ui_port,
                rstudio_server_port=rstudio_server_port,
                host=host,
                connect=connect
            )
        )

        if self.cluster_id is None:
            raise aztk.error.AztkError(
                "Please supply an id for the cluster either in the ssh.yaml configuration file or with a parameter (--id)")

        if self.username is None:
            raise aztk.error.AztkError(
                "Please supply a username either in the ssh.yaml configuration file or with a parameter (--username)")


def load_aztk_spark_config():
    def get_file_if_exists(file, local: bool):
        if local:
            if os.path.exists(os.path.join(aztk.utils.constants.DEFAULT_SPARK_CONF_SOURCE, file)):
                return os.path.join(aztk.utils.constants.DEFAULT_SPARK_CONF_SOURCE, file)
        else:
            if os.path.exists(os.path.join(aztk.utils.constants.GLOBAL_CONFIG_PATH, file)):
                return os.path.join(aztk.utils.constants.GLOBAL_CONFIG_PATH, file)

    jars = spark_defaults_conf = spark_env_sh = core_site_xml = None

    # try load global
    try:
        jars_src = os.path.join(aztk.utils.constants.GLOBAL_CONFIG_PATH, 'jars')
        jars = [os.path.join(jars_src, jar) for jar in os.listdir(jars_src)]
    except FileNotFoundError:
        pass

    spark_defaults_conf = get_file_if_exists('spark-defaults.conf', False)
    spark_env_sh = get_file_if_exists('spark-env.sh', False)
    core_site_xml = get_file_if_exists('core-site.xml', False)

    # try load local, overwrite if found
    try:
        jars_src = os.path.join(aztk.utils.constants.DEFAULT_SPARK_CONF_SOURCE, 'jars')
        jars = [os.path.join(jars_src, jar) for jar in os.listdir(jars_src)]
    except FileNotFoundError:
        pass

    spark_defaults_conf = get_file_if_exists('spark-defaults.conf', True)
    spark_env_sh = get_file_if_exists('spark-env.sh', True)
    core_site_xml = get_file_if_exists('core-site.xml', True)

    return aztk.spark.models.SparkConfiguration(
        spark_defaults_conf=spark_defaults_conf,
        jars=jars,
        spark_env_sh=spark_env_sh,
        core_site_xml=core_site_xml)
