from aztk.client.base import BaseOperations
from aztk.models import ClusterConfiguration

from .helpers import copy, create, delete, get, list, wait_for_task_to_complete


class CoreClusterOperations(BaseOperations):
    def create(self, cluster_configuration: ClusterConfiguration, software_metadata_key: str, start_task,
               vm_image_model):
        """Create a cluster.

        Args:
            cluster_configuration (:obj:`aztk.models.ClusterConfiguration`): Configuration for the cluster to be created
            software_metadata_key (:obj:`str`): the key for the primary software that will be run on the cluster
            start_task (:obj:`azure.batch.models.StartTask`): Batch StartTask defintion to configure the Batch Pool
            vm_image_model (:obj:`azure.batch.models.VirtualMachineConfiguration`):
                Configuration of the virtual machine image and settings

        Returns:
            :obj:`aztk.models.Cluster`: A Cluster object representing the state and configuration of the cluster.
        """
        return create.create_pool_and_job(self, cluster_configuration, software_metadata_key, start_task,
                                          vm_image_model)

    def get(self, id: str):
        """Get the state and configuration of a cluster

        Args:
            id (:obj:`str`): the id of the cluster to get.

        Returns:
            :obj:`aztk.models.Cluster`: A Cluster object representing the state and configuration of the cluster.
        """
        return get.get_pool_details(self, id)

    def copy(self, id, source_path, destination_path=None, container_name=None, internal=False, get=False,
             timeout=None):
        """Copy files to or from every node in a cluster.

        Args:
            id (:obj:`str`): the id of the cluster to copy files with.
            source_path (:obj:`str`): the path of the file to copy from.
            destination_path (:obj:`str`, optional): the local directory path where the output should be written.
                If None, a SpooledTemporaryFile will be returned in the NodeOutput object, else the file will be
                written to this path. Defaults to None.
            container_name (:obj:`str`, optional): the name of the container to copy to or from.
                If None, the copy operation will occur on the host VM, Defaults to None.
            internal (:obj:`bool`, optional): if True, this will connect to the node using its internal IP.
                Only use this if running within the same VNET as the cluster. Defaults to False.
            get (:obj:`bool`, optional): If True, the file are downloaded from every node in the cluster.
                Else, the file is copied from the client to the node. Defaults to False.
            timeout (:obj:`int`, optional): The timeout in seconds for establishing a connection to the node.
                Defaults to None.

        Returns:
            :obj:`List[aztk.models.NodeOutput]`:
                A list of NodeOutput objects representing the output of the copy command.
        """
        return copy.cluster_copy(self, id, source_path, destination_path, container_name, internal, get, timeout)

    def delete(self, id: str, keep_logs: bool = False):
        """Copy files to or from every node in a cluster.

        Args:
            id (:obj:`str`): the id of the cluster to delete
            keep_logs (:obj:`bool`): If True, the logs related to this cluster in Azure Storage are not deleted.
                Defaults to False.

        Returns:
            :obj:`List[aztk.models.NodeOutput]`:
                A list of NodeOutput objects representing the output of the copy command.
        """
        return delete.delete_pool_and_job(self, id, keep_logs)

    def list(self, software_metadata_key):
        """List clusters running the specified software.

        Args:
            software_metadata_key(:obj:`str`): the key of the primary softare running on the cluster.
                This filters out non-aztk clusters and aztk clusters running other software.

        Returns:
            :obj:`List[aztk.models.Cluster]`: list of clusters running the software defined by software_metadata_key
        """
        return list.list_clusters(self, software_metadata_key)

    def wait(self, id, task_name):
        """Wait until the task has completed

        Args:
            id (:obj:`str`): the id of the job the task was submitted to
            task_name (:obj:`str`): the name of the task to wait for

        Returns:
            :obj:`None`
        """
        return wait_for_task_to_complete.wait_for_task_to_complete(self, id, task_name)
