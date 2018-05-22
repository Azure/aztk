from __future__ import print_function
import datetime
import io
import os
import time
import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth
import azure.batch.models as batch_models
import azure.storage.blob as blob
from aztk.version import __version__
from aztk.utils import constants
from aztk import error
import aztk.models


class MasterInvalidStateError(Exception):
    pass


def wait_for_master_to_be_ready(client, cluster_id: str):

    master_node_id = None
    start_time = datetime.datetime.now()
    while True:
        if not master_node_id:
            master_node_id = client.get_cluster(cluster_id).master_node_id
            if not master_node_id:
                time.sleep(5)
                continue

        master_node = client.batch_client.compute_node.get(cluster_id, master_node_id)

        if master_node.state in [batch_models.ComputeNodeState.idle,  batch_models.ComputeNodeState.running]:
            break
        elif master_node.state is batch_models.ComputeNodeState.start_task_failed:
            raise MasterInvalidStateError("Start task failed on master")
        elif master_node.state in [batch_models.ComputeNodeState.unknown, batch_models.ComputeNodeState.unusable]:
            raise MasterInvalidStateError("Master is in an invalid state")
        else:
            now = datetime.datetime.now()

            delta = now - start_time
            if delta.total_seconds() > constants.WAIT_FOR_MASTER_TIMEOUT:
                raise MasterInvalidStateError(
                    "Master didn't become ready before timeout.")

            time.sleep(10)
