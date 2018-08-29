from typing import List

import azure.batch.models as batch_models
from Cryptodome.PublicKey import RSA

import aztk.models
from aztk import error
from aztk.core.models import Model, fields
from aztk.utils import constants, helpers


class SparkToolkit(aztk.models.Toolkit):
    def __init__(self, version: str, environment: str = None, environment_version: str = None):
        super().__init__(
            software="spark", version=version, environment=environment, environment_version=environment_version)


class Cluster(aztk.models.Cluster):
    def __init__(self, cluster: aztk.models.Cluster):
        super().__init__(cluster.pool, cluster.nodes)
        self.master_node_id = self.__get_master_node_id()
        self.gpu_enabled = helpers.is_gpu_enabled(cluster.pool.vm_size)

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
    def __init__(self, remote_login: aztk.models.RemoteLogin):
        super().__init__(remote_login.ip_address, remote_login.port)


class PortForwardingSpecification(aztk.models.PortForwardingSpecification):
    pass


class File(aztk.models.File):
    pass


class SparkConfiguration(Model):
    spark_defaults_conf = fields.String(default=None)
    spark_env_sh = fields.String(default=None)
    core_site_xml = fields.String(default=None)
    jars = fields.List()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh_key_pair = self.__generate_ssh_key_pair()

    def __generate_ssh_key_pair(self):
        key = RSA.generate(2048)
        priv_key = key.exportKey("PEM")
        pub_key = key.publickey().exportKey("OpenSSH")
        return {"pub_key": pub_key, "priv_key": priv_key}


class CustomScript(aztk.models.CustomScript):
    pass


class FileShare(aztk.models.FileShare):
    pass


class UserConfiguration(aztk.models.UserConfiguration):
    pass


class ServicePrincipalConfiguration(aztk.models.ServicePrincipalConfiguration):
    pass


class SharedKeyConfiguration(aztk.models.SharedKeyConfiguration):
    pass


class DockerConfiguration(aztk.models.DockerConfiguration):
    pass


class PluginConfiguration(aztk.models.PluginConfiguration):
    pass


# SchedulingTarget = aztk.models.SchedulingTarget


class ClusterConfiguration(aztk.models.ClusterConfiguration):
    spark_configuration = fields.Model(SparkConfiguration, default=None)
    worker_on_master = fields.Boolean(default=True)


class SecretsConfiguration(aztk.models.SecretsConfiguration):
    pass


class VmImage(aztk.models.VmImage):
    pass


class ApplicationConfiguration:
    def __init__(
            self,
            name=None,
            application=None,
            application_args=None,
            main_class=None,
            jars=None,
            py_files=None,
            files=None,
            driver_java_options=None,
            driver_library_path=None,
            driver_class_path=None,
            driver_memory=None,
            executor_memory=None,
            driver_cores=None,
            executor_cores=None,
            max_retry_count=None,
    ):
        self.name = name
        self.application = application
        self.application_args = application_args
        self.main_class = main_class
        self.jars = jars or []
        self.py_files = py_files or []
        self.files = files or []
        self.driver_java_options = driver_java_options
        self.driver_library_path = driver_library_path
        self.driver_class_path = driver_class_path
        self.driver_memory = driver_memory
        self.executor_memory = executor_memory
        self.driver_cores = driver_cores
        self.executor_cores = executor_cores
        self.max_retry_count = max_retry_count


class Application:
    def __init__(self, cloud_task: batch_models.CloudTask):
        self.name = cloud_task.id
        self.last_modified = cloud_task.last_modified
        self.creation_time = cloud_task.creation_time
        self.state = cloud_task.state.name
        self.state_transition_time = cloud_task.state_transition_time
        self.exit_code = cloud_task.execution_info.exit_code
        if cloud_task.previous_state:
            self.previous_state = cloud_task.previous_state.name
            self.previous_state_transition_time = cloud_task.previous_state_transition_time

        self._execution_info = cloud_task.execution_info
        self._node_info = cloud_task.node_info
        self._stats = cloud_task.stats
        self._multi_instance_settings = cloud_task.multi_instance_settings
        self._display_name = cloud_task.display_name
        self._exit_conditions = cloud_task.exit_conditions
        self._command_line = cloud_task.command_line
        self._resource_files = cloud_task.resource_files
        self._output_files = cloud_task.output_files
        self._environment_settings = cloud_task.environment_settings
        self._affinity_info = cloud_task.affinity_info
        self._constraints = cloud_task.constraints
        self._user_identity = cloud_task.user_identity
        self._depends_on = cloud_task.depends_on
        self._application_package_references = cloud_task.application_package_references
        self._authentication_token_settings = cloud_task.authentication_token_settings
        self._url = cloud_task.url
        self._e_tag = cloud_task.e_tag


