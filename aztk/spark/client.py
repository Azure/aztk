from typing import List
import azure.batch.models.batch_error as batch_error
import aztk
from aztk import error
from aztk.client import Client as BaseClient
from aztk.spark import models
from aztk.utils import helpers
from aztk.spark.helpers import create_cluster as create_cluster_helper
from aztk.spark.helpers import submit as cluster_submit_helper
from aztk.spark.helpers import job_submission as job_submit_helper
from aztk.spark.helpers import get_log as get_log_helper
from aztk.spark.utils import upload_node_scripts, util
import yaml


class Client(BaseClient):
    def __init__(self, secrets_config):
        super().__init__(secrets_config)

    '''
    Spark client public interface
    '''
    def create_cluster(self, cluster_conf: models.ClusterConfiguration, wait: bool = False):
        cluster_conf.validate()

        try:
            zip_resource_files = upload_node_scripts.zip_scripts(self.blob_client,
                                                                 cluster_conf.cluster_id,
                                                                 cluster_conf.custom_scripts,
                                                                 cluster_conf.spark_configuration,
                                                                 cluster_conf.user_configuration,
                                                                 cluster_conf.plugins)

            start_task = create_cluster_helper.generate_cluster_start_task(self,
                                                                           zip_resource_files,
                                                                           cluster_conf.gpu_enabled(),
                                                                           cluster_conf.docker_repo,
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

    def delete_cluster(self, cluster_id: str):
        try:
            return self.__delete_pool_and_job(cluster_id)
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

    def submit(self, cluster_id: str, application: models.ApplicationConfiguration, wait: bool = False):
        try:
            cluster_submit_helper.submit_application(self, cluster_id, application, wait)
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
            self.__create_user(cluster.id, master_node_id, username, password, ssh_key)
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

    def cluster_run(self, cluster_id: str, command: str):
        try:
            return self.__cluster_run(cluster_id, 'spark', command)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    def cluster_copy(self, cluster_id: str, source_path: str, destination_path: str):
        try:
            return self.__cluster_copy(cluster_id, 'spark', source_path, destination_path)
        except batch_error.BatchErrorException as e:
            raise error.AztkError(helpers.format_batch_exception(e))

    '''
        job submission
    '''
    def submit_job(self, job_configuration):
        try:
            zip_resource_files = upload_node_scripts.zip_scripts(self.blob_client,
                                                                 job_configuration.id,
                                                                 job_configuration.custom_scripts,
                                                                 job_configuration.spark_configuration)

            start_task = create_cluster_helper.generate_cluster_start_task(self,
                                                                           zip_resource_files,
                                                                           job_configuration.gpu_enabled,
                                                                           job_configuration.docker_repo,
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

            if job_configuration.max_dedicated_nodes and not job_configuration.max_low_pri_nodes:
                autoscale_formula = "maxNumberofVMs = {0}; targetNumberofVMs = {1};" \
                                    " $TargetDedicatedNodes=min(maxNumberofVMs, targetNumberofVMs)".format(
                                        job_configuration.max_dedicated_nodes, job_configuration.max_dedicated_nodes)
            elif job_configuration.max_low_pri_nodes and not job_configuration.max_dedicated_nodes:
                autoscale_formula = "maxNumberofVMs = {0}; targetNumberofVMs = {1};" \
                                    " $TargetLowPriorityNodes=min(maxNumberofVMs, targetNumberofVMs)".format(
                                        job_configuration.max_low_pri_nodes, job_configuration.max_low_pri_nodes)
            else:
                raise error.AztkError("Jobs do not support both dedicated and low priority nodes." \
                                      " JobConfiguration fields max_dedicated_nodes and max_low_pri_nodes are mutually exclusive values.")

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

    def delete_job(self, job_id):
        try:
            return job_submit_helper.delete(self, job_id)
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
