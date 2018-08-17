import os

import azure.batch.models as batch_models
import yaml

from core import config
from install.pick_master import get_master_node_id


def affinitize_task_to_master(batch_client, cluster_id, task):
    pool = batch_client.pool.get(config.pool_id)
    master_node_id = get_master_node_id(pool)
    master_node = batch_client.compute_node.get(pool_id=cluster_id, node_id=master_node_id)
    task.affinity_info = batch_models.AffinityInformation(affinity_id=master_node.affinity_id)
    return task


def schedule_tasks(tasks_path):
    """
        Handle the request to submit a task
    """
    batch_client = config.batch_client

    for task_definition in tasks_path:
        with open(task_definition, "r", encoding="UTF-8") as stream:
            try:
                task = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        # affinitize task to master
        task = affinitize_task_to_master(batch_client, os.environ["AZ_BATCH_POOL_ID"], task)
        # schedule the task
        batch_client.task.add(job_id=os.environ["AZ_BATCH_JOB_ID"], task=task)


if __name__ == "__main__":
    tasks_path = []
    for file in os.listdir(os.environ["AZ_BATCH_TASK_WORKING_DIR"]):
        if file.endswith(".yaml"):
            tasks_path.append(os.path.join(os.environ["AZ_BATCH_TASK_WORKING_DIR"], file))

    schedule_tasks(tasks_path)
