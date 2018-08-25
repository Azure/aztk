from typing import List

import azure.batch.models as batch_models

from aztk.spark import models

from .helpers import generate_application_task, generate_cluster_start_task


class SparkBaseOperations:
    """Spark Base operations object that all other Spark operations objects inherit from
    """

    # TODO: make this private or otherwise not public
    def _generate_cluster_start_task(
            self,
            core_base_operations,
            zip_resource_file: batch_models.ResourceFile,
            id: str,
            gpu_enabled: bool,
            docker_repo: str = None,
            docker_run_options: str = None,
            file_shares: List[models.FileShare] = None,
            mixed_mode: bool = False,
            worker_on_master: bool = True,
    ):
        """Generate the Azure Batch Start Task to provision a Spark cluster.

        Args:
            zip_resource_file (:obj:`azure.batch.models.ResourceFile`): a single zip file of all necessary data
                to upload to the cluster.
            id (:obj:`str`): the id of the cluster.
            gpu_enabled (:obj:`bool`): if True, the cluster is GPU enabled.
            docker_repo (:obj:`str`, optional): the docker repository and tag that identifies the docker image to use.
                If None, the default Docker image will be used. Defaults to None.
            file_shares (:obj:`aztk.spark.models.FileShare`, optional): a list of FileShares to mount on the cluster.
                Defaults to None.
            mixed_mode (:obj:`bool`, optional): If True, the cluster is configured to use both dedicated
                and low priority VMs. Defaults to False.
            worker_on_master (:obj:`bool`, optional): If True, the cluster is configured to provision a Spark worker
                on the VM that runs the Spark master. Defaults to True.

        Returns:
            :obj:`azure.batch.models.StartTask`: the StartTask definition to provision the cluster.
        """
        return generate_cluster_start_task.generate_cluster_start_task(
            core_base_operations,
            zip_resource_file,
            id,
            gpu_enabled,
            docker_repo,
            docker_run_options,
            file_shares,
            mixed_mode,
            worker_on_master,
        )

    # TODO: make this private or otherwise not public
    def _generate_application_task(self, core_base_operations, container_id, application, remote=False):
        """Generate the Azure Batch Start Task to provision a Spark cluster.

        Args:
            container_id (:obj:`str`): the id of the container to run the application in
            application (:obj:`aztk.spark.models.ApplicationConfiguration): the Application Definition
            remote (:obj:`bool`): If True, the application file will not be uploaded, it is assumed to be reachable
                by the cluster already. This is useful when your application is stored in a mounted Azure File Share
                and not the client. Defaults to False.

        Returns:
            :obj:`azure.batch.models.TaskAddParameter`: the Task definition for the Application.
        """
        return generate_application_task.generate_application_task(core_base_operations, container_id, application,
                                                                   remote)
