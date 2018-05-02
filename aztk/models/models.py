import io
from typing import List
import azure.batch.models as batch_models
from aztk import error
from aztk.utils import helpers, deprecate
from aztk.models.plugins import PluginConfiguration
from aztk.internal import ConfigurationBase
from .toolkit import Toolkit


class FileShare:
    def __init__(self,
                 storage_account_name: str = None,
                 storage_account_key: str = None,
                 file_share_path: str = None,
                 mount_path: str = None):
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.file_share_path = file_share_path
        self.mount_path = mount_path

class File:
    def __init__(self, name: str, payload: io.StringIO):
        self.name = name
        self.payload = payload


class CustomScript:
    def __init__(self, name: str = None, script=None, run_on=None):
        self.name = name
        self.script = script
        self.run_on = run_on


class UserConfiguration(ConfigurationBase):
    def __init__(self,
                 username: str,
                 ssh_key: str = None,
                 password: str = None):
        self.username = username
        self.ssh_key = ssh_key
        self.password = password

    def merge(self, other):
        self._merge_attributes(other, [
            "username",
            "ssh_key",
            "password",
        ])

    def validate(self):
        pass


class ClusterConfiguration(ConfigurationBase):
    """
    Cluster configuration model

    Args:
        toolkit
    """

    def __init__(self,
                 toolkit: Toolkit = None,
                 custom_scripts: List[CustomScript] = None,
                 file_shares: List[FileShare] = None,
                 cluster_id: str = None,
                 vm_count=0,
                 vm_low_pri_count=0,
                 vm_size=None,
                 subnet_id=None,
                 plugins: List[PluginConfiguration] = None,
                 user_configuration: UserConfiguration = None):
        super().__init__()
        self.toolkit = toolkit
        self.custom_scripts = custom_scripts
        self.file_shares = file_shares
        self.cluster_id = cluster_id
        self.vm_count = vm_count
        self.vm_size = vm_size
        self.vm_low_pri_count = vm_low_pri_count
        self.subnet_id = subnet_id
        self.user_configuration = user_configuration
        self.plugins = plugins

    def merge(self, other):
        """
        Merge other cluster config into this one.
        :params other: ClusterConfiguration
        """

        self._merge_attributes(other, [
            "toolkit",
            "custom_scripts",
            "file_shares",
            "cluster_id",
            "vm_size",
            "subnet_id",
            "vm_count",
            "vm_low_pri_count",
            "plugins",
        ])

        if other.user_configuration:
            if self.user_configuration:
                self.user_configuration.merge(other.user_configuration)
            else:
                self.user_configuration = other.user_configuration

        if self.plugins:
            for plugin in self.plugins:
                plugin.validate()

    def mixed_mode(self) -> bool:
        return self.vm_count > 0 and self.vm_low_pri_count > 0


    def gpu_enabled(self):
        return helpers.is_gpu_enabled(self.vm_size)

    def get_docker_repo(self):
        return self.toolkit.get_docker_repo(self.gpu_enabled())

    def validate(self) -> bool:
        """
        Validate the config at its current state.
        Raises: Error if invalid
        """
        if self.toolkit is None:
            raise error.InvalidModelError(
                "Please supply a toolkit for the cluster")

        self.toolkit.validate()

        if self.cluster_id is None:
            raise error.AztkError(
                "Please supply an id for the cluster with a parameter (--id)")

        if self.vm_count == 0 and self.vm_low_pri_count == 0:
            raise error.AztkError(
                "Please supply a valid (greater than 0) size or size_low_pri value either in the cluster.yaml configuration file or with a parameter (--size or --size-low-pri)"
            )

        if self.vm_size is None:
            raise error.AztkError(
                "Please supply a vm_size in either the cluster.yaml configuration file or with a parameter (--vm-size)"
            )

        if self.mixed_mode() and not self.subnet_id:
            raise error.AztkError(
                "You must configure a VNET to use AZTK in mixed mode (dedicated and low priority nodes). Set the VNET's subnet_id in your cluster.yaml."
            )

        if self.custom_scripts:
            deprecate("Custom scripts are DEPRECATED and will be removed in 0.8.0. Use plugins instead See https://aztk.readthedocs.io/en/v0.7.0/15-plugins.html")


