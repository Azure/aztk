from aztk.client.base import BaseOperations

from .helpers import submit


class CoreJobOperations(BaseOperations):
    def submit(
            self,
            job_configuration,
            start_task,
            job_manager_task,
            autoscale_formula,
            software_metadata_key: str,
            vm_image_model,
            application_metadata,
    ):
        """Submit a job

        Jobs are a cluster definition and one or many application definitions which run on the cluster. The job's
        cluster will be allocated and configured, then the applications will be executed with their output stored
        in Azure Storage. When all applications have completed, the cluster will be automatically deleted.

        Args:
            job_configuration (:obj:`aztk.models.JobConfiguration`): Model defining the job's configuration.
            start_task (:obj:`azure.batch.models.StartTask`): Batch StartTask defintion to configure the Batch Pool
            job_manager_task (:obj:`azure.batch.models.JobManagerTask`): Batch JobManagerTask defintion to schedule
                the defined applications on the cluster.
            autoscale_formula (:obj:`str`): formula that defines the numbers of nodes allocated to the cluster.
            software_metadata_key (:obj:`str`): the key of the primary softare running on the cluster.
            vm_image_model
            application_metadata (:obj:`List[str]`): list of the names of all applications that will be run as a
                part of the job

        Returns:
            :obj:`azure.batch.models.CloudJobSchedule`: Model representing the Azure Batch JobSchedule state.
        """
        return submit.submit_job(
            self,
            job_configuration,
            start_task,
            job_manager_task,
            autoscale_formula,
            software_metadata_key,
            vm_image_model,
            application_metadata,
        )
