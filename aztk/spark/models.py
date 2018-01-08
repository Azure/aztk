from Crypto.PublicKey import RSA
from typing import List
import aztk.models
from aztk.utils import constants, helpers
import azure.batch.models as batch_models


class Cluster(aztk.models.Cluster):
    def __init__(self, pool: batch_models.CloudPool, nodes: batch_models.ComputeNodePaged = None):
        super().__init__(pool, nodes)
        self.master_node_id = self.__get_master_node_id()
        self.gpu_enabled = helpers.is_gpu_enabled(pool.vm_size)


    def is_pool_running_spark(self, pool: batch_models.CloudPool):
        if pool.metadata is None:
            return False

        for metadata in pool.metadata:
            if metadata.name == constants.AZTK_SOFTWARE_METADATA_KEY:
                return metadata.value == aztk.models.Software.spark

        return False

    def __get_master_node_id(self):
        """
            :returns: the id of the node that is the assigned master of this pool
        """
        if self.pool.metadata is None:
            return None

        for metadata in self.pool.metadata:
            if metadata.name == constants.MASTER_NODE_METADATA_KEY:
                return metadata.value

        return None

class RemoteLogin(aztk.models.RemoteLogin):
    pass


class SparkConfiguration():
    def __init__(self, spark_defaults_conf: str = None, spark_env_sh: str = None, core_site_xml: str = None, jars: List[str]=None):
        self.spark_defaults_conf = spark_defaults_conf
        self.spark_env_sh = spark_env_sh
        self.core_site_xml = core_site_xml
        self.jars = jars
        self.ssh_key_pair = self.__generate_ssh_key_pair()

    def __generate_ssh_key_pair(self):
        key = RSA.generate(2048)
        priv_key = key.exportKey('PEM')
        pub_key = key.publickey().exportKey('OpenSSH')
        return {'pub_key': pub_key, 'priv_key': priv_key}


class CustomScript(aztk.models.CustomScript):
    pass


class FileShare(aztk.models.FileShare):
    pass


class ClusterConfiguration(aztk.models.ClusterConfiguration):
    def __init__(
            self,
            custom_scripts: List[CustomScript] = None,
            file_shares: List[FileShare] = None,
            cluster_id: str = None,
            vm_count=None,
            vm_low_pri_count=None,
            vm_size=None,
            docker_repo: str=None,
            spark_configuration: SparkConfiguration = None):
        super().__init__(custom_scripts=custom_scripts,
              cluster_id=cluster_id,
              vm_count=vm_count,
              vm_low_pri_count=vm_low_pri_count,
              vm_size=vm_size,
              docker_repo=docker_repo,
              file_shares=file_shares
        )
        self.spark_configuration = spark_configuration
        self.gpu_enabled = helpers.is_gpu_enabled(vm_size)


class SecretsConfiguration(aztk.models.SecretsConfiguration):
    pass


class VmImage(aztk.models.VmImage):
    pass


class Application:
    def __init__(
            self,
            name=None,
            application=None,
            application_args=None,
            main_class=None,
            jars=[],
            py_files=[],
            files=[],
            driver_java_options=None,
            driver_library_path=None,
            driver_class_path=None,
            driver_memory=None,
            executor_memory=None,
            driver_cores=None,
            executor_cores=None,
            max_retry_count=None):
        self.name = name
        self.application = application
        self.application_args = application_args
        self.main_class = main_class
        self.jars = jars
        self.py_files = py_files
        self.files = files
        self.driver_java_options = driver_java_options
        self.driver_library_path = driver_library_path
        self.driver_class_path = driver_class_path
        self.driver_memory = driver_memory
        self.executor_memory = executor_memory
        self.driver_cores = driver_cores
        self.executor_cores = executor_cores
        self.max_retry_count = max_retry_count


class ApplicationLog():
    def __init__(self, name: str, cluster_id: str, log: str, total_bytes: int, application_state: batch_models.TaskState):
        self.name = name
        self.cluster_id = cluster_id
        self.log = log
        self.total_bytes = total_bytes
        self.application_state = application_state
