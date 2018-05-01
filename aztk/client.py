import asyncio
import concurrent.futures
from datetime import datetime, timedelta, timezone

import azure.batch.models as batch_models
import azure.batch.models.batch_error as batch_error
import aztk.utils.azure_api as azure_api
import aztk.utils.constants as constants
import aztk.utils.get_ssh_key as get_ssh_key
import aztk.utils.helpers as helpers
import aztk.utils.ssh as ssh_lib
import aztk.models as models
import azure.batch.models as batch_models
from azure.batch.models import batch_error
from Crypto.PublicKey import RSA
from aztk.internal import cluster_data

class Client:
    def __init__(self, secrets_config: models.SecretsConfiguration):
        self.secrets_config = secrets_config

        azure_api.validate_secrets(secrets_config)
        self.batch_client = azure_api.make_batch_client(secrets_config)
        self.blob_client = azure_api.make_blob_client(secrets_config)

    def get_cluster_config(self, cluster_id: str) -> models.ClusterConfiguration:
        return self._get_cluster_data(cluster_id).read_cluster_config()

    def _get_cluster_data(self, cluster_id: str) -> cluster_data.ClusterData:
        """
        Returns ClusterData object to manage data related to the given cluster id
        """
        return cluster_data.ClusterData(self.blob_client, cluster_id)

    '''
    General Batch Operations
    '''

    def __delete_pool_and_job(self, pool_id: str, keep_logs: bool = False):
        """
            Delete a pool and it's associated job
            :param cluster_id: the pool to add the user to
            :return bool: deleted the pool if exists and job if exists
        """
        # job id is equal to pool id
        job_id = pool_id
        job_exists = True

        try:
            self.batch_client.job.get(job_id)
        except batch_models.batch_error.BatchErrorException:
            job_exists = False

        pool_exists = self.batch_client.pool.exists(pool_id)

        if job_exists:
            self.batch_client.job.delete(job_id)

        if pool_exists:
            self.batch_client.pool.delete(pool_id)

        if not keep_logs:
            cluster_data = self._get_cluster_data(pool_id)
            cluster_data.delete_container(pool_id)

        return job_exists or pool_exists

    def __create_pool_and_job(self, cluster_conf: models.ClusterConfiguration, software_metadata_key: str, start_task, VmImageModel):
        """
            Create a pool and job
            :param cluster_conf: the configuration object used to create the cluster
            :type cluster_conf: aztk.models.ClusterConfiguration
            :parm software_metadata_key: the id of the software being used on the cluster
            :param start_task: the start task for the cluster
            :param VmImageModel: the type of image to provision for the cluster
            :param wait: wait until the cluster is ready
        """
        self._get_cluster_data(cluster_conf.cluster_id).save_cluster_config(cluster_conf)
        # reuse pool_id as job_id
        pool_id = cluster_conf.cluster_id
        job_id = cluster_conf.cluster_id

        # Get a verified node agent sku
        sku_to_use, image_ref_to_use = \
            helpers.select_latest_verified_vm_image_with_node_agent_sku(
                VmImageModel.publisher, VmImageModel.offer, VmImageModel.sku, self.batch_client)

        network_conf = None
        if cluster_conf.subnet_id is not None:
            network_conf = batch_models.NetworkConfiguration(
                subnet_id=cluster_conf.subnet_id)
        auto_scale_formula = "$TargetDedicatedNodes={0}; $TargetLowPriorityNodes={1}".format(
            cluster_conf.vm_count, cluster_conf.vm_low_pri_count)

        # Confiure the pool
        pool = batch_models.PoolAddParameter(
            id=pool_id,
            virtual_machine_configuration=batch_models.VirtualMachineConfiguration(
                image_reference=image_ref_to_use,
                node_agent_sku_id=sku_to_use),
            vm_size=cluster_conf.vm_size,
            enable_auto_scale=True,
            auto_scale_formula=auto_scale_formula,
            auto_scale_evaluation_interval=timedelta(minutes=5),
            start_task=start_task,
            enable_inter_node_communication=True if not cluster_conf.subnet_id else False,
            max_tasks_per_node=1,
            network_configuration=network_conf,
            metadata=[
                batch_models.MetadataItem(
                    name=constants.AZTK_SOFTWARE_METADATA_KEY, value=software_metadata_key),
                batch_models.MetadataItem(
                        name=constants.AZTK_MODE_METADATA_KEY, value=constants.AZTK_CLUSTER_MODE_METADATA)
            ])

        # Create the pool + create user for the pool
        helpers.create_pool_if_not_exist(pool, self.batch_client)

        # Create job
        job = batch_models.JobAddParameter(
            id=job_id,
            pool_info=batch_models.PoolInformation(pool_id=pool_id))

        # Add job to batch
        self.batch_client.job.add(job)

        return helpers.get_cluster(cluster_conf.cluster_id, self.batch_client)

    def __get_pool_details(self, cluster_id: str):
        """
            Print the information for the given cluster
            :param cluster_id: Id of the cluster
            :return pool: CloudPool, nodes: ComputeNodePaged
        """
        pool = self.batch_client.pool.get(cluster_id)
        nodes = self.batch_client.compute_node.list(pool_id=cluster_id)
        return pool, nodes

    def __list_clusters(self, software_metadata_key):
        """
            List all the cluster on your account.
        """
        pools = self.batch_client.pool.list()
        software_metadata = (
            constants.AZTK_SOFTWARE_METADATA_KEY, software_metadata_key)
        cluster_metadata = (
            constants.AZTK_MODE_METADATA_KEY, constants.AZTK_CLUSTER_MODE_METADATA)

        aztk_pools = []
        for pool in [pool for pool in pools if pool.metadata]:
            pool_metadata = [(metadata.name, metadata.value) for metadata in pool.metadata]
            if all([metadata in pool_metadata for metadata in [software_metadata, cluster_metadata]]):
                aztk_pools.append(pool)
        return aztk_pools

    def __create_user(self, pool_id: str, node_id: str, username: str, password: str = None, ssh_key: str = None) -> str:
        """
            Create a pool user
            :param pool: the pool to add the user to
            :param node: the node to add the user to
            :param username: username of the user to add
            :param password: password of the user to add
            :param ssh_key: ssh_key of the user to add
        """
        # Create new ssh user for the master node
        self.batch_client.compute_node.add_user(
            pool_id,
            node_id,
            batch_models.ComputeNodeUser(
                name=username,
                is_admin=True,
                password=password,
                ssh_public_key=get_ssh_key.get_user_public_key(
                    ssh_key, self.secrets_config),
                expiry_time=datetime.now(timezone.utc) + timedelta(days=365)))

    def __delete_user(self, pool_id: str, node_id: str, username: str) -> str:
        """
            Create a pool user
            :param pool: the pool to add the user to
            :param node: the node to add the user to
            :param username: username of the user to add
        """
        # Delete a user on the given node
        self.batch_client.compute_node.delete_user(pool_id, node_id, username)


    def __get_remote_login_settings(self, pool_id: str, node_id: str):
        """
        Get the remote_login_settings for node
        :param pool_id
        :param node_id
        :returns aztk.models.RemoteLogin
        """
        result = self.batch_client.compute_node.get_remote_login_settings(
            pool_id, node_id)
        return models.RemoteLogin(ip_address=result.remote_login_ip_address, port=str(result.remote_login_port))

    def __create_user_on_node(self, username, pool_id, node_id, ssh_key):
        try:
            self.__create_user(pool_id=pool_id, node_id=node_id, username=username, ssh_key=ssh_key)
        except batch_error.BatchErrorException as error:
            try:
                self.__delete_user(pool_id, node_id, username)
                self.__create_user(pool_id=pool_id, node_id=node_id, username=username, ssh_key=ssh_key)
            except batch_error.BatchErrorException as error:
                print(error)
                raise error
        return ssh_key

    def __create_user_on_pool(self, username, pool_id, nodes):
        ssh_key = RSA.generate(2048)
        ssh_pub_key = ssh_key.publickey().exportKey('OpenSSH').decode('utf-8')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.__create_user_on_node,
                                       username,
                                       pool_id,
                                       node.id,
                                       ssh_pub_key): node for node in nodes}
            concurrent.futures.wait(futures)
        return ssh_key

    def __delete_user_on_pool(self, username, pool_id, nodes):
        with concurrent.futures.ThreadPoolExecutor() as exector:
            futures = [exector.submit(self.__delete_user, pool_id, node.id, username) for node in nodes]
            concurrent.futures.wait(futures)


    def __cluster_run(self, cluster_id, command, internal, container_name=None, timeout=None):
        pool, nodes = self.__get_pool_details(cluster_id)
        nodes = [node for node in nodes]
        if internal:
            cluster_nodes = [(node, models.RemoteLogin(ip_address=node.ip_address, port="22")) for node in nodes]
        else:
            cluster_nodes = [(node, self.__get_remote_login_settings(pool.id, node.id)) for node in nodes]
        try:
            ssh_key = self.__create_user_on_pool('aztk', pool.id, nodes)
            output = asyncio.get_event_loop().run_until_complete(ssh_lib.clus_exec_command(command,
                                                                                           'aztk',
                                                                                           cluster_nodes,
                                                                                           ssh_key=ssh_key.exportKey().decode('utf-8'),
                                                                                           container_name=container_name,
                                                                                           timeout=timeout))
            return output
        except OSError as exc:
            raise exc
        finally:
            self.__delete_user_on_pool('aztk', pool.id, nodes)

    def __cluster_copy(self, cluster_id, source_path, destination_path, container_name=None, internal=False, get=False, timeout=None):
        pool, nodes = self.__get_pool_details(cluster_id)
        nodes = [node for node in nodes]
        if internal:
            cluster_nodes = [(node, models.RemoteLogin(ip_address=node.ip_address, port="22")) for node in nodes]
        else:
            cluster_nodes = [(node, self.__get_remote_login_settings(pool.id, node.id)) for node in nodes]
        try:
            ssh_key = self.__create_user_on_pool('aztk', pool.id, nodes)
            output = asyncio.get_event_loop().run_until_complete(
                ssh_lib.clus_copy(container_name=container_name,
                                  username='aztk',
                                  nodes=cluster_nodes,
                                  source_path=source_path,
                                  destination_path=destination_path,
                                  ssh_key=ssh_key.exportKey().decode('utf-8'),
                                  get=get,
                                  timeout=timeout))
            return output
        except (OSError, batch_error.BatchErrorException) as exc:
            raise exc
        finally:
            self.__delete_user_on_pool('aztk', pool.id, nodes)

    def __submit_job(self,
                     job_configuration,
                     start_task,
                     job_manager_task,
                     autoscale_formula,
                     software_metadata_key: str,
                     vm_image_model,
                     application_metadata):
        """
            Job Submission
            :param job_configuration -> aztk_sdk.spark.models.JobConfiguration
            :param start_task -> batch_models.StartTask
            :param job_manager_task -> batch_models.TaskAddParameter
            :param autoscale forumula -> str
            :param software_metadata_key -> str
            :param vm_image_model -> aztk_sdk.models.VmImage
            :returns None
        """
        self._get_cluster_data(job_configuration.id).save_cluster_config(job_configuration.to_cluster_config())

        # get a verified node agent sku
        sku_to_use, image_ref_to_use = \
            helpers.select_latest_verified_vm_image_with_node_agent_sku(
                vm_image_model.publisher, vm_image_model.offer, vm_image_model.sku, self.batch_client)

        # set up subnet if necessary
        network_conf = None
        if job_configuration.subnet_id:
            network_conf = batch_models.NetworkConfiguration(
                subnet_id=job_configuration.subnet_id)

        # set up a schedule for a recurring job
        auto_pool_specification = batch_models.AutoPoolSpecification(
            pool_lifetime_option=batch_models.PoolLifetimeOption.job_schedule,
            auto_pool_id_prefix=job_configuration.id,
            keep_alive=False,
            pool=batch_models.PoolSpecification(
                display_name=job_configuration.id,
                virtual_machine_configuration=batch_models.VirtualMachineConfiguration(
                    image_reference=image_ref_to_use,
                    node_agent_sku_id=sku_to_use),
                vm_size=job_configuration.vm_size,
                enable_auto_scale=True,
                auto_scale_formula=autoscale_formula,
                auto_scale_evaluation_interval=timedelta(minutes=5),
                start_task=start_task,
                enable_inter_node_communication=not job_configuration.mixed_mode(),
                network_configuration=network_conf,
                max_tasks_per_node=1,
                metadata=[
                    batch_models.MetadataItem(
                        name=constants.AZTK_SOFTWARE_METADATA_KEY, value=software_metadata_key),
                    batch_models.MetadataItem(
                        name=constants.AZTK_MODE_METADATA_KEY, value=constants.AZTK_JOB_MODE_METADATA)
                ]
            )
        )

        # define job specification
        job_spec = batch_models.JobSpecification(
            pool_info=batch_models.PoolInformation(auto_pool_specification=auto_pool_specification),
            display_name=job_configuration.id,
            on_all_tasks_complete=batch_models.OnAllTasksComplete.terminate_job,
            job_manager_task=job_manager_task,
            metadata=[
                batch_models.MetadataItem(
                    name='applications', value=application_metadata)
            ]
        )

        # define schedule
        schedule = batch_models.Schedule(
            do_not_run_until=None,
            do_not_run_after=None,
            start_window=None,
            recurrence_interval=None
        )

        # create job schedule and add task
        setup = batch_models.JobScheduleAddParameter(
            id=job_configuration.id,
            schedule=schedule,
            job_specification=job_spec)

        self.batch_client.job_schedule.add(setup)

        return self.batch_client.job_schedule.get(job_schedule_id=job_configuration.id)


    '''
    Define Public Interface
    '''

    def create_cluster(self, cluster_conf, wait: bool = False):
        raise NotImplementedError()

    def create_clusters_in_parallel(self, cluster_confs):
        raise NotImplementedError()

    def delete_cluster(self, cluster_id: str):
        raise NotImplementedError()

    def get_cluster(self, cluster_id: str):
        raise NotImplementedError()

    def list_clusters(self):
        raise NotImplementedError()

    def wait_until_cluster_is_ready(self, cluster_id):
        raise NotImplementedError()

    def create_user(self, cluster_id: str, username: str, password: str = None, ssh_key: str = None) -> str:
        raise NotImplementedError()

    def get_remote_login_settings(self, cluster_id, node_id):
        raise NotImplementedError()

    def cluster_run(self, cluster_id, command):
        raise NotImplementedError()

    def cluster_copy(self, cluster_id, source_path, destination_path):
        raise NotImplementedError()

    def cluster_download(self, cluster_id, source_path, destination_path):
        raise NotImplementedError()

    def submit_job(self, job):
        raise NotImplementedError()
