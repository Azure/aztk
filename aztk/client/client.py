import asyncio
import concurrent.futures
from datetime import datetime, timedelta, timezone

import azure.batch.models as batch_models
import azure.batch.models.batch_error as batch_error
from Cryptodome.PublicKey import RSA

import aztk.error as error
import aztk.models as models
import aztk.utils.azure_api as azure_api
import aztk.utils.constants as constants
import aztk.utils.get_ssh_key as get_ssh_key
import aztk.utils.helpers as helpers
import aztk.utils.ssh as ssh_lib
from aztk.internal import cluster_data
from aztk.utils import deprecated, secure_utils


class CoreClient:
    """The base AZTK client that all other clients inherit from.

    **This client should not be used directly. Only software specific clients
    should be used.**

    """

    def __init__(self):
        self.secrets_configuration = None
        self.batch_client = None
        self.blob_client = None

    def _get_context(self, secrets_configuration: models.SecretsConfiguration):
        self.secrets_configuration = secrets_configuration

        azure_api.validate_secrets(secrets_configuration)
        self.batch_client = azure_api.make_batch_client(secrets_configuration)
        self.blob_client = azure_api.make_blob_client(secrets_configuration)
        context = {
            "batch_client": self.batch_client,
            "blob_client": self.blob_client,
            "secrets_configuration": self.secrets_configuration,
        }
        return context

    # ALL THE FOLLOWING METHODS ARE DEPRECATED AND WILL BE REMOVED IN 0.10.0
    @deprecated("0.10.0")
    def get_cluster_config(self, cluster_id: str) -> models.ClusterConfiguration:
        return self._get_cluster_data(cluster_id).read_cluster_config()

    @deprecated("0.10.0")
    def _get_cluster_data(self, cluster_id: str) -> cluster_data.ClusterData:
        """
        Returns ClusterData object to manage data related to the given cluster id
        """
        return cluster_data.ClusterData(self.blob_client, cluster_id)

    """
    General Batch Operations
    """

    @deprecated("0.10.0")
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

    @deprecated("0.10.0")
    def __create_pool_and_job(self, cluster_conf: models.ClusterConfiguration, software_metadata_key: str, start_task,
                              VmImageModel):
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
        sku_to_use, image_ref_to_use = helpers.select_latest_verified_vm_image_with_node_agent_sku(
            VmImageModel.publisher, VmImageModel.offer, VmImageModel.sku, self.batch_client)

        network_conf = None
        if cluster_conf.subnet_id is not None:
            network_conf = batch_models.NetworkConfiguration(subnet_id=cluster_conf.subnet_id)
        auto_scale_formula = "$TargetDedicatedNodes={0}; $TargetLowPriorityNodes={1}".format(
            cluster_conf.size, cluster_conf.size_low_priority)

        # Configure the pool
        pool = batch_models.PoolAddParameter(
            id=pool_id,
            virtual_machine_configuration=batch_models.VirtualMachineConfiguration(
                image_reference=image_ref_to_use, node_agent_sku_id=sku_to_use),
            vm_size=cluster_conf.vm_size,
            enable_auto_scale=True,
            auto_scale_formula=auto_scale_formula,
            auto_scale_evaluation_interval=timedelta(minutes=5),
            start_task=start_task,
            enable_inter_node_communication=True if not cluster_conf.subnet_id else False,
            max_tasks_per_node=4,
            network_configuration=network_conf,
            metadata=[
                batch_models.MetadataItem(name=constants.AZTK_SOFTWARE_METADATA_KEY, value=software_metadata_key),
                batch_models.MetadataItem(
                    name=constants.AZTK_MODE_METADATA_KEY, value=constants.AZTK_CLUSTER_MODE_METADATA),
            ],
        )

        # Create the pool + create user for the pool
        helpers.create_pool_if_not_exist(pool, self.batch_client)

        # Create job
        job = batch_models.JobAddParameter(id=job_id, pool_info=batch_models.PoolInformation(pool_id=pool_id))

        # Add job to batch
        self.batch_client.job.add(job)

        return helpers.get_cluster(cluster_conf.cluster_id, self.batch_client)

    @deprecated("0.10.0")
    def __get_pool_details(self, cluster_id: str):
        """
            Print the information for the given cluster
            :param cluster_id: Id of the cluster
            :return pool: CloudPool, nodes: ComputeNodePaged
        """
        pool = self.batch_client.pool.get(cluster_id)
        nodes = self.batch_client.compute_node.list(pool_id=cluster_id)
        return pool, nodes

    @deprecated("0.10.0")
    def __list_clusters(self, software_metadata_key):
        """
            List all the cluster on your account.
        """
        pools = self.batch_client.pool.list()
        software_metadata = (constants.AZTK_SOFTWARE_METADATA_KEY, software_metadata_key)
        cluster_metadata = (constants.AZTK_MODE_METADATA_KEY, constants.AZTK_CLUSTER_MODE_METADATA)

        aztk_pools = []
        for pool in [pool for pool in pools if pool.metadata]:
            pool_metadata = [(metadata.name, metadata.value) for metadata in pool.metadata]
            if all([metadata in pool_metadata for metadata in [software_metadata, cluster_metadata]]):
                aztk_pools.append(pool)
        return aztk_pools

    @deprecated("0.10.0")
    def __create_user(self, pool_id: str, node_id: str, username: str, password: str = None,
                      ssh_key: str = None) -> str:
        """
            Create a pool user
            :param pool: the pool to add the user to
            :param node: the node to add the user to
            :param username: username of the user to add
            :param password: password of the user to add
            :param ssh_key: ssh_key of the user to add
        """
        # Create new ssh user for the given node
        self.batch_client.compute_node.add_user(
            pool_id,
            node_id,
            batch_models.ComputeNodeUser(
                name=username,
                is_admin=True,
                password=password,
                ssh_public_key=get_ssh_key.get_user_public_key(ssh_key, self.secrets_configuration),
                expiry_time=datetime.now(timezone.utc) + timedelta(days=365),
            ),
        )

    @deprecated("0.10.0")
    def __delete_user(self, pool_id: str, node_id: str, username: str) -> str:
        """
            Create a pool user
            :param pool: the pool to add the user to
            :param node: the node to add the user to
            :param username: username of the user to add
        """
        # Delete a user on the given node
        self.batch_client.compute_node.delete_user(pool_id, node_id, username)

    @deprecated("0.10.0")
    def __get_remote_login_settings(self, pool_id: str, node_id: str):
        """
        Get the remote_login_settings for node
        :param pool_id
        :param node_id
        :returns aztk.models.RemoteLogin
        """
        result = self.batch_client.compute_node.get_remote_login_settings(pool_id, node_id)
        return models.RemoteLogin(ip_address=result.remote_login_ip_address, port=str(result.remote_login_port))

    @deprecated("0.10.0")
    def __create_user_on_node(self, username, pool_id, node_id, ssh_key=None, password=None):
        try:
            self.__create_user(pool_id=pool_id, node_id=node_id, username=username, ssh_key=ssh_key, password=password)
        except batch_error.BatchErrorException as error:
            try:
                self.__delete_user(pool_id, node_id, username)
                self.__create_user(pool_id=pool_id, node_id=node_id, username=username, ssh_key=ssh_key)
            except batch_error.BatchErrorException as error:
                raise error

    @deprecated("0.10.0")
    def __generate_user_on_node(self, pool_id, node_id):
        generated_username = secure_utils.generate_random_string()
        ssh_key = RSA.generate(2048)
        ssh_pub_key = ssh_key.publickey().exportKey("OpenSSH").decode("utf-8")
        self.__create_user_on_node(generated_username, pool_id, node_id, ssh_pub_key)
        return generated_username, ssh_key

    @deprecated("0.10.0")
    def __generate_user_on_pool(self, pool_id, nodes):
        generated_username = secure_utils.generate_random_string()
        ssh_key = RSA.generate(2048)
        ssh_pub_key = ssh_key.publickey().exportKey("OpenSSH").decode("utf-8")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.__create_user_on_node, generated_username, pool_id, node.id, ssh_pub_key): node
                for node in nodes
            }
            concurrent.futures.wait(futures)

        return generated_username, ssh_key

    @deprecated("0.10.0")
    def __create_user_on_pool(self, username, pool_id, nodes, ssh_pub_key=None, password=None):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.__create_user_on_node, username, pool_id, node.id, ssh_pub_key, password): node
                for node in nodes
            }
            concurrent.futures.wait(futures)

    @deprecated("0.10.0")
    def __delete_user_on_pool(self, username, pool_id, nodes):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.__delete_user, pool_id, node.id, username) for node in nodes]
            concurrent.futures.wait(futures)

    @deprecated("0.10.0")
    def __node_run(self, cluster_id, node_id, command, internal, container_name=None, timeout=None):
        pool, nodes = self.__get_pool_details(cluster_id)
        try:
            node = next(node for node in nodes if node.id == node_id)
        except StopIteration:
            raise error.AztkError("Node with id {} not found".format(node_id))

        if internal:
            node_rls = models.RemoteLogin(ip_address=node.ip_address, port="22")
        else:
            node_rls = self.__get_remote_login_settings(pool.id, node.id)

        try:
            generated_username, ssh_key = self.__generate_user_on_node(pool.id, node.id)
            output = ssh_lib.node_exec_command(
                node.id,
                command,
                generated_username,
                node_rls.ip_address,
                node_rls.port,
                ssh_key=ssh_key.exportKey().decode("utf-8"),
                container_name=container_name,
                timeout=timeout,
            )
            return output
        finally:
            self.__delete_user(cluster_id, node.id, generated_username)

    @deprecated("0.10.0")
    def __cluster_run(self, cluster_id, command, internal, container_name=None, timeout=None):
        pool, nodes = self.__get_pool_details(cluster_id)
        nodes = list(nodes)
        if internal:
            cluster_nodes = [(node, models.RemoteLogin(ip_address=node.ip_address, port="22")) for node in nodes]
        else:
            cluster_nodes = [(node, self.__get_remote_login_settings(pool.id, node.id)) for node in nodes]

        try:
            generated_username, ssh_key = self.__generate_user_on_pool(pool.id, nodes)
            output = asyncio.get_event_loop().run_until_complete(
                ssh_lib.clus_exec_command(
                    command,
                    generated_username,
                    cluster_nodes,
                    ssh_key=ssh_key.exportKey().decode("utf-8"),
                    container_name=container_name,
                    timeout=timeout,
                ))
            return output
        except OSError as exc:
            raise exc
        finally:
            self.__delete_user_on_pool(generated_username, pool.id, nodes)

    @deprecated("0.10.0")
    def __cluster_copy(
            self,
            cluster_id,
            source_path,
            destination_path=None,
            container_name=None,
            internal=False,
            get=False,
            timeout=None,
    ):
        pool, nodes = self.__get_pool_details(cluster_id)
        nodes = list(nodes)
        if internal:
            cluster_nodes = [(node, models.RemoteLogin(ip_address=node.ip_address, port="22")) for node in nodes]
        else:
            cluster_nodes = [(node, self.__get_remote_login_settings(pool.id, node.id)) for node in nodes]

        try:
            generated_username, ssh_key = self.__generate_user_on_pool(pool.id, nodes)
            output = asyncio.get_event_loop().run_until_complete(
                ssh_lib.clus_copy(
                    container_name=container_name,
                    username=generated_username,
                    nodes=cluster_nodes,
                    source_path=source_path,
                    destination_path=destination_path,
                    ssh_key=ssh_key.exportKey().decode("utf-8"),
                    get=get,
                    timeout=timeout,
                ))
            return output
        except (OSError, batch_error.BatchErrorException) as exc:
            raise exc
        finally:
            self.__delete_user_on_pool(generated_username, pool.id, nodes)

    @deprecated("0.10.0")
    def __ssh_into_node(self,
                        pool_id,
                        node_id,
                        username,
                        ssh_key=None,
                        password=None,
                        port_forward_list=None,
                        internal=False):
        if internal:
            result = self.batch_client.compute_node.get(pool_id=pool_id, node_id=node_id)
            rls = models.RemoteLogin(ip_address=result.ip_address, port="22")
        else:
            result = self.batch_client.compute_node.get_remote_login_settings(pool_id, node_id)
            rls = models.RemoteLogin(ip_address=result.remote_login_ip_address, port=str(result.remote_login_port))

        ssh_lib.node_ssh(
            username=username,
            hostname=rls.ip_address,
            port=rls.port,
            ssh_key=ssh_key,
            password=password,
            port_forward_list=port_forward_list,
        )

    @deprecated("0.10.0")
    def __submit_job(
            self,
            job_configuration,
            start_task,
            job_manager_task,
            autoscale_formula,
            software_metadata_key: str,
            vm_image_model,
            application_metadata,
    ):
        """
            Job Submission
            :param job_configuration -> aztk_sdk.spark.models.JobConfiguration
            :param start_task -> batch_models.StartTask
            :param job_manager_task -> batch_models.TaskAddParameter
            :param autoscale_formula -> str
            :param software_metadata_key -> str
            :param vm_image_model -> aztk_sdk.models.VmImage
            :returns None
        """
        self._get_cluster_data(job_configuration.id).save_cluster_config(job_configuration.to_cluster_config())

        # get a verified node agent sku
        sku_to_use, image_ref_to_use = helpers.select_latest_verified_vm_image_with_node_agent_sku(
            vm_image_model.publisher, vm_image_model.offer, vm_image_model.sku, self.batch_client)

        # set up subnet if necessary
        network_conf = None
        if job_configuration.subnet_id:
            network_conf = batch_models.NetworkConfiguration(subnet_id=job_configuration.subnet_id)

        # set up a schedule for a recurring job
        auto_pool_specification = batch_models.AutoPoolSpecification(
            pool_lifetime_option=batch_models.PoolLifetimeOption.job_schedule,
            auto_pool_id_prefix=job_configuration.id,
            keep_alive=False,
            pool=batch_models.PoolSpecification(
                display_name=job_configuration.id,
                virtual_machine_configuration=batch_models.VirtualMachineConfiguration(
                    image_reference=image_ref_to_use, node_agent_sku_id=sku_to_use),
                vm_size=job_configuration.vm_size,
                enable_auto_scale=True,
                auto_scale_formula=autoscale_formula,
                auto_scale_evaluation_interval=timedelta(minutes=5),
                start_task=start_task,
                enable_inter_node_communication=not job_configuration.mixed_mode(),
                network_configuration=network_conf,
                max_tasks_per_node=4,
                metadata=[
                    batch_models.MetadataItem(name=constants.AZTK_SOFTWARE_METADATA_KEY, value=software_metadata_key),
                    batch_models.MetadataItem(
                        name=constants.AZTK_MODE_METADATA_KEY, value=constants.AZTK_JOB_MODE_METADATA),
                ],
            ),
        )

        # define job specification
        job_spec = batch_models.JobSpecification(
            pool_info=batch_models.PoolInformation(auto_pool_specification=auto_pool_specification),
            display_name=job_configuration.id,
            on_all_tasks_complete=batch_models.OnAllTasksComplete.terminate_job,
            job_manager_task=job_manager_task,
            metadata=[batch_models.MetadataItem(name="applications", value=application_metadata)],
        )

        # define schedule
        schedule = batch_models.Schedule(
            do_not_run_until=None, do_not_run_after=None, start_window=None, recurrence_interval=None)

        # create job schedule and add task
        setup = batch_models.JobScheduleAddParameter(
            id=job_configuration.id, schedule=schedule, job_specification=job_spec)

        self.batch_client.job_schedule.add(setup)

        return self.batch_client.job_schedule.get(job_schedule_id=job_configuration.id)
