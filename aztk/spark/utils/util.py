from __future__ import print_function

import datetime
import time

import azure.batch.models as batch_models

from aztk.utils import constants


class MasterInvalidStateError(Exception):
    pass


def wait_for_master_to_be_ready(core_operations, spark_operations, cluster_id: str):

    master_node_id = None
    start_time = datetime.datetime.now()
    while True:
        if not master_node_id:
            master_node_id = spark_operations.get(cluster_id).master_node_id
            if not master_node_id:
                time.sleep(5)
                continue

        master_node = core_operations.batch_client.compute_node.get(cluster_id, master_node_id)

        if master_node.state in [batch_models.ComputeNodeState.idle, batch_models.ComputeNodeState.running]:
            break
        elif master_node.state is batch_models.ComputeNodeState.start_task_failed:
            raise MasterInvalidStateError("Start task failed on master")
        elif master_node.state in [batch_models.ComputeNodeState.unknown, batch_models.ComputeNodeState.unusable]:
            raise MasterInvalidStateError("Master is in an invalid state")
        else:
            now = datetime.datetime.now()

            delta = now - start_time
            if delta.total_seconds() > constants.WAIT_FOR_MASTER_TIMEOUT:
                raise MasterInvalidStateError("Master didn't become ready before timeout.")

            time.sleep(10)