class RemoteLogin:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port


class ServicePrincipalConfiguration(ConfigurationBase):
    """
    Container class for AAD authentication
    """

    def __init__(self,
                 tenant_id: str = None,
                 client_id: str = None,
                 credential: str = None,
                 batch_account_resource_id: str = None,
                 storage_account_resource_id: str = None):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.credential = credential
        self.batch_account_resource_id = batch_account_resource_id
        self.storage_account_resource_id = storage_account_resource_id

    def validate(self) -> bool:
        """
        Validate the config at its current state.
        Raises: Error if invalid
        """
        self._validate_required([
            "tenant_id",
            "client_id",
            "credential",
            "batch_account_resource_id",
            "storage_account_resource_id",
        ])


class SharedKeyConfiguration(ConfigurationBase):
    """
    Container class for shared key authentication
    """

    def __init__(self,
                 batch_account_name: str = None,
                 batch_account_key: str = None,
                 batch_service_url: str = None,
                 storage_account_name: str = None,
                 storage_account_key: str = None,
                 storage_account_suffix: str = None):

        self.batch_account_name = batch_account_name
        self.batch_account_key = batch_account_key
        self.batch_service_url = batch_service_url
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.storage_account_suffix = storage_account_suffix

    def validate(self) -> bool:
        """
        Validate the config at its current state.
        Raises: Error if invalid
        """
        self._validate_required([
            "batch_account_name",
            "batch_account_key",
            "batch_service_url",
            "storage_account_name",
            "storage_account_key",
            "storage_account_suffix",
        ])


class DockerConfiguration(ConfigurationBase):
    def __init__(self, endpoint=None, username=None, password=None):

        self.endpoint = endpoint
        self.username = username
        self.password = password

    def validate(self):
        pass


class SecretsConfiguration(ConfigurationBase):
    def __init__(self,
                 service_principal=None,
                 shared_key=None,
                 docker=None,
                 ssh_pub_key=None,
                 ssh_priv_key=None):
        self.service_principal = service_principal
        self.shared_key = shared_key
        self.docker = docker

        self.ssh_pub_key = ssh_pub_key
        self.ssh_priv_key = ssh_priv_key

    def validate(self):
        if self.service_principal and self.shared_key:
            raise error.AztkError(
                "Both service_principal and shared_key auth are configured, must use only one"
            )
        elif self.service_principal:
            self.service_principal.validate()
        elif self.shared_key:
            self.shared_key.validate()
        else:
            raise error.AztkError(
                "Neither service_principal and shared_key auth are configured, must use only one"
            )

    def is_aad(self):
        return self.service_principal is not None


class VmImage:
    def __init__(self, publisher, offer, sku):
        self.publisher = publisher
        self.offer = offer
        self.sku = sku


class Cluster:
    def __init__(self,
                 pool: batch_models.CloudPool,
                 nodes: batch_models.ComputeNodePaged = None):
        self.id = pool.id
        self.pool = pool
        self.nodes = nodes
        self.vm_size = pool.vm_size
        if pool.state.value is batch_models.PoolState.active:
            self.visible_state = pool.allocation_state.value
        else:
            self.visible_state = pool.state.value
        self.total_current_nodes = pool.current_dedicated_nodes + \
            pool.current_low_priority_nodes
        self.total_target_nodes = pool.target_dedicated_nodes + \
            pool.target_low_priority_nodes
        self.current_dedicated_nodes = pool.current_dedicated_nodes
        self.current_low_pri_nodes = pool.current_low_priority_nodes
        self.target_dedicated_nodes = pool.target_dedicated_nodes
        self.target_low_pri_nodes = pool.target_low_priority_nodes


class SSHLog():
    def __init__(self, output, node_id):
        self.output = output
        self.node_id = node_id


class Software:
    """
        Enum with list of available softwares
    """
    spark = "spark"
