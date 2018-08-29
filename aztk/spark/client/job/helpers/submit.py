import azure.batch.models as batch_models
import azure.batch.models.batch_error as batch_error
import yaml

from aztk import error
from aztk import models as base_models
from aztk.internal.cluster_data import NodeData
from aztk.spark import models
from aztk.utils import helpers
from aztk.utils.command_builder import CommandBuilder


def __app_cmd():
    docker_exec = CommandBuilder("sudo docker exec")
    docker_exec.add_argument("-i")
    docker_exec.add_option("-e", "AZ_BATCH_TASK_WORKING_DIR=$AZ_BATCH_TASK_WORKING_DIR")
    docker_exec.add_option("-e", "AZ_BATCH_JOB_ID=$AZ_BATCH_JOB_ID")
    docker_exec.add_argument(
        r'spark /bin/bash >> output.log 2>&1 -c "'
        r"source ~/.bashrc; "
        r"export PYTHONPATH=$PYTHONPATH:\$AZTK_WORKING_DIR; "
        r"cd \$AZ_BATCH_TASK_WORKING_DIR; "
        r'\$AZTK_WORKING_DIR/.aztk-env/.venv/bin/python \$AZTK_WORKING_DIR/aztk/node_scripts/job_submission.py"')
    return docker_exec.to_str()


def generate_job_manager_task(core_job_operations, job, application_tasks):
    resource_files = []
    for application, task in application_tasks:
        task_definition_resource_file = helpers.upload_text_to_container(
            container_name=job.id,
            application_name=application.name + ".yaml",
            file_path=application.name + ".yaml",
            content=yaml.dump(task),
            blob_client=core_job_operations.blob_client,
        )
        resource_files.append(task_definition_resource_file)

    task_cmd = __app_cmd()

    # Create task
    task = batch_models.JobManagerTask(
        id=job.id,
        command_line=helpers.wrap_commands_in_shell([task_cmd]),
        resource_files=resource_files,
        kill_job_on_completion=False,
        allow_low_priority_node=True,
        user_identity=batch_models.UserIdentity(
            auto_user=batch_models.AutoUserSpecification(
                scope=batch_models.AutoUserScope.task, elevation_level=batch_models.ElevationLevel.admin)),
    )

    return task


# def _default_scheduling_target(vm_count: int):
#     if vm_count == 0:
#         return models.SchedulingTarget.Any
#     else:
#         return models.SchedulingTarget.Dedicated


def _apply_default_for_job_config(job_conf: models.JobConfiguration):
    # if job_conf.scheduling_target is None:
    #     job_conf.scheduling_target = _default_scheduling_target(job_conf.max_dedicated_nodes)

    return job_conf


def submit_job(core_job_operations,
               spark_job_operations,
               job_configuration: models.JobConfiguration,
               wait: bool = False):
    try:
        job_configuration = _apply_default_for_job_config(job_configuration)
        job_configuration.validate()
        cluster_data = core_job_operations.get_cluster_data(job_configuration.id)
        node_data = NodeData(job_configuration.to_cluster_config()).add_core().done()
        zip_resource_files = cluster_data.upload_node_data(node_data).to_resource_file()

        start_task = spark_job_operations._generate_cluster_start_task(
            core_job_operations,
            zip_resource_files,
            job_configuration.id,
            job_configuration.gpu_enabled,
            job_configuration.get_docker_repo(),
            job_configuration.get_docker_run_options(),
            mixed_mode=job_configuration.mixed_mode(),
            worker_on_master=job_configuration.worker_on_master,
        )

        application_tasks = []
        for application in job_configuration.applications:
            application_tasks.append((
                application,
                spark_job_operations._generate_application_task(core_job_operations, job_configuration.id, application),
            ))

        job_manager_task = generate_job_manager_task(core_job_operations, job_configuration, application_tasks)

        software_metadata_key = base_models.Software.spark

        vm_image = models.VmImage(publisher="Canonical", offer="UbuntuServer", sku="16.04")

        autoscale_formula = "$TargetDedicatedNodes = {0}; " "$TargetLowPriorityNodes = {1}".format(
            job_configuration.max_dedicated_nodes, job_configuration.max_low_pri_nodes)

        job = core_job_operations.submit(
            job_configuration=job_configuration,
            start_task=start_task,
            job_manager_task=job_manager_task,
            autoscale_formula=autoscale_formula,
            software_metadata_key=software_metadata_key,
            vm_image_model=vm_image,
            application_metadata="\n".join(application.name for application in (job_configuration.applications or [])),
        )

        if wait:
            spark_job_operations.wait(id=job_configuration.id)

        return models.Job(job)

    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
