import io
import logging

import azure.common
import yaml
from msrest.exceptions import ClientRequestError

from aztk.models import ClusterConfiguration
from aztk.utils import BackOffPolicy, retry

from .blob_data import BlobData
from .node_data import NodeData


class ClusterData:
    """
    Class handling the management of data for a cluster
    """

    # ALl data related to cluster(config, metadata, etc.) should be under this folder
    CLUSTER_DIR = "cluster"
    APPLICATIONS_DIR = "applications"
    CLUSTER_CONFIG_FILE = "config.yaml"

    def __init__(self, blob_client, cluster_id: str):
        self.blob_client = blob_client
        self.cluster_id = cluster_id
        self._ensure_container()

    @retry(retry_count=4, retry_interval=1, backoff_policy=BackOffPolicy.exponential, exceptions=(ClientRequestError))
    def save_cluster_config(self, cluster_config):
        blob_path = self.CLUSTER_DIR + "/" + self.CLUSTER_CONFIG_FILE
        content = yaml.dump(cluster_config)
        container_name = cluster_config.cluster_id
        self.blob_client.create_blob_from_text(container_name, blob_path, content)

    @retry(retry_count=4, retry_interval=1, backoff_policy=BackOffPolicy.exponential, exceptions=(ClientRequestError))
    def read_cluster_config(self):
        blob_path = self.CLUSTER_DIR + "/" + self.CLUSTER_CONFIG_FILE
        try:
            result = self.blob_client.get_blob_to_text(self.cluster_id, blob_path)
            return yaml.load(result.content)
        except azure.common.AzureMissingResourceHttpError:
            logging.warning("Cluster %s doesn't have cluster configuration in storage", self.cluster_id)
        except yaml.YAMLError:
            logging.warning("Cluster %s contains invalid cluster configuration in blob", self.cluster_id)

    @retry(retry_count=4, retry_interval=1, backoff_policy=BackOffPolicy.exponential, exceptions=(ClientRequestError))
    def upload_file(self, blob_path: str, local_path: str) -> BlobData:
        self.blob_client.create_blob_from_path(self.cluster_id, blob_path, local_path)
        return BlobData(self.blob_client, self.cluster_id, blob_path)

    @retry(retry_count=4, retry_interval=1, backoff_policy=BackOffPolicy.exponential, exceptions=(ClientRequestError))
    def upload_bytes(self, blob_path: str, bytes_io: io.BytesIO) -> BlobData:
        self.blob_client.create_blob_from_bytes(self.cluster_id, blob_path, bytes_io.getvalue())
        return BlobData(self.blob_client, self.cluster_id, blob_path)

    def upload_cluster_file(self, blob_path: str, local_path: str) -> BlobData:
        blob_data = self.upload_bytes(self.CLUSTER_DIR + "/" + blob_path, local_path)
        blob_data.dest = blob_path
        return blob_data

    def upload_application_file(self, blob_path: str, local_path: str) -> BlobData:
        blob_data = self.upload_file(self.APPLICATIONS_DIR + "/" + blob_path, local_path)
        blob_data.dest = blob_path
        return blob_data

    def upload_node_data(self, node_data: NodeData) -> BlobData:
        return self.upload_cluster_file("node-scripts.zip", node_data.zip_path)

    @retry(retry_count=4, retry_interval=1, backoff_policy=BackOffPolicy.exponential, exceptions=(ClientRequestError))
    def _ensure_container(self):
        self.blob_client.create_container(self.cluster_id, fail_on_exist=False)

    @retry(retry_count=4, retry_interval=1, backoff_policy=BackOffPolicy.exponential, exceptions=(ClientRequestError))
    def delete_container(self, container_name: str):
        self.blob_client.delete_container(container_name)