class JobConfiguration:
    def __init__(
            self,
            id=None,
            applications=None,
            vm_size=None,
            spark_configuration=None,
            toolkit=None,
            max_dedicated_nodes=0,
            max_low_pri_nodes=0,
            subnet_id=None,
    # scheduling_target: SchedulingTarget = None,
            worker_on_master=None,
    ):

        self.id = id
        self.applications = applications
        self.spark_configuration = spark_configuration
        self.vm_size = vm_size
        self.gpu_enabled = None
        if vm_size:
            self.gpu_enabled = helpers.is_gpu_enabled(vm_size)
        self.toolkit = toolkit
        self.max_dedicated_nodes = max_dedicated_nodes
        self.max_low_pri_nodes = max_low_pri_nodes
        self.subnet_id = subnet_id
        self.worker_on_master = worker_on_master
        # self.scheduling_target = scheduling_target

    def to_cluster_config(self):
        return ClusterConfiguration(
            cluster_id=self.id,
            toolkit=self.toolkit,
            vm_size=self.vm_size,
            size=self.max_dedicated_nodes,
            size_low_priority=self.max_low_pri_nodes,
            subnet_id=self.subnet_id,
            worker_on_master=self.worker_on_master,
            spark_configuration=self.spark_configuration,
        # scheduling_target=self.scheduling_target,
        )

    def mixed_mode(self) -> bool:
        return self.max_dedicated_nodes > 0 and self.max_low_pri_nodes > 0

    def get_docker_repo(self) -> str:
        return self.toolkit.get_docker_repo(self.gpu_enabled)

    def get_docker_run_options(self) -> str:
        return self.toolkit.get_docker_run_options()

    def validate(self) -> bool:
        """
        Validate the config at its current state.
        Raises: Error if invalid
        """
        if self.toolkit is None:
            raise error.InvalidModelError("Please supply a toolkit in the cluster configuration")

        self.toolkit.validate()

        if self.id is None:
            raise error.AztkError("Please supply an ID for the Job in your configuration.")

        if self.max_dedicated_nodes == 0 and self.max_low_pri_nodes == 0:
            raise error.AztkError("Please supply a valid (greater than 0) value for either max_dedicated_nodes "
                                  "or max_low_pri_nodes in your configuration.")

        if self.vm_size is None:
            raise error.AztkError("Please supply a vm_size in your configuration.")

        if self.mixed_mode() and not self.subnet_id:
            raise error.AztkError(
                "You must configure a VNET to use AZTK in mixed mode (dedicated and low priority nodes) "
                "and pass the subnet_id in your configuration..")

        # if self.scheduling_target == SchedulingTarget.Dedicated and self.max_dedicated_nodes == 0:
        #     raise error.InvalidModelError("Scheduling target cannot be Dedicated if dedicated vm size is 0")


class JobState:
    complete = "completed"
    active = "active"
    completed = "completed"
    disabled = "disabled"
    terminating = "terminating"
    deleting = "deleting"


class Job:
    def __init__(
            self,
            cloud_job_schedule: batch_models.CloudJobSchedule,
            cloud_tasks: List[batch_models.CloudTask] = None,
            pool: batch_models.CloudPool = None,
            nodes: batch_models.ComputeNodePaged = None,
    ):
        self.id = cloud_job_schedule.id
        self.last_modified = cloud_job_schedule.last_modified
        self.state = cloud_job_schedule.state.name
        self.state_transition_time = cloud_job_schedule.state_transition_time
        self.creation_time = cloud_job_schedule.creation_time
        self.applications = [Application(task) for task in (cloud_tasks or [])]
        if pool:
            self.cluster = Cluster(aztk.models.Cluster(pool, nodes))
        else:
            self.cluster = None


class ApplicationLog(aztk.models.ApplicationLog):
    def __init__(self, application_log: aztk.models.ApplicationLog):
        super().__init__(
            name=application_log.name,
            cluster_id=application_log.cluster_id,  # TODO: change to something cluster/job agnostic
            log=application_log.log,
            total_bytes=application_log.total_bytes,
            application_state=application_log.application_state,
            exit_code=application_log.exit_code,
        )
