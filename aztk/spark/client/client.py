from aztk.client import CoreClient
from aztk.spark import models
from aztk.spark.client.cluster import ClusterOperations
from aztk.spark.client.job import JobOperations


class Client(CoreClient):
    """The client used to create and manage Spark clusters

        Attributes:
            cluster (:obj:`aztk.spark.client.cluster.ClusterOperations`): Cluster
            job (:obj:`aztk.spark.client.job.JobOperations`): Job
    """

    def __init__(self, secrets_configuration: models.SecretsConfiguration):
        super().__init__()
        context = self._get_context(secrets_configuration)
        self.cluster = ClusterOperations(context)
        self.job = JobOperations(context)
