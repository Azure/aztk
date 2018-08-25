from aztk.client.cluster import CoreClusterOperations
from aztk.spark import models
from aztk.spark.client.base import SparkBaseOperations

from .helpers import (
    copy,
    create,
    create_user,
    delete,
    diagnostics,
    download,
    get,
    get_application_log,
    get_application_status,
    get_configuration,
    get_remote_login_settings,
    list,
    node_run,
    run,
    ssh_into_master,
    submit,
    wait,
)


class ClusterOperations(SparkBaseOperations):
    """Spark ClusterOperations object

    Attributes:
        _core_cluster_operations (:obj:`aztk.client.cluster.CoreClusterOperations`):
        # _spark_base_cluster_operations (:obj:`aztk.spark.client.cluster.CoreClusterOperations`):
    """

    def __init__(self, context):
        self._core_cluster_operations = CoreClusterOperations(context)
        # self._spark_base_cluster_operations = SparkBaseOperations()

    def create(self, cluster_configuration: models.ClusterConfiguration, wait: bool = False):
        """Create a cluster.

        Args:
            cluster_configuration (:obj:`ClusterConfiguration`): Configuration for the cluster to be created.
            wait (:obj:`bool`): if True, this function will block until the cluster creation is finished.

        Returns:
            :obj:`aztk.spark.models.Cluster`: An Cluster object representing the state and configuration of the cluster.
        """
        return create.create_cluster(self._core_cluster_operations, self, cluster_configuration, wait)

    def delete(self, id: str, keep_logs: bool = False):
        """Delete a cluster.

        Args:
            id (:obj:`str`): the id of the cluster to delete.
            keep_logs (:obj:`bool`): If True, the logs related to this cluster in Azure Storage are not deleted.
                Defaults to False.
        Returns:
            :obj:`bool`: True if the deletion process was successful.
        """
        return delete.delete_cluster(self._core_cluster_operations, id, keep_logs)

    def get(self, id: str):
        """Get details about the state of a cluster.

        Args:
            id (:obj:`str`): the id of the cluster to get.

        Returns:
            :obj:`aztk.spark.models.Cluster`: A Cluster object representing the state and configuration of the cluster.
        """
        return get.get_cluster(self._core_cluster_operations, id)

    def list(self):
        """List all clusters.

        Returns:
            :obj:`List[aztk.spark.models.Cluster]`: List of Cluster objects each representing the state
                and configuration of the cluster.
        """
        return list.list_clusters(self._core_cluster_operations)

    def submit(self, id: str, application: models.ApplicationConfiguration, remote: bool = False, wait: bool = False):
        """Submit an application to a cluster.

        Args:
            id (:obj:`str`): the id of the cluster to submit the application to.
            application (:obj:`aztk.spark.models.ApplicationConfiguration`): Application definition
            remote (:obj:`bool`): If True, the application file will not be uploaded, it is assumed to be reachable
                by the cluster already. This is useful when your application is stored in a mounted Azure File Share
                and not the client. Defaults to False.
            wait (:obj:`bool`, optional): If True, this function blocks until the application has completed.
                Defaults to False.

        Returns:
            :obj:`None`
        """
        return submit.submit(self._core_cluster_operations, self, id, application, remote, wait)

    def create_user(self, id: str, username: str, password: str = None, ssh_key: str = None):
        """Create a user on every node in the cluster

        Args:
            username (:obj:`str`): name of the user to create.
            pool_id (:obj:`str`): id of the cluster to create the user on.
            ssh_key (:obj:`str`, optional): ssh public key to create the user with, must use ssh_key or password.
                Defaults to None.
            password (:obj:`str`, optional): password for the user, must use ssh_key or password. Defaults to None.

        Returns:
            :obj:`None`
        """
        return create_user.create_user(self._core_cluster_operations, self, id, username, ssh_key, password)

    def get_application_status(self, id: str, application_name: str):
        """Get the status of a submitted application

        Args:
            id (:obj:`str`): the name of the cluster the application was submitted to
            application_name (:obj:`str`): the name of the application to get

        Returns:
            :obj:`str`: the status state of the application
        """
        return get_application_status.get_application_status(self._core_cluster_operations, id, application_name)

    def run(self, id: str, command: str, host=False, internal: bool = False, timeout=None):
        """Run a bash command on every node in the cluster

        Args:
            id (:obj:`str`): the id of the cluster to run the command on.
            command (:obj:`str`): the bash command to execute on the node.
            internal (:obj:`bool`): if true, this will connect to the node using its internal IP.
                Only use this if running within the same VNET as the cluster. Defaults to False.
            container_name=None (:obj:`str`, optional): the name of the container to run the command in.
                If None, the command will run on the host VM. Defaults to None.
            timeout=None (:obj:`str`, optional): The timeout in seconds for establishing a connection to the node.
                Defaults to None.

        Returns:
            :obj:`List[aztk.spark.models.NodeOutput]`:
                list of NodeOutput objects containing the output of the run command
        """
        return run.cluster_run(self._core_cluster_operations, id, command, host, internal, timeout)

    def node_run(self, id: str, node_id: str, command: str, host=False, internal: bool = False, timeout=None):
        """Run a bash command on the given node

        Args:
            id (:obj:`str`): the id of the cluster to run the command on.
            node_id (:obj:`str`): the id of the node in the cluster to run the command on.
            command (:obj:`str`): the bash command to execute on the node.
            internal (:obj:`bool`): if True, this will connect to the node using its internal IP.
                Only use this if running within the same VNET as the cluster. Defaults to False.
            container_name=None (:obj:`str`, optional): the name of the container to run the command in.
                If None, the command will run on the host VM. Defaults to None.
            timeout=None (:obj:`str`, optional): The timeout in seconds for establishing a connection to the node.
                Defaults to None.

        Returns:
            :obj:`aztk.spark.models.NodeOutput`: object containing the output of the run command
        """
        return node_run.node_run(self._core_cluster_operations, id, node_id, command, host, internal, timeout)

    def copy(
            self,
            id: str,
            source_path: str,
            destination_path: str,
            host: bool = False,
            internal: bool = False,
            timeout: int = None,
    ):
        """Copy a file to every node in a cluster.

        Args:
            id (:obj:`str`): the id of the cluster to copy files with.
            source_path (:obj:`str`): the local path of the file to copy.
            destination_path (:obj:`str`, optional): the path on each node the file is copied to.
            container_name (:obj:`str`, optional): the name of the container to copy to or from.
                If None, the copy operation will occur on the host VM, Defaults to None.
            internal (:obj:`bool`, optional): if True, this will connect to the node using its internal IP.
                Only use this if running within the same VNET as the cluster. Defaults to False.
            timeout (:obj:`int`, optional): The timeout in seconds for establishing a connection to the node.
                Defaults to None.

        Returns:
            :obj:`List[aztk.spark.models.NodeOutput]`:
                A list of NodeOutput objects representing the output of the copy command.
        """
        return copy.cluster_copy(self._core_cluster_operations, id, source_path, destination_path, host, internal,
                                 timeout)

    def download(
            self,
            id: str,
            source_path: str,
            destination_path: str = None,
            host: bool = False,
            internal: bool = False,
            timeout: int = None,
    ):
        """Download a file from every node in a cluster.

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
            timeout (:obj:`int`, optional): The timeout in seconds for establishing a connection to the node.
                Defaults to None.

        Returns:
            :obj:`List[aztk.spark.models.NodeOutput]`:
                A list of NodeOutput objects representing the output of the copy command.
        """
        return download.cluster_download(self._core_cluster_operations, id, source_path, destination_path, host,
                                         internal, timeout)

    def diagnostics(self, id, output_directory: str = None, brief: bool = False):
        """Download a file from every node in a cluster.

        Args:
            id (:obj:`str`): the id of the cluster to copy files with.
            output_directory (:obj:`str`, optional): the local directory path where the output should be written.
                If None, a SpooledTemporaryFile will be returned in the NodeOutput object, else the file will be
                written to this path. Defaults to None.

        Returns:
            :obj:`List[aztk.spark.models.NodeOutput]`:
                A list of NodeOutput objects representing the output of the copy command.
        """
        return diagnostics.run_cluster_diagnostics(self, id, output_directory, brief)

    def get_application_log(self, id: str, application_name: str, tail=False, current_bytes: int = 0):
        """Get the log for a running or completed application

        Args:
            id (:obj:`str`): the id of the cluster to run the command on.
            application_name (:obj:`str`): str
            tail (:obj:`bool`, optional): If True, get the remaining bytes after current_bytes.
                Otherwise, the whole log will be retrieved. Only use this if streaming the log as it is being written.
                Defaults to False.
            current_bytes (:obj:`int`): Specifies the last seen byte, so only the bytes after current_bytes are
                retrieved. Only useful is streaming the log as it is being written. Only used if tail is True.

        Returns:
            :obj:`aztk.spark.models.ApplicationLog`: a model representing the output of the application.
        """
        return get_application_log.get_application_log(self._core_cluster_operations, id, application_name, tail,
                                                       current_bytes)

    def get_remote_login_settings(self, id: str, node_id: str):
        """Get the remote login information for a node in a cluster

        Args:
            id (:obj:`str`): the id of the cluster the node is in
            node_id (:obj:`str`): the id of the node in the cluster

        Returns:
            :obj:`aztk.spark.models.RemoteLogin`:
                Object that contains the ip address and port combination to login to a node
        """
        return get_remote_login_settings.get_remote_login_settings(self._core_cluster_operations, id, node_id)

    def wait(self, id: str, application_name: str):
        """Wait until the application has completed

        Args:
            id (:obj:`str`): the id of the cluster the application was submitted to
            application_name (:obj:`str`): the name of the application to wait for

        Returns:
            :obj:`None`
        """
        return wait.wait_for_application_to_complete(self._core_cluster_operations, id, application_name)

    def get_configuration(self, id: str):
        """Get the initial configuration of the cluster

        Args:
            id (:obj:`str`): the id of the cluster

        Returns:
            :obj:`aztk.spark.models.ClusterConfiguration`
        """
        return get_configuration.get_configuration(self._core_cluster_operations, id)

    def ssh_into_master(self, id, username, ssh_key=None, password=None, port_forward_list=None, internal=False):
        """Open an SSH tunnel to the Spark master node and forward the specified ports

        Args:
            id (:obj:`str`): the id of the cluster
            username (:obj:`str`): the name of the user to open the ssh session with
            ssh_key (:obj:`str`, optional): the ssh_key to authenticate the ssh user with.
                Must specify either `ssh_key` or `password`.
            password (:obj:`str`, optional): the password to authenticate the ssh user with.
                Must specify either `password` or `ssh_key`.
            port_forward_list (:obj:`aztk.spark.models.PortForwardingSpecification`, optional):
                List of the ports to forward.
            internal (:obj:`str`, optional): if True, this will connect to the node using its internal IP.
                Only use this if running within the same VNET as the cluster. Defaults to False.
        """
        return ssh_into_master.ssh_into_master(self, self._core_cluster_operations, id, username, ssh_key, password,
                                               port_forward_list, internal)
