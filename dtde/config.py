import os
import yaml
import typing
from shutil import copyfile, rmtree
from dtde import log
from dtde import error
from . import constants

def load_spark_config():
    """
        Copies the spark-defautls.conf and spark-env.sh in the .thunderbolt/ diretory
    """
    if not os.path.exists(constants.DEFAULT_SPARK_CONF_DEST):
        os.mkdir(constants.DEFAULT_SPARK_CONF_DEST)

    try:
        copyfile(
                os.path.join(constants.DEFAULT_SPARK_CONF_SOURCE, 'spark-defaults.conf'),
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

        self.ssh_pub_key = None


    def load_secrets_config(self, path: str=constants.DEFAULT_SECRETS_PATH):
        """
            Loads the secrets.yaml file in the .thunderbolt directory
        """
        if not os.path.isfile(path):
            raise error.ThunderboltError(
                "Secrets configuration file doesn't exists at {0}".format(path))

        with open(path, 'r') as stream:
            try:
                secrets_config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise error.ThunderboltError(
                    "Error in cluster.yaml: {0}".format(err))
            
            self._merge_dict(secrets_config)


    def _merge_dict(self, secrets_config):
        self.batch_account_name = secrets_config['batch']['batchaccountname']
        self.batch_account_key = secrets_config['batch']['batchaccountkey']
        self.batch_service_url = secrets_config['batch']['batchserviceurl']

        self.storage_account_name = secrets_config['storage']['storageaccountname']
        self.storage_account_key = secrets_config['storage']['storageaccountkey']
        self.storage_account_suffix = secrets_config['storage']['storageaccountsuffix']

        try:
            self.ssh_pub_key = secrets_config['default']['ssh_pub_key']
        except (KeyError, TypeError) as e:
            pass


class ClusterConfig:

    def __init__(self):
        self.uid = None
        self.vm_size = None
        self.size = 0
        self.size_low_pri = 0
        self.username = None
        self.password = None
        self.ssh_key = None
        self.custom_script = None
        self.docker_repo = None
        self.wait = False


    def _read_config_file(self, path: str=constants.DEFAULT_CLUSTER_CONFIG_PATH):
        """
            Reads the config file in the .thunderbolt/ directory (.thunderbolt/cluster.yaml)
        """
        if not os.path.isfile(path):
            raise error.ThunderboltError(
                    "Configuration file doesn't exist at {0}".format(path))

        with open(path, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise error.ThunderboltError(
                    "Error in cluster.yaml: {0}".format(err))
            
            if config is None:
               return
            
            self._merge_dict(config)

    
    def _merge_dict(self, config):
        if 'id' in config and config['id'] is not None:
            self.uid = config['id']  

        if 'vm_size' in config and config['vm_size'] is not None:
            self.vm_size = config['vm_size']

        if 'size' in config and config['size'] is not None:
            self.size = config['size']

        if 'size_low_pri' in config and config['size_low_pri'] is not None:
            self.size_low_pri = config['size_low_pri']

        if 'username' in config and config['username'] is not None:
            self.username = config['username']

        if 'password' in config and config['password'] is not None:
            self.password = config['password']

        if 'custom_script' in config and config['custom_script'] is not None:
            self.custom_script = config['custom_script']

        if 'docker_repo' in config and config['docker_repo'] is not None:
            self.docker_repo = config['docker_repo']

        if 'wait' in config and config['wait'] is not False:
            self.wait = config['wait']


    def merge(self, uid, username, size, size_low_pri, vm_size, ssh_key, password, wait, custom_script, docker_repo):
        """
            Reads configuration file (cluster.yaml), merges with command line parameters,
            checks for errors with configuration
        """
        self._read_config_file()

        self._merge_dict(
            dict(
                id = uid,
                username = username,
                size = size,
                size_low_pri = size_low_pri,
                vm_size = vm_size,
                ssh_key = ssh_key,
                password = password,
                wait = wait,
                custom_script = custom_script, 
                docker_repo = docker_repo
            )
        )

        if self.uid is None:
            raise error.ThunderboltError(
                    "Please supply an id for the cluster with a parameter (--id)")

        if self.size == 0 and self.size_low_pri == 0:
            raise error.ThunderboltError(
                    "Please supply a valid (greater than 0) size or size_low_pri value either in the cluster.yaml configuration file or with a parameter (--size or --size-low-pri)")

        if self.vm_size is None:
            raise error.ThunderboltError(
                    "Please supply a vm_size in either the cluster.yaml configuration file or with a parameter (--vm-size)")
            
        if self.username is not None and self.wait is False:
            raise error.ThunderboltError(
                    "User {0} will not be created since wait is not set to true in either the cluster.yaml configuration file or with a parameter (--wait)".format(self.username))


class SshConfig:

    def __init__(self):
        self.username = None
        self.cluster_id = None
        self.job_ui_port = None
        self.web_ui_port = None
        self.jupyter_port = None
        self.connect = True


    def _read_config_file(self, path: str=constants.DEFAULT_SSH_CONFIG_PATH):
        """
            Reads the config file in the .thunderbolt/ directory (.thunderbolt/cluster.yaml)
        """
        if not os.path.isfile(path):
            raise Exception(
                    "SSH Configuration file doesn't exist at {0}".format(path))

        with open(path, 'r') as stream:
            try:
               config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise Exception(
                    "Error in ssh.yaml: {0}".format(err))

            if config is None:
               return

            self._merge_dict(config)

    
    def _merge_dict(self, config):
        if 'username' in config and config['username'] is not None:
            self.username = config['username']

        if 'cluster_id' in config and config['cluster_id'] is not None:
            self.cluster_id = config['cluster_id']

        if 'job_ui_port' in config and config['job_ui_port'] is not None:
            self.job_ui_port = config['job_ui_port']

        if 'web_ui_port' in config and config['web_ui_port'] is not None:
            self.web_ui_port = config['web_ui_port']
        
        if 'jupyter_port' in config and config['jupyter_port'] is not None:
            self.jupyter_port = config['jupyter_port']

        if 'connect' in config and config['connect'] is False:
            self.connect = False        


    def merge(self, cluster_id, username, job_ui_port, web_ui_port, jupyter_port, connect):
        """
            Merges fields with args object
        """
        self._read_config_file()
        self._merge_dict(
            dict(
                cluster_id = cluster_id,
                username = username,
                job_ui_port = job_ui_port,
                web_ui_port = web_ui_port,
                jupyter_port = jupyter_port,
                connect = connect
            )
        )

        if self.cluster_id is None:
            raise Exception(
                "Please supply an id for the cluster either in the ssh.yaml configuration file or with a parameter (--id)")
        
        if self.username is None:
            raise Exception(
                "Please supply a username either in the ssh.yaml configuration file or with a parameter (--username)")
