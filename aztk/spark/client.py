from typing import List

import azure.batch.models.batch_error as batch_error

import aztk
from aztk import error
from aztk.client import Client as BaseClient
from aztk.internal.cluster_data import NodeData
from aztk.spark import models
from aztk.spark.helpers import create_cluster as create_cluster_helper
from aztk.spark.helpers import get_log as get_log_helper
from aztk.spark.helpers import job_submission as job_submit_helper
from aztk.spark.helpers import submit as cluster_submit_helper
from aztk.spark.helpers import cluster_diagnostic_helper
from aztk.spark.utils import util
from aztk.utils import helpers


class Client(BaseClient):
    """
    Aztk Spark Client
    This is the main entry point for using aztk for spark

    Args:
        secrets_config(aztk.spark.models.models.SecretsConfiguration): Configuration with all the needed credentials
    """

    def create_cluster(self, cluster_conf: models.ClusterConfiguration, wait: bool = False):
        """
        Create a new aztk spark cluster

        Args:
            cluster_conf(aztk.spark.models.models.ClusterConfiguration): Configuration for the the cluster to be created
            wait(bool): If you should wait for the cluster to be ready before returning

        Returns:
            aztk.spark.models.Cluster
        """
        cluster_conf = _apply_default_for_cluster_config(cluster_conf)
        cluster_conf.validate()

        cluster_data = self._get_cluster_data(cluster_conf.cluster_id)
        try:
            zip_resource_files = None
            node_data = NodeData(cluster_conf).add_core().done()
            zip_resource_files = cluster_data.upload_node_data(node_data).to_resource_file()

            start_task = create_cluster_helper.generate_cluster_start_task(self,
                                                                           zip_resource_files,
                                                                           cluster_conf.cluster_id,
                                                                           cluster_conf.gpu_enabled(),
                                                                           cluster_conf.get_docker_repo(),
                                                                           cluster_conf.file_shares,
                                                                           cluster_conf.plugins,
                                                                           cluster_conf.mixed_mode(),
                                                                           cluster_conf.worker_on_master)

            software_metadata_key = "spark"

            vm_image = models.VmImage(
                publisher='Canonical',
                offer='UbuntuServer',
                sku='16.04')

            cluster = self.__create_pool_and_job(
                cluster_conf, software_metadata_key, start_task, vm_image)

            # Wait for the master to be ready
            if wait:
                util.wait_for_master_to_be_ready(self, cluster.id)
                cluster = self.get_cluster(cluster.id)

            return cluster

        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def create_clusters_in_parallel(self, cluster_confs):
        for cluster_conf in cluster_confs:
            self.create_cluster(cluster_conf)

    def delete_cluster(self, cluster_id: str, keep_logs: bool = False):
        try:
            return self.__delete_pool_and_job(cluster_id, keep_logs)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def get_cluster(self, cluster_id: str):
        try:
            pool, nodes = self.__get_pool_details(cluster_id)
            return models.Cluster(pool, nodes)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def list_clusters(self):
        try:
            return [models.Cluster(pool) for pool in self.__list_clusters(aztk.models.Software.spark)]
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def get_remote_login_settings(self, cluster_id: str, node_id: str):
        try:
            return self.__get_remote_login_settings(cluster_id, node_id)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def submit(self, cluster_id: str, application: models.ApplicationConfiguration, remote: bool = False, wait: bool = False):
        try:
            cluster_submit_helper.submit_application(self, cluster_id, application, remote, wait)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def submit_all_applications(self, cluster_id: str, applications):
        for application in applications:
            self.submit(cluster_id, application)

    def wait_until_application_done(self, cluster_id: str, task_id: str):
        try:
            helpers.wait_for_task_to_complete(job_id=cluster_id, task_id=task_id, batch_client=self.batch_client)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def wait_until_applications_done(self, cluster_id: str):
        try:
            helpers.wait_for_tasks_to_complete(job_id=cluster_id, batch_client=self.batch_client)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def wait_until_cluster_is_ready(self, cluster_id: str):
        try:
            util.wait_for_master_to_be_ready(self, cluster_id)
            pool = self.batch_client.pool.get(cluster_id)
            nodes = self.batch_client.compute_node.list(pool_id=cluster_id)
            return models.Cluster(pool, nodes)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def wait_until_all_clusters_are_ready(self, clusters: List[str]):
        for cluster_id in clusters:
            self.wait_until_cluster_is_ready(cluster_id)

    def create_user(self, cluster_id: str, username: str, password: str = None, ssh_key: str = None) -> str:
        try:
            cluster = self.get_cluster(cluster_id)
            master_node_id = cluster.master_node_id
            if not master_node_id:
                raise error.ClusterNotReadyError("The master has not yet been picked, a user cannot be added.")
            self.__create_user_on_pool(username, cluster.id, cluster.nodes, ssh_key, password)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def get_application_log(self, cluster_id: str, application_name: str, tail=False, current_bytes: int = 0):
        try:
            return get_log_helper.get_log(self.batch_client, self.blob_client,
                                          cluster_id, application_name, tail, current_bytes)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def get_application_status(self, cluster_id: str, app_name: str):
        try:
            task = self.batch_client.task.get(cluster_id, app_name)
            return task.state._value_
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def cluster_run(self, cluster_id: str, command: str, host=False, internal: bool = False, timeout=None):
        try:
            return self.__cluster_run(cluster_id,
                                      command,
                                      internal,
                                      container_name='spark' if not host else None,
                                      timeout=timeout)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def node_run(self, cluster_id: str, node_id: str, command: str, host=False, internal: bool = False, timeout=None):
        try:
            return self.__node_run(cluster_id,
                                   node_id,
                                   command,
                                   internal,
                                   container_name='spark' if not host else None,
                                   timeout=timeout)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def cluster_copy(self, cluster_id: str, source_path: str, destination_path: str, host: bool = False, internal: bool = False, timeout: int = None):
        try:
            container_name = None if host else 'spark'
            return self.__cluster_copy(cluster_id,
                                       source_path,
                                       destination_path=destination_path,
                                       container_name=container_name,
                                       get=False,
                                       internal=internal,
                                       timeout=timeout)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def cluster_download(self, cluster_id: str, source_path: str, destination_path: str = None, host: bool = False, internal: bool = False, timeout: int = None):
        try:
            container_name = None if host else 'spark'
            return self.__cluster_copy(cluster_id,
                                       source_path,
                                       destination_path=destination_path,
                                       container_name=container_name,
                                       get=True,
                                       internal=internal,
                                       timeout=timeout)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def cluster_ssh_into_master(self, cluster_id, node_id, username, ssh_key=None, password=None, port_forward_list=None, internal=False):
        try:
            self.__ssh_into_node(cluster_id, node_id, username, ssh_key, password, port_forward_list, internal)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    '''
        job submission
    '''
    def submit_job(self, job_configuration: models.JobConfiguration):
        try:
            job_configuration = _apply_default_for_job_config(job_configuration)
            job_configuration.validate()
            cluster_data = self._get_cluster_data(job_configuration.id)
            node_data =  NodeData(job_configuration.to_cluster_config()).add_core().done()
            zip_resource_files = cluster_data.upload_node_data(node_data).to_resource_file()

            start_task = create_cluster_helper.generate_cluster_start_task(self,
                                                                           zip_resource_files,
                                                                           job_configuration.id,
                                                                           job_configuration.gpu_enabled,
                                                                           job_configuration.get_docker_repo(),
                                                                           mixed_mode=job_configuration.mixed_mode(),
                                                                           worker_on_master=job_configuration.worker_on_master)

            application_tasks = []
            for application in job_configuration.applications:
                application_tasks.append(
                    (application, cluster_submit_helper.generate_task(self, job_configuration.id, application))
                )

            job_manager_task = job_submit_helper.generate_task(self, job_configuration, application_tasks)


            software_metadata_key = "spark"

            vm_image = models.VmImage(
                publisher='Canonical',
                offer='UbuntuServer',
                sku='16.04')

            autoscale_formula = "$TargetDedicatedNodes = {0}; " \
                                "$TargetLowPriorityNodes = {1}".format(
                                    job_configuration.max_dedicated_nodes,
                                    job_configuration.max_low_pri_nodes)

            job = self.__submit_job(
                job_configuration=job_configuration,
                start_task=start_task,
                job_manager_task=job_manager_task,
                autoscale_formula=autoscale_formula,
                software_metadata_key=software_metadata_key,
                vm_image_model=vm_image,
                application_metadata='\n'.join(application.name for application in (job_configuration.applications or [])))

            return models.Job(job)

        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def list_jobs(self):
        try:
            return [models.Job(cloud_job_schedule) for cloud_job_schedule in job_submit_helper.list_jobs(self)]
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def list_applications(self, job_id):
        try:
            applications = job_submit_helper.list_applications(self, job_id)
            for item in applications:
                if applications[item]:
                    applications[item] = models.Application(applications[item])
            return applications
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def get_job(self, job_id):
        try:
            job, apps, pool, nodes = job_submit_helper.get_job(self, job_id)
            return models.Job(job, apps, pool, nodes)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def stop_job(self, job_id):
        try:
            return job_submit_helper.stop(self, job_id)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def delete_job(self, job_id: str, keep_logs: bool = False):
        try:
            return job_submit_helper.delete(self, job_id, keep_logs)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def get_application(self, job_id, application_name):
        try:
            return models.Application(job_submit_helper.get_application(self, job_id, application_name))
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def get_job_application_log(self, job_id, application_name):
        try:
            return job_submit_helper.get_application_log(self, job_id, application_name)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def stop_job_app(self, job_id, application_name):
        try:
            return job_submit_helper.stop_app(self, job_id, application_name)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def wait_until_job_finished(self, job_id):
        try:
            job_submit_helper.wait_until_job_finished(self, job_id)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def wait_until_all_jobs_finished(self, jobs):
        for job in jobs:
            self.wait_until_job_finished(job)

    def run_cluster_diagnostics(self, cluster_id, output_directory=None):
        try:
            output = cluster_diagnostic_helper.run(self, cluster_id, output_directory)
            return output
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))


def _default_scheduling_target(vm_count: int):
    if vm_count == 0:
        return models.SchedulingTarget.Any
    else:
        return models.SchedulingTarget.Dedicated

def _apply_default_for_cluster_config(configuration: models.ClusterConfiguration):
    cluster_conf = models.ClusterConfiguration()
    cluster_conf.merge(configuration)
    if cluster_conf.scheduling_target is None:
        cluster_conf.scheduling_target = _default_scheduling_target(cluster_conf.size)
    return cluster_conf

def _apply_default_for_job_config(job_conf: models.JobConfiguration):
    if job_conf.scheduling_target is None:
        job_conf.scheduling_target = _default_scheduling_target(job_conf.max_dedicated_nodes)

    return job_conf
