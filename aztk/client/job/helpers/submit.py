from datetime import timedelta

import azure.batch.models as batch_models

from aztk.utils import constants, helpers


def submit_job(
        job_client,
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
    job_client.get_cluster_data(job_configuration.id).save_cluster_config(job_configuration.to_cluster_config())

    # get a verified node agent sku
    sku_to_use, image_ref_to_use = helpers.select_latest_verified_vm_image_with_node_agent_sku(
        vm_image_model.publisher, vm_image_model.offer, vm_image_model.sku, job_client.batch_client)

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
    setup = batch_models.JobScheduleAddParameter(id=job_configuration.id, schedule=schedule, job_specification=job_spec)

    job_client.batch_client.job_schedule.add(setup)

    return job_client.batch_client.job_schedule.get(job_schedule_id=job_configuration.id)
