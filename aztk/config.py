import os
import yaml
import typing
from shutil import copyfile, rmtree
from aztk import log
from aztk import error
from . import constants


def load_spark_config():
    """
        Copies the spark-defautls.conf and spark-env.sh in the .aztk/ diretory
    """
    if not os.path.exists(constants.DEFAULT_SPARK_CONF_DEST):
        os.mkdir(constants.DEFAULT_SPARK_CONF_DEST)

    try:
        copyfile(
            os.path.join(constants.DEFAULT_SPARK_CONF_SOURCE,
                         'spark-defaults.conf'),
            os.path.join(constants.DEFAULT_SPARK_CONF_DEST, 'spark-defaults.conf'))
        log.info("Loaded spark-defaults.conf")
    except Exception as e:
        pass

    try:
        copyfile(
            os.path.join(constants.DEFAULT_SPARK_CONF_SOURCE, 'spark-env.sh'),
            os.path.join(constants.DEFAULT_SPARK_CONF_DEST, 'spark-env.sh'))
        log.info("Loaded spark-env.sh")
    except Exception as e:
        pass


def cleanup_spark_config():
    """
        Removes copied remaining spark config files after they have been uploaded
    """
    if os.path.exists(constants.DEFAULT_SPARK_CONF_DEST):
        rmtree(constants.DEFAULT_SPARK_CONF_DEST)


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

    def load_secrets_config(self, path: str=constants.DEFAULT_SECRETS_PATH):
        """
            Loads the secrets.yaml file in the .aztk directory
        """
        if not os.path.isfile(path):
            raise error.AztkError(
                "Secrets configuration file doesn't exists at {0}".format(path))

        with open(path, 'r') as stream:
            try:
                secrets_config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise error.AztkError(
                    "Error in cluster.yaml: {0}".format(err))

            self._merge_dict(secrets_config)

    def _merge_dict(self, secrets_config):
        # Ensure all necessary fields are provided
        try:
            self.batch_account_name = secrets_config['batch']['batchaccountname']
        except KeyError:
            raise error.AztkError(
                "Please specify a batch account name in your .aztk/secrets.yaml file")
        try:
            self.batch_account_key = secrets_config['batch']['batchaccountkey']
        except KeyError:
            raise error.AztkError(
                "Please specify a batch account key in your .aztk/secrets.yaml file")
        try:
            self.batch_service_url = secrets_config['batch']['batchserviceurl']
        except KeyError:
            raise error.AztkError(
                "Please specify a batch service url in your .aztk/secrets.yaml file")

        try:
            self.storage_account_name = secrets_config['storage']['storageaccountname']
        except KeyError:
            raise error.AztkError(
                "Please specify a storage account name in your .aztk/secrets.yaml file")
        try:
            self.storage_account_key = secrets_config['storage']['storageaccountkey']
        except KeyError:
            raise error.AztkError(
                "Please specify a storage account key in your .aztk/secrets.yaml file")
        try:
            self.storage_account_suffix = secrets_config['storage']['storageaccountsuffix']
        except KeyError:
            raise error.AztkError(
                "Please specify a storage account suffix in your .aztk/secrets.yaml file")

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


class ClusterConfig:

    def __init__(self):
        self.uid = None
        self.vm_size = None
        self.size = 0
        self.size_low_pri = 0
        self.username = None
        self.password = None
        self.ssh_key = None
        self.custom_scripts = None
        self.docker_repo = None
        self.wait = None

    def _read_config_file(self, path: str=constants.DEFAULT_CLUSTER_CONFIG_PATH):
        """
            Reads the config file in the .aztk/ directory (.aztk/cluster.yaml)
        """
        if not os.path.isfile(path):
            raise error.AztkError(
                "Configuration file doesn't exist at {0}".format(path))

        with open(path, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise error.AztkError(
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

        if config.get('docker_repo') is not None:
            self.docker_repo = config['docker_repo']

        if config.get('wait') is not None:
            self.wait = config['wait']

    def merge(self, uid, username, size, size_low_pri, vm_size, ssh_key, password, wait, docker_repo):
        """
            Reads configuration file (cluster.yaml), merges with command line parameters,
            checks for errors with configuration
        """
        self._read_config_file()

        self._merge_dict(
            dict(
                id=uid,
                username=username,
                size=size,
                size_low_pri=size_low_pri,
                vm_size=vm_size,
                ssh_key=ssh_key,
                password=password,
                wait=wait,
                custom_scripts=None,
                docker_repo=docker_repo
            )
        )

        if self.uid is None:
            raise error.AztkError(
                "Please supply an id for the cluster with a parameter (--id)")

        if self.size == 0 and self.size_low_pri == 0:
            raise error.AztkError(
                "Please supply a valid (greater than 0) size or size_low_pri value either in the cluster.yaml configuration file or with a parameter (--size or --size-low-pri)")

        if self.vm_size is None:
            raise error.AztkError(
                "Please supply a vm_size in either the cluster.yaml configuration file or with a parameter (--vm-size)")

        if self.wait is None:
            raise error.AztkError(
                "Please supply a value for wait in either the cluster.yaml configuration file or with a parameter (--wait or --no-wait)")

        if self.username is not None and self.wait is False:
            raise error.AztkError(
                "You cannot create a user '{0}' if wait is set to false. By default, we create a user in the cluster.yaml file. Please either the configure your cluster.yaml file or set the parameter (--wait)".format(self.username))


class SshConfig:

    def __init__(self):
        self.username = None
        self.cluster_id = None
        self.job_ui_port = None
        self.web_ui_port = None
        self.jupyter_port = None
        self.host = False
        self.connect = True

    def _read_config_file(self, path: str=constants.DEFAULT_SSH_CONFIG_PATH):
        """
            Reads the config file in the .aztk/ directory (.aztk/cluster.yaml)
        """
        if not os.path.isfile(path):
            raise error.AztkError(
                "SSH Configuration file doesn't exist at {0}".format(path))

        with open(path, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise error.AztkError(
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

        if config.get('web_ui_port') is not None:
            self.web_ui_port = config['web_ui_port']

        if config.get('jupyter_port') is not None:
            self.jupyter_port = config['jupyter_port']

        if config.get('host') is not None:
            self.host = config['host']

        if config.get('connect') is not None:
            self.connect = config['connect']

    def merge(self, cluster_id, username, job_ui_port, web_ui_port, jupyter_port, host, connect):
        """
            Merges fields with args object
        """
        self._read_config_file()
        self._merge_dict(
            dict(
                cluster_id=cluster_id,
                username=username,
                job_ui_port=job_ui_port,
                web_ui_port=web_ui_port,
                jupyter_port=jupyter_port,
                host=host,
                connect=connect
            )
        )

        if self.cluster_id is None:
            raise error.AztkError(
                "Please supply an id for the cluster either in the ssh.yaml configuration file or with a parameter (--id)")

        if self.username is None:
            raise error.AztkError(
                "Please supply a username either in the ssh.yaml configuration file or with a parameter (--username)")
