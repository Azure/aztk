from typing import List

import azure.batch.models.batch_error as batch_error

from aztk import error
from aztk import models as base_models
from aztk.client import CoreClient
from aztk.spark import models
from aztk.spark.client.cluster import ClusterOperations
from aztk.spark.client.job import JobOperations
from aztk.spark.helpers import job_submission as job_submit_helper
from aztk.spark.utils import util
from aztk.utils import deprecate, deprecated, helpers


class Client(CoreClient):
    """The client used to create and manage Spark clusters

        Attributes:
            cluster (:obj:`aztk.spark.client.cluster.ClusterOperations`): Cluster
            job (:obj:`aztk.spark.client.job.JobOperations`): Job
    """

    def __init__(self, secrets_configuration: models.SecretsConfiguration = None, **kwargs):
        super().__init__()
        context = None
        if kwargs.get("secrets_config"):
            deprecate(
                version="0.10.0",
                message="secrets_config key is deprecated in secrets.yaml",
                advice="Please use secrets_configuration key instead.",
            )
            context = self._get_context(kwargs.get("secrets_config"))
        else:
            context = self._get_context(secrets_configuration)
        self.cluster = ClusterOperations(context)
        self.job = JobOperations(context)

    # ALL THE FOLLOWING METHODS ARE DEPRECATED AND WILL BE REMOVED IN 0.10.0

    @deprecated("0.10.0")
    def create_cluster(self, cluster_conf: models.ClusterConfiguration, wait: bool = False):
        return self.cluster.create(cluster_configuration=cluster_conf, wait=wait)

    @deprecated("0.10.0")
    def create_clusters_in_parallel(self, cluster_confs):    # NOT IMPLEMENTED
        for cluster_conf in cluster_confs:
            self.cluster.create(cluster_conf)

    @deprecated("0.10.0")
    def delete_cluster(self, cluster_id: str, keep_logs: bool = False):
        return self.cluster.delete(id=cluster_id, keep_logs=keep_logs)

    @deprecated("0.10.0")
    def get_cluster(self, cluster_id: str):
        return self.cluster.get(id=cluster_id)

    @deprecated("0.10.0")
    def list_clusters(self):
        return self.cluster.list()

    @deprecated("0.10.0")
    def get_remote_login_settings(self, cluster_id: str, node_id: str):
        return self.cluster.get_remote_login_settings(cluster_id, node_id)

    @deprecated("0.10.0")
    def submit(self,
               cluster_id: str,
               application: models.ApplicationConfiguration,
               remote: bool = False,
               wait: bool = False):
        return self.cluster.submit(id=cluster_id, application=application, remote=remote, wait=wait)

    @deprecated("0.10.0")
    def submit_all_applications(self, cluster_id: str, applications):    # NOT IMPLEMENTED
        for application in applications:
            self.cluster.submit(cluster_id, application)

    @deprecated("0.10.0")
    def wait_until_application_done(self, cluster_id: str, task_id: str):    # NOT IMPLEMENTED
        try:
            helpers.wait_for_task_to_complete(job_id=cluster_id, task_id=task_id, batch_client=self.batch_client)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    @deprecated("0.10.0")
    def wait_until_applications_done(self, cluster_id: str):    # NOT IMPLEMENTED
        try:
            helpers.wait_for_tasks_to_complete(job_id=cluster_id, batch_client=self.batch_client)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    @deprecated("0.10.0")
    def wait_until_cluster_is_ready(self, cluster_id: str):    # NOT IMPLEMENTED
        try:
            util.wait_for_master_to_be_ready(self.cluster._core_cluster_operations, self.cluster, cluster_id)
            pool = self.batch_client.pool.get(cluster_id)
            nodes = self.batch_client.compute_node.list(pool_id=cluster_id)
            return models.Cluster(base_models.Cluster(pool, nodes))
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    @deprecated("0.10.0")
    def wait_until_all_clusters_are_ready(self, clusters: List[str]):    # NOT IMPLEMENTED
        for cluster_id in clusters:
            self.wait_until_cluster_is_ready(cluster_id)

    @deprecated("0.10.0")
    def create_user(self, cluster_id: str, username: str, password: str = None, ssh_key: str = None) -> str:
        return self.cluster.create_user(id=cluster_id, username=username, password=password, ssh_key=ssh_key)

    @deprecated("0.10.0")
    def get_application_log(self, cluster_id: str, application_name: str, tail=False, current_bytes: int = 0):
        return self.cluster.get_application_log(
            id=cluster_id, application_name=application_name, tail=tail, current_bytes=current_bytes)

    @deprecated("0.10.0")
    def get_application_status(self, cluster_id: str, app_name: str):
        return self.cluster.get_application_status(id=cluster_id, application_name=app_name)

    @deprecated("0.10.0")
    def cluster_run(self, cluster_id: str, command: str, host=False, internal: bool = False, timeout=None):
        return self.cluster.run(id=cluster_id, command=command, host=host, internal=internal)

    @deprecated("0.10.0")
    def node_run(self, cluster_id: str, node_id: str, command: str, host=False, internal: bool = False, timeout=None):
        return self.cluster.node_run(
            id=cluster_id, node_id=node_id, command=command, host=host, internal=internal, timeout=timeout)

    @deprecated("0.10.0")
    def cluster_copy(
            self,
            cluster_id: str,
            source_path: str,
            destination_path: str,
            host: bool = False,
            internal: bool = False,
            timeout: int = None,
    ):
        return self.cluster.copy(
            id=cluster_id,
            source_path=source_path,
            destination_path=destination_path,
            host=host,
            internal=internal,
            timeout=timeout,
        )

    @deprecated("0.10.0")
    def cluster_download(
            self,
            cluster_id: str,
            source_path: str,
            destination_path: str = None,
            host: bool = False,
            internal: bool = False,
            timeout: int = None,
    ):
        return self.cluster.download(
            id=cluster_id,
            source_path=source_path,
            destination_path=destination_path,
            host=host,
            internal=internal,
            timeout=timeout,
        )

    @deprecated("0.10.0")
    def cluster_ssh_into_master(self,
                                cluster_id,
                                node_id,
                                username,
                                ssh_key=None,
                                password=None,
                                port_forward_list=None,
                                internal=False):
        return self.cluster._core_cluster_operations.ssh_into_node(cluster_id, node_id, username, ssh_key, password,
                                                                   port_forward_list, internal)

    """
        job submission
    """

    @deprecated("0.10.0")
    def submit_job(self, job_configuration: models.JobConfiguration):
        return self.job.submit(job_configuration)

    @deprecated("0.10.0")
    def list_jobs(self):
        return self.job.list()

    @deprecated("0.10.0")
    def list_applications(self, job_id):
        return self.job.list_applications(job_id)

    @deprecated("0.10.0")
    def get_job(self, job_id):
        return self.job.get(job_id)

    @deprecated("0.10.0")
    def stop_job(self, job_id):
        return self.job.stop(job_id)

    @deprecated("0.10.0")
    def delete_job(self, job_id: str, keep_logs: bool = False):
        return self.job.delete(job_id, keep_logs)

    @deprecated("0.10.0")
    def get_application(self, job_id, application_name):
        return self.job.get_application(job_id, application_name)

    @deprecated("0.10.0")
    def get_job_application_log(self, job_id, application_name):
        return self.job.get_application_log(job_id, application_name)

    @deprecated("0.10.0")
    def stop_job_app(self, job_id, application_name):    # NOT IMPLEMENTED
        try:
            return job_submit_helper.stop_app(self, job_id, application_name)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    @deprecated("0.10.0")
    def wait_until_job_finished(self, job_id):
        try:
            self.job.wait(job_id)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    @deprecated("0.10.0")
    def wait_until_all_jobs_finished(self, jobs):    # NOT IMPLEMENTED
        for job in jobs:
            self.wait_until_job_finished(job)

    @deprecated("0.10.0")
    def run_cluster_diagnostics(self, cluster_id, output_directory=None):
        return self.cluster.diagnostics(cluster_id, output_directory)
