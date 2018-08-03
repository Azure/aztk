def get_recent_job(core_job_operations, job_id):
    job_schedule = core_job_operations.batch_client.job_schedule.get(job_id)
    return core_job_operations.batch_client.job.get(job_schedule.execution_info.recent_job.id)
