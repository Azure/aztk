import time

import azure.batch.models as batch_models


def wait_for_task_to_complete(core_cluster_operations, job_id: str, task_id: str):
    while True:
        task = core_cluster_operations.batch_client.task.get(job_id=job_id, task_id=task_id)
        if task.state != batch_models.TaskState.completed:
            time.sleep(2)
        else:
            return
