import os

import yaml

import aztk.spark
from aztk.models import Toolkit
from aztk.models.plugins.internal import PluginReference
from aztk.spark.models import ClusterConfiguration, SecretsConfiguration

# from aztk.spark.models import SchedulingTarget


def load_aztk_secrets() -> SecretsConfiguration:
    """
    Loads aztk from .aztk/secrets.yaml files(local and global)
    """
    secrets = SecretsConfiguration()
    # read global ~/secrets.yaml
    global_config = _load_config_file(os.path.join(aztk.utils.constants.HOME_DIRECTORY_PATH, ".aztk", "secrets.yaml"))
    # read current working directory secrets.yaml
    local_config = _load_config_file(aztk.utils.constants.DEFAULT_SECRETS_PATH)

    if not global_config and not local_config:
        raise aztk.error.AztkError("There is no secrets.yaml in either ./.aztk/secrets.yaml or .aztk/secrets.yaml")

    if global_config:    # Global config is optional
        _merge_secrets_dict(secrets, global_config)
    if local_config:
        _merge_secrets_dict(secrets, local_config)

    # Validate and raise error if any
    secrets.validate()
    return secrets


def _load_config_file(path: str):
    if not os.path.isfile(path):
        return None

    with open(path, "r", encoding="UTF-8") as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as err:
            raise aztk.error.AztkError("Error in {0}:\n {1}".format(path, err))


def _merge_secrets_dict(secrets: SecretsConfiguration, secrets_config):
    other = SecretsConfiguration.from_dict(secrets_config)
    secrets.merge(other)


def read_cluster_config(path: str = aztk.utils.constants.DEFAULT_CLUSTER_CONFIG_PATH) -> ClusterConfiguration:
    """
        Reads the config file in the .aztk/ directory (.aztk/cluster.yaml)
    """
    config_dict = _load_config_file(path)
    return cluster_config_from_dict(config_dict)


def cluster_config_from_dict(config: dict):
    wait = False
    if config.get("plugins") not in [[None], None]:
        plugins = []
        for plugin in config["plugins"]:
            ref = PluginReference.from_dict(plugin)
            plugins.append(ref.get_plugin())
        config["plugins"] = plugins

    if config.get("username") is not None:
        config["user_configuration"] = dict(username=config.pop("username"))

    if config.get("wait") is not None:
        wait = config.pop("wait")

    return ClusterConfiguration.from_dict(config), wait


class SshConfig:
    def __init__(self):
        self.username = None
        self.cluster_id = None
        self.host = False
        self.connect = True
        self.internal = False

        # Set up ports with default values
        self.job_ui_port = "4040"
        self.job_history_ui_port = "18080"
        self.web_ui_port = "8080"

    def _read_config_file(self, path: str = aztk.utils.constants.DEFAULT_SSH_CONFIG_PATH):
        """
            Reads the config file in the .aztk/ directory (.aztk/ssh.yaml)
        """
        if not os.path.isfile(path):
            return

        with open(path, "r", encoding="UTF-8") as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise aztk.error.AztkError("Error in ssh.yaml: {0}".format(err))

            if config is None:
                return

            self._merge_dict(config)

    def _merge_dict(self, config):
        if config.get("username") is not None:
            self.username = config["username"]

        if config.get("cluster_id") is not None:
            self.cluster_id = config["cluster_id"]

        if config.get("job_ui_port") is not None:
            self.job_ui_port = config["job_ui_port"]

        if config.get("job_history_ui_port") is not None:
            self.job_history_ui_port = config["job_history_ui_port"]

        if config.get("web_ui_port") is not None:
            self.web_ui_port = config["web_ui_port"]

        if config.get("host") is not None:
            self.host = config["host"]

        if config.get("connect") is not None:
            self.connect = config["connect"]

        if config.get("internal") is not None:
            self.internal = config["internal"]

    def merge(self, cluster_id, username, job_ui_port, job_history_ui_port, web_ui_port, host, connect, internal):
        """
            Merges fields with args object
        """
        self._read_config_file(os.path.join(aztk.utils.constants.HOME_DIRECTORY_PATH, ".aztk", "ssh.yaml"))
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
                internal=internal,
            ))

        if self.cluster_id is None:
            raise aztk.error.AztkError("Please supply an id for the cluster either in the ssh.yaml configuration file "
                                       "or with a parameter (--id)")

        if self.username is None:
            raise aztk.error.AztkError(
                "Please supply a username either in the ssh.yaml configuration file or with a parameter (--username)")


