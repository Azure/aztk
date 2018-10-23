from azure.batch.models import BatchErrorException


def stop_app(core_job_operations, job_id, application_name):
    recent_run_job = core_job_operations.get_recent_job(job_id)

    # stop batch task
    try:
        core_job_operations.batch_client.task.terminate(job_id=recent_run_job.id, task_id=application_name)
        return True
    except BatchErrorException:
        return False
