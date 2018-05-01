import os
import yaml
from aztk_cli import log
import aztk.spark
from aztk.spark.models import (
    SecretsConfiguration,
    ServicePrincipalConfiguration,
    SharedKeyConfiguration,
    DockerConfiguration,
    ClusterConfiguration,
    UserConfiguration,
)
from aztk.models import Toolkit
from aztk.models.plugins.internal import PluginReference

def load_aztk_secrets() -> SecretsConfiguration:
    """
    Loads aztk from .aztk/secrets.yaml files(local and global)
    """
    secrets = SecretsConfiguration()
    # read global ~/secrets.yaml
    global_config = _load_secrets_config(
        os.path.join(aztk.utils.constants.HOME_DIRECTORY_PATH, '.aztk',
                     'secrets.yaml'))
    # read current working directory secrets.yaml
    local_config = _load_secrets_config()

    if not global_config and not local_config:
        raise aztk.error.AztkError("There is no secrets.yaml in either ./.aztk/secrets.yaml or .aztk/secrets.yaml")

    if global_config:  # GLobal config is optional
        _merge_secrets_dict(secrets, global_config)
    if local_config:
        _merge_secrets_dict(secrets, local_config)

    # Validate and raise error if any
    secrets.validate()
    return secrets


def _load_secrets_config(
        path: str = aztk.utils.constants.DEFAULT_SECRETS_PATH):
    """
        Loads the secrets.yaml file in the .aztk directory
    """
    if not os.path.isfile(path):
        return None

    with open(path, 'r', encoding='UTF-8') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as err:
            raise aztk.error.AztkError(
                "Error in secrets.yaml: {0}".format(err))


def _merge_secrets_dict(secrets: SecretsConfiguration, secrets_config):
    service_principal_config = secrets_config.get('service_principal')
    if service_principal_config:
        secrets.service_principal = ServicePrincipalConfiguration(
            tenant_id=service_principal_config.get('tenant_id'),
            client_id=service_principal_config.get('client_id'),
            credential=service_principal_config.get('credential'),
            batch_account_resource_id=service_principal_config.get(
                'batch_account_resource_id'),
            storage_account_resource_id=service_principal_config.get(
                'storage_account_resource_id'),
        )

    shared_key_config = secrets_config.get('shared_key')
    batch = secrets_config.get('batch')
    storage = secrets_config.get('storage')

    if shared_key_config and (batch or storage):
        raise aztk.error.AztkError(
            "Shared keys must be configured either under 'sharedKey:' or under 'batch:' and 'storage:', not both."
        )

    if shared_key_config:
        secrets.shared_key = SharedKeyConfiguration(
            batch_account_name=shared_key_config.get('batch_account_name'),
            batch_account_key=shared_key_config.get('batch_account_key'),
            batch_service_url=shared_key_config.get('batch_service_url'),
            storage_account_name=shared_key_config.get('storage_account_name'),
            storage_account_key=shared_key_config.get('storage_account_key'),
            storage_account_suffix=shared_key_config.get(
                'storage_account_suffix'),
        )
    elif batch or storage:
        secrets.shared_key = SharedKeyConfiguration()
        if batch:
            log.warning(
                "Your secrets.yaml format is deprecated. To use shared key authentication use the shared_key key. See config/secrets.yaml.template"
            )
            secrets.shared_key.batch_account_name = batch.get(
                'batchaccountname')
            secrets.shared_key.batch_account_key = batch.get('batchaccountkey')
            secrets.shared_key.batch_service_url = batch.get('batchserviceurl')

        if storage:
            secrets.shared_key.storage_account_name = storage.get(
                'storageaccountname')
            secrets.shared_key.storage_account_key = storage.get(
                'storageaccountkey')
            secrets.shared_key.storage_account_suffix = storage.get(
                'storageaccountsuffix')

    docker_config = secrets_config.get('docker')
    if docker_config:
        secrets.docker = DockerConfiguration(
            endpoint=docker_config.get('endpoint'),
            username=docker_config.get('username'),
            password=docker_config.get('password'),
        )

    default_config = secrets_config.get('default')
    # Check for ssh keys if they are provided
    if default_config:
        secrets.ssh_priv_key = default_config.get('ssh_priv_key')
        secrets.ssh_pub_key = default_config.get('ssh_pub_key')


