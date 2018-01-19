import sys
import os
import yaml
import subprocess
import datetime
from typing import List
import azure.storage.blob as blob
import azure.batch.models as batch_models
from command_builder import CommandBuilder
from core import config


def schedule_tasks(tasks_path):
    '''
        Handle the request to submit a task
    '''
    batch_client = config.batch_client
    blob_client = config.blob_client
    
    for task_definition in tasks_path:
        with open(task_definition, 'r') as stream:
            try:
                task = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        # schedule the task
        batch_client.task.add(job_id=os.environ['AZ_BATCH_JOB_ID'], task=task)


if __name__ == "__main__":
    tasks_path = []
    for file in os.listdir(os.environ['AZ_BATCH_TASK_WORKING_DIR']):
        if file.endswith(".yaml"):
            tasks_path.append(os.path.join(os.environ['AZ_BATCH_TASK_WORKING_DIR'], file))

    schedule_tasks(tasks_path)
