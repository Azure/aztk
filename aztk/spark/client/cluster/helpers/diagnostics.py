import os

from azure.batch.models import batch_error

from aztk import error
from aztk.utils import helpers


def _run(spark_cluster_operations, cluster_id, output_directory=None, brief=False):
    # copy debug program to each node
    copy_output = spark_cluster_operations.copy(
        cluster_id, os.path.abspath("./aztk/spark/utils/debug.py"), "/tmp/debug.py", host=True)
    for node_output in copy_output:
        if node_output.error:
            raise error.AztkError("Failed to copy diagnostic script to cluster.")
    ssh_cmd = _build_diagnostic_ssh_command(brief)
    run_output = spark_cluster_operations.run(cluster_id, ssh_cmd, host=True)
    remote_path = "/tmp/debug.zip"
    result = None
    if output_directory:
        local_path = os.path.join(os.path.abspath(output_directory), "debug.zip")
        result = spark_cluster_operations.download(cluster_id, remote_path, local_path, host=True)

        # write run output or error to debug/ directory
        with open(os.path.join(output_directory, "debug-output.txt"), "w", encoding="UTF-8") as stream:
            for node_output in run_output:
                stream.write(node_output.error) if node_output.error else stream.write(node_output.output)
    else:
        result = spark_cluster_operations.download(cluster_id, remote_path, host=True)

    return result


def _build_diagnostic_ssh_command(brief):
    return ("sudo rm -rf /tmp/debug.zip; "
            "sudo apt-get install -y python3-pip; "
            "sudo -H pip3 install --upgrade pip; "
            "sudo -H pip3 install docker; "
            "sudo python3 /tmp/debug.py {}".format(brief))


def run_cluster_diagnostics(spark_cluster_operations, cluster_id, output_directory=None, brief=False):
    try:
        output = _run(spark_cluster_operations, cluster_id, output_directory, brief)
        return output
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
