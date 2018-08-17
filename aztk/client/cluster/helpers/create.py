from datetime import timedelta
import azure.batch.models as batch_models

from aztk import models
from aztk.utils import helpers, constants


def create_pool_and_job(
        core_cluster_operations,
        cluster_conf: models.ClusterConfiguration,
        software_metadata_key: str,
        start_task,
        VmImageModel,
):
    """
        Create a pool and job
        :param cluster_conf: the configuration object used to create the cluster
        :type cluster_conf: aztk.models.ClusterConfiguration
        :parm software_metadata_key: the id of the software being used on the cluster
        :param start_task: the start task for the cluster
        :param VmImageModel: the type of image to provision for the cluster
        :param wait: wait until the cluster is ready
    """
    core_cluster_operations.get_cluster_data(cluster_conf.cluster_id).save_cluster_config(cluster_conf)
    # reuse pool_id as job_id
    pool_id = cluster_conf.cluster_id
    job_id = cluster_conf.cluster_id

    # Get a verified node agent sku
    sku_to_use, image_ref_to_use = helpers.select_latest_verified_vm_image_with_node_agent_sku(
        VmImageModel.publisher, VmImageModel.offer, VmImageModel.sku, core_cluster_operations.batch_client)

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
    helpers.create_pool_if_not_exist(pool, core_cluster_operations.batch_client)

    # Create job
    job = batch_models.JobAddParameter(id=job_id, pool_info=batch_models.PoolInformation(pool_id=pool_id))

    # Add job to batch
    core_cluster_operations.batch_client.job.add(job)

    return helpers.get_cluster(cluster_conf.cluster_id, core_cluster_operations.batch_client)