def read_cluster_config(
        path: str = aztk.utils.constants.DEFAULT_CLUSTER_CONFIG_PATH
) -> ClusterConfiguration:
    """
        Reads the config file in the .aztk/ directory (.aztk/cluster.yaml)
    """
    if not os.path.isfile(path):
        return None

    with open(path, 'r', encoding='UTF-8') as stream:
        try:
            config_dict = yaml.load(stream)
        except yaml.YAMLError as err:
            raise aztk.error.AztkError(
                "Error in cluster.yaml: {0}".format(err))

        if config_dict is None:
            return None

        return cluster_config_from_dict(config_dict)


def cluster_config_from_dict(config: dict):
    output = ClusterConfiguration()
    wait = False
    if config.get('id') is not None:
        output.cluster_id = config['id']

    if config.get('vm_size') is not None:
        output.vm_size = config['vm_size']

    if config.get('size'):
        output.vm_count = config['size']

    if config.get('size_low_pri'):
        output.vm_low_pri_count = config['size_low_pri']

    if config.get('subnet_id') is not None:
        output.subnet_id = config['subnet_id']

    if config.get('username') is not None:
        output.user_configuration = UserConfiguration(
            username=config['username'])

        if config.get('password') is not None:
            output.user_configuration.password = config['password']

    if config.get('custom_scripts') not in [[None], None]:
        output.custom_scripts = []
        for custom_script in config['custom_scripts']:
            output.custom_scripts.append(
                aztk.spark.models.CustomScript(
                    script=custom_script['script'],
                    run_on=custom_script['runOn']))

    if config.get('azure_files') not in [[None], None]:
        output.file_shares = []
        for file_share in config['azure_files']:
            output.file_shares.append(
                aztk.spark.models.FileShare(
                    storage_account_name=file_share['storage_account_name'],
                    storage_account_key=file_share['storage_account_key'],
                    file_share_path=file_share['file_share_path'],
                    mount_path=file_share['mount_path'],
                ))

    if config.get('toolkit') is not None:
        output.toolkit = Toolkit.from_dict(config['toolkit'])

    if config.get('plugins') not in [[None], None]:
        output.plugins = []
        for plugin in config['plugins']:
            ref = PluginReference.from_dict(plugin)
            output.plugins.append(ref.get_plugin())

    if config.get('worker_on_master') is not None:
        output.worker_on_master = config['worker_on_master']

    if config.get('wait') is not None:
        wait = config['wait']

    return output, wait


class SshConfig:
    def __init__(self):
        self.username = None
        self.cluster_id = None
        self.host = False
        self.connect = True
        self.internal = False

        # Set up ports with default values
        self.job_ui_port = '4040'
        self.job_history_ui_port = '18080'
        self.web_ui_port = '8080'

    def _read_config_file(
            self, path: str = aztk.utils.constants.DEFAULT_SSH_CONFIG_PATH):
        """
            Reads the config file in the .aztk/ directory (.aztk/ssh.yaml)
        """
        if not os.path.isfile(path):
            return

        with open(path, 'r', encoding='UTF-8') as stream:
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

        if config.get('host') is not None:
            self.host = config['host']

        if config.get('connect') is not None:
            self.connect = config['connect']

        if config.get('internal') is not None:
            self.internal = config['internal']

    def merge(self, cluster_id, username, job_ui_port, job_history_ui_port,
              web_ui_port, host, connect, internal):
        """
            Merges fields with args object
        """
        self._read_config_file(
            os.path.join(aztk.utils.constants.HOME_DIRECTORY_PATH, '.aztk',
                         'ssh.yaml'))
        self._read_config_file()
        self._merge_dict(
            dict(
                cluster_id=cluster_id,
                username=username,
                job_ui_port=job_ui_port,
                job_history_ui_port=job_history_ui_port,
                web_ui_port=web_ui_port,
                host=host,
                connect=connect,
                internal=internal))

        if self.cluster_id is None:
            raise aztk.error.AztkError(
                "Please supply an id for the cluster either in the ssh.yaml configuration file or with a parameter (--id)"
            )

        if self.username is None:
            raise aztk.error.AztkError(
                "Please supply a username either in the ssh.yaml configuration file or with a parameter (--username)"
            )


