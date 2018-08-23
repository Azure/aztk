import time

import azure.batch.models as batch_models

from aztk.error import AztkError


def wait_for_all_nodes(spark_client, id, nodes):
    start_time = time.time()
    while (time.time() - start_time) < 300:
        print("{} : running wait for all nodes check node states".format(time.time() - start_time))
        if any([
                node.state in [batch_models.ComputeNodeState.unusable, batch_models.ComputeNodeState.start_task_failed]
                for node in nodes
        ]):
            raise AztkError("A node is unusable or had its start task fail.")
        if any([
                node.state not in [batch_models.ComputeNodeState.idle, batch_models.ComputeNodeState.running]
                for node in nodes
        ]):
            nodes = spark_client.cluster.get(id).nodes
            print("Not all nodes idle or running.")
        else:
            break
