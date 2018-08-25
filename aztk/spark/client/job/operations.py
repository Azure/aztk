from aztk.client.job import CoreJobOperations
from aztk.spark import models
from aztk.spark.client.base import SparkBaseOperations

from .helpers import (
    delete,
    get,
    get_application,
    get_application_log,
    list,
    list_applications,
    stop,
    stop_application,
    submit,
    wait_until_complete,
)


class JobOperations(SparkBaseOperations):
    """Spark ClusterOperations object

    Attributes:
        _core_job_operations (:obj:`aztk.client.cluster.CoreJobOperations`):
    """

    def __init__(self, context):
        self._core_job_operations = CoreJobOperations(context)
        # self._spark_base_cluster_operations = SparkBaseOperations()

    def list(self):
        """List all jobs.

        Returns:
            :obj:`List[Job]`: List of aztk.models.Job objects each representing the state and configuration of the job.
        """
        return list.list_jobs(self._core_job_operations)

    def delete(self, id, keep_logs: bool = False):
        """Delete a job.

        Args:
            id (:obj:`str`): the id of the job to delete.
            keep_logs (:obj:`bool`): If True, the logs related to this job in Azure Storage are not deleted.
                Defaults to False.
        Returns:
            :obj:`bool`: True if the deletion process was successful.
        """
        return delete.delete(self._core_job_operations, self, id, keep_logs)

    def get(self, id):
        """Get details about the state of a job.

        Args:
            id (:obj:`str`): the id of the job to get.

        Returns:
            :obj:`aztk.spark.models.job`: A job object representing the state and configuration of the job.
        """
        return get.get_job(self._core_job_operations, id)

    def get_application(self, id, application_name):
        """Get information on a submitted application

        Args:
            id (:obj:`str`): the name of the job the application was submitted to
            application_name (:obj:`str`): the name of the application to get

        Returns:
            :obj:`aztk.spark.models.Application`: object representing that state and output of an application
        """
        return get_application.get_application(self, id, application_name)

    def get_application_log(self, id, application_name):
        """Get the log for a running or completed application

        Args:
            id (:obj:`str`): the id of the job the application was submitted to.
            application_name (:obj:`str`): the name of the application to get the log of

        Returns:
            :obj:`aztk.spark.models.ApplicationLog`: a model representing the output of the application.
        """
        return get_application_log.get_job_application_log(self._core_job_operations, self, id, application_name)

    def list_applications(self, id):
        """List all application defined as a part of a job

        Args:
            id (:obj:`str`): the id of the job to list the applications of

        Returns:
            :obj:`List[aztk.spark.models.Application]`: a list of all applications defined as a part of the job
        """
        return list_applications.list_applications(self._core_job_operations, id)

    def stop(self, id):
        """Stop a submitted job

        Args:
            id (:obj:`str`): the id of the job to stop

        Returns:
            :obj:`None`
        """
        return stop.stop(self._core_job_operations, id)

    def stop_application(self, id, application_name):
        """Stops a submitted application

        Args:
            id (:obj:`str`): the id of the job the application belongs to
            application_name (:obj:`str`):  the name of the application to stop

        Returns:
            :obj:`bool`: True if the stop was successful, else False
        """
        return stop_application.stop_app(self._core_job_operations, id, application_name)

    def submit(self, job_configuration: models.JobConfiguration, wait: bool = False):
        """Submit a job

        Jobs are a cluster definition and one or many application definitions which run on the cluster. The job's
        cluster will be allocated and configured, then the applications will be executed with their output stored
        in Azure Storage. When all applications have completed, the cluster will be automatically deleted.

        Args:
            job_configuration (:obj:`aztk.spark.models.JobConfiguration`): Model defining the job's configuration.
            wait (:obj:`bool`): If True, blocks until job is completed. Defaults to False.

        Returns:
            :obj:`aztk.spark.models.Job`: Model representing the state of the job.
        """
        return submit.submit_job(self._core_job_operations, self, job_configuration, wait)

    def wait(self, id):
        """Wait until the job has completed.
        Args:
            id (:obj:`str`): the id of the job the application belongs to

        Returns:
            :obj:`None`
        """
        wait_until_complete.wait_until_job_finished(self._core_job_operations, id)