class JobConfig():
    def __init__(self):
        self.id = None
        self.applications = []
        self.custom_scripts = None
        self.spark_configuration = None
        self.vm_size = None
        self.toolkit = None
        self.max_dedicated_nodes = 0
        self.max_low_pri_nodes = 0
        self.spark_defaults_conf = None
        self.spark_env_sh = None
        self.core_site_xml = None
        self.subnet_id = None
        self.worker_on_master = None

    def _merge_dict(self, config):
        config = config.get('job')

        if config.get('id') is not None:
            self.id = config['id']

        cluster_configuration = config.get('cluster_configuration')
        if cluster_configuration:
            self.vm_size = cluster_configuration.get('vm_size')
            self.toolkit = Toolkit.from_dict(cluster_configuration.get('toolkit'))
            if cluster_configuration.get('size') is not None:
                self.max_dedicated_nodes = cluster_configuration.get('size')
            if cluster_configuration.get('size_low_pri') is not None:
                self.max_low_pri_nodes = cluster_configuration.get('size_low_pri')
            self.custom_scripts = cluster_configuration.get('custom_scripts')
            self.subnet_id = cluster_configuration.get('subnet_id')
            self.worker_on_master = cluster_configuration.get("worker_on_master")

        applications = config.get('applications')
        if applications:
            self.applications = []
            for application in applications:
                self.applications.append(
                    aztk.spark.models.ApplicationConfiguration(
                        name=application.get('name'),
                        application=application.get('application'),
                        application_args=application.get('application_args'),
                        main_class=application.get('main_class'),
                        jars=application.get('jars'),
                        py_files=application.get('py_files'),
                        files=application.get('files'),
                        driver_java_options=application.get('driver_java_options'),
                        driver_library_path=application.get('driver_library_path'),
                        driver_class_path=application.get('driver_class_path'),
                        driver_memory=application.get('driver_memory'),
                        executor_memory=application.get('executor_memory'),
                        driver_cores=application.get('driver_cores'),
                        executor_cores=application.get('executor_cores')
                    )
                )

        spark_configuration = config.get('spark_configuration')
        if spark_configuration:
            self.spark_defaults_conf = self.__convert_to_path(spark_configuration.get('spark_defaults_conf'))
            self.spark_env_sh = self.__convert_to_path(spark_configuration.get('spark_env_sh'))
            self.core_site_xml = self.__convert_to_path(spark_configuration.get('core_site_xml'))
            self.jars = [self.__convert_to_path(jar) for jar in spark_configuration.get('jars') or []]

    def __convert_to_path(self, str_path):
        if str_path:
            abs_path = os.path.abspath(os.path.expanduser(str_path))
            if not os.path.exists(abs_path):
                raise aztk.error.AztkError(
                    "Could not find file: {0}\nCheck your configuration file".
                    format(str_path))
            return abs_path

    def _read_config_file(
            self, path: str = aztk.utils.constants.DEFAULT_SPARK_JOB_CONFIG):
        """
            Reads the Job config file in the .aztk/ directory (.aztk/job.yaml)
        """
        if not path or not os.path.isfile(path):
            return

        with open(path, 'r', encoding='UTF-8') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise aztk.error.AztkError(
                    "Error in job.yaml: {0}".format(err))

            if config is None:
                return

            self._merge_dict(config)

    def merge(self, id, job_config_yaml=None):
        self._read_config_file(aztk.utils.constants.GLOBAL_SPARK_JOB_CONFIG)
        self._read_config_file(aztk.utils.constants.DEFAULT_SPARK_JOB_CONFIG)
        self._read_config_file(job_config_yaml)
        if id:
            self.id = id

        for entry in self.applications:
            if entry.name is None:
                raise aztk.error.AztkError(
                    "Application specified with no name. Please verify your configuration in job.yaml")
            if entry.application is None:
                raise aztk.error.AztkError(
                    "No path to application specified for {} in job.yaml".format(entry.name))


def get_file_if_exists(file):
    local_conf_file = os.path.join(
        aztk.utils.constants.DEFAULT_SPARK_CONF_SOURCE, file)
    global_conf_file = os.path.join(aztk.utils.constants.GLOBAL_CONFIG_PATH,
                                    file)

    if os.path.exists(local_conf_file):
        return local_conf_file
    if os.path.exists(global_conf_file):
        return global_conf_file

    return None


def load_aztk_spark_config():
    return aztk.spark.models.SparkConfiguration(
        spark_defaults_conf=get_file_if_exists('spark-defaults.conf'),
        jars=load_jars(),
        spark_env_sh=get_file_if_exists('spark-env.sh'),
        core_site_xml=get_file_if_exists('core-site.xml'))


def load_jars():
    jars = None

    # try load global
    try:
        jars_src = os.path.join(aztk.utils.constants.GLOBAL_CONFIG_PATH,
                                'jars')
        jars = [os.path.join(jars_src, jar) for jar in os.listdir(jars_src)]
    except FileNotFoundError:
        pass

    # try load local, overwrite if found
    try:
        jars_src = os.path.join(aztk.utils.constants.DEFAULT_SPARK_CONF_SOURCE,
                                'jars')
        jars = [os.path.join(jars_src, jar) for jar in os.listdir(jars_src)]
    except FileNotFoundError:
        pass

    return jars
