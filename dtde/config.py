import os
import yaml
import typing
from shutil import copyfile, rmtree
from dtde import log
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
        print(e)
    try:
        copyfile(
                os.path.join(constants.DEFAULT_SPARK_CONF_SOURCE, 'spark-env.sh'),
                os.path.join(constants.DEFAULT_SPARK_CONF_DEST, 'spark-env.sh'))
        log.info("Loaded spark-env.sh")
    except Exception as e:
        print(e)


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
            raise Exception(
                "Secrets configuration file doesn't exists at {0}".format(path))

        with open(path, 'r') as stream:
            try:
                secrets_config = yaml.load(stream)
                self.batch_account_name = secrets_config['batch']['batchaccountname']
                self.batch_account_key = secrets_config['batch']['batchaccountkey']
                self.batch_service_url = secrets_config['batch']['batchserviceurl']

                self.storage_account_name = secrets_config['storage']['storageaccountname']
                self.storage_account_key = secrets_config['storage']['storageaccountkey']
                self.storage_account_suffix = secrets_config['storage']['storageaccountsuffix']

                self.ssh_pub_key = secrets_config['default']['ssh_pub_key']
            except yaml.YAMLError as err:
                print(err)


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
            raise Exception(
                    "Configuration file doesn't exist at {0}".format(path))

        with open(path, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise Exception(
                    "Error in cluster.yaml: {0}".format(err))
            
            if config is None:
               return
            
            self._merge_dict(config)

    
    def _merge_dict(self, config):
        if 'id' in config and config['id'] is not None:
            self.uid = config['id']  

        if 'vm_size' in config and config['vm_size'] is not None:
            self.vm_size = config['vm_size']

        if 'size' in config and config['size'] is not 0:
            self.size = config['size']

        if 'size_low_pri' in config and config['size_low_pri'] is not 0:
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
            raise Exception(
                    "Please supply an id for the cluster either in the cluster.yaml configuration file or with a parameter (--id)")

        if self.size == 0 and self.size_low_pri == 0:
            raise Exception(
                    "Please supply a size or size_low_pri value either in the cluster.yaml configuration file or with a parameter (--size or --size-low-pri)")

        if self.vm_size is None:
            raise Exception(
                    "Please supply a vm_size in either the cluster.yaml configuration file or with a parameter (--vm-size)")

        if self.username is not None and self.wait is False:
            raise Exception(
                    "User {0} will not be created since wait is not set to true in either the cluster.yaml configuration file or with a parameter (--wait)".format(self.username))
