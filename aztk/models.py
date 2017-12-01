from typing import List
import aztk.utils.constants as constants
import azure.batch.models as batch_models

class FileShare:
    def __init__(self, storage_account_name: str = None,
        storage_account_key: str = None,
        file_share_path: str = None,
        mount_path: str = None):
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.file_share_path = file_share_path
        self.mount_path = mount_path

class CustomScript:
    def __init__(self, name: str = None, script: str = None, run_on=None):
        self.name = name
        self.script = script
        self.run_on = run_on


class ClusterConfiguration:
    def __init__(
            self,
            custom_scripts: List[CustomScript] = None,
            file_shares: List[FileShare] = None,
            cluster_id: str = None,
            vm_count=None,
            vm_low_pri_count=None,
            vm_size=None,
            docker_repo: str=None):

        self.custom_scripts = custom_scripts
        self.file_shares = file_shares
        self.cluster_id = cluster_id
        self.vm_count = vm_count
        self.vm_size = vm_size
        self.vm_low_pri_count = vm_low_pri_count
        self.docker_repo = docker_repo


class RemoteLogin:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port


class SecretsConfiguration:
    def __init__(
            self,
            batch_account_name=None,
            batch_account_key=None,
            batch_service_url=None,
            storage_account_name=None,
            storage_account_key=None,
            storage_account_suffix=None,
            docker_endpoint=None,
            docker_username=None,
            docker_password=None,
            ssh_pub_key=None,
            ssh_priv_key=None):

        self.batch_account_name = batch_account_name
        self.batch_account_key = batch_account_key
        self.batch_service_url = batch_service_url

        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.storage_account_suffix = storage_account_suffix

        self.docker_endpoint = docker_endpoint
        self.docker_username = docker_username
        self.docker_password = docker_password

        self.ssh_pub_key = ssh_pub_key
        self.ssh_priv_key = ssh_priv_key


class VmImage:
    def __init__(self, publisher, offer, sku):
        self.publisher = publisher
        self.offer = offer
        self.sku = sku


class Cluster:
    def __init__(self, pool: batch_models.CloudPool, nodes: batch_models.ComputeNodePaged = None):
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


class Software:
    """
        Enum with list of available softwares
    """
    spark = "spark"
