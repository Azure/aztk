import azure.batch.models as batch_models
from azure.batch.models import BatchErrorException

from aztk.error import AztkError


def clean_up_cluster(spark_client, id):
    try:
        cluster = spark_client.cluster.get(id)
        nodes = [node for node in cluster.nodes]
        if not any([
                node.state in [batch_models.ComputeNodeState.unusable, batch_models.ComputeNodeState.start_task_failed]
                for node in nodes
        ]):
            spark_client.cluster.delete(id=id)
    except (BatchErrorException, AztkError) as e:
        # pass in the event that the cluster does not exist
        print(str(e))
        acceptable_failures = [
            "The specified job has been marked for deletion and is being garbage collected.",
            "The specified pool has been marked for deletion and is being reclaimed."
        ]
        if any(item in str(e) for item in acceptable_failures):
            pass
        else:
            raise e
