import time

import azure.batch.models as batch_models

from aztk.error import AztkError


def wait_for_all_nodes(spark_client, id, nodes):
    nodes = [node for node in nodes]
    start_time = time.time()
    while (time.time() - start_time) < 300:
        if any([
                node.state in [batch_models.ComputeNodeState.unusable, batch_models.ComputeNodeState.start_task_failed]
                for node in nodes
        ]):
            raise AztkError("A node is unusable or had its start task fail.")

        if not all(node.state in [batch_models.ComputeNodeState.idle, batch_models.ComputeNodeState.running]
                   for node in nodes):
            nodes = [node for node in spark_client.cluster.get(id).nodes]
            time.sleep(1)
        else:
            break