def __convert_to_path(path: str):
    if path:
        abs_path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(abs_path):
            raise aztk.error.AztkError("Could not find file: {0}\nCheck your configuration file".format(path))
        return abs_path
    return None


class JobConfig:
    def __init__(self):
        self.id = None
        self.applications = []
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
        # self.scheduling_target = None
        self.jars = []

    def _merge_dict(self, config):
        config = config.get("job")

        if config.get("id") is not None:
            self.id = config["id"]

        cluster_configuration = config.get("cluster_configuration")
        if cluster_configuration:
            self.vm_size = cluster_configuration.get("vm_size")
            self.toolkit = Toolkit.from_dict(cluster_configuration.get("toolkit"))
            if cluster_configuration.get("size") is not None:
                self.max_dedicated_nodes = cluster_configuration.get("size")
            if cluster_configuration.get("size_low_priority") is not None:
                self.max_low_pri_nodes = cluster_configuration.get("size_low_priority")
            self.subnet_id = cluster_configuration.get("subnet_id")
            self.worker_on_master = cluster_configuration.get("worker_on_master")
            # scheduling_target = cluster_configuration.get("scheduling_target")
            # if scheduling_target:
            #     self.scheduling_target = SchedulingTarget(scheduling_target)

        applications = config.get("applications")
        if applications:
            self.applications = []
            for application in applications:
                self.applications.append(
                    aztk.spark.models.ApplicationConfiguration(
                        name=application.get("name"),
                        application=application.get("application"),
                        application_args=application.get("application_args"),
                        main_class=application.get("main_class"),
                        jars=application.get("jars"),
                        py_files=application.get("py_files"),
                        files=application.get("files"),
                        driver_java_options=application.get("driver_java_options"),
                        driver_library_path=application.get("driver_library_path"),
                        driver_class_path=application.get("driver_class_path"),
                        driver_memory=application.get("driver_memory"),
                        executor_memory=application.get("executor_memory"),
                        driver_cores=application.get("driver_cores"),
                        executor_cores=application.get("executor_cores"),
                    ))

        spark_configuration = config.get("spark_configuration")
        if spark_configuration:
            self.spark_defaults_conf = __convert_to_path(spark_configuration.get("spark_defaults_conf"))
            self.spark_env_sh = __convert_to_path(spark_configuration.get("spark_env_sh"))
            self.core_site_xml = __convert_to_path(spark_configuration.get("core_site_xml"))
            self.jars = [__convert_to_path(jar) for jar in spark_configuration.get("jars") or []]

    def _read_config_file(self, path: str = aztk.utils.constants.DEFAULT_SPARK_JOB_CONFIG):
        """
            Reads the Job config file in the .aztk/ directory (.aztk/job.yaml)
        """
        if not path or not os.path.isfile(path):
            return

        with open(path, "r", encoding="UTF-8") as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise aztk.error.AztkError("Error in job.yaml: {0}".format(err))

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
                raise aztk.error.AztkError("No path to application specified for {} in job.yaml".format(entry.name))


def get_file_if_exists(file):
    local_conf_file = os.path.join(aztk.utils.constants.DEFAULT_SPARK_CONF_SOURCE, file)
    global_conf_file = os.path.join(aztk.utils.constants.GLOBAL_CONFIG_PATH, file)

    if os.path.exists(local_conf_file):
        return local_conf_file
    if os.path.exists(global_conf_file):
        return global_conf_file

    return None


def load_aztk_spark_config():
    return aztk.spark.models.SparkConfiguration(
        spark_defaults_conf=get_file_if_exists("spark-defaults.conf"),
        jars=load_jars(),
        spark_env_sh=get_file_if_exists("spark-env.sh"),
        core_site_xml=get_file_if_exists("core-site.xml"),
    )


def load_jars():
    jars = None

    # try load global
    try:
        jars_src = os.path.join(aztk.utils.constants.GLOBAL_CONFIG_PATH, "jars")
        jars = [os.path.join(jars_src, jar) for jar in os.listdir(jars_src)]
    except FileNotFoundError:
        pass

    # try load local, overwrite if found
    try:
        jars_src = os.path.join(aztk.utils.constants.DEFAULT_SPARK_CONF_SOURCE, "jars")
        jars = [os.path.join(jars_src, jar) for jar in os.listdir(jars_src)]
    except FileNotFoundError:
        pass

    return jars
