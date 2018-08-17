import os


def run(spark_client, cluster_id, output_directory=None):
    # copy debug program to each node
    output = spark_client.cluster_copy(
        cluster_id, os.path.abspath("./aztk/spark/utils/debug.py"), "/tmp/debug.py", host=True)
    ssh_cmd = _build_diagnostic_ssh_command()
    run_output = spark_client.cluster_run(cluster_id, ssh_cmd, host=True)
    remote_path = "/tmp/debug.zip"
    if output_directory:
        local_path = os.path.join(os.path.abspath(output_directory), "debug.zip")
        output = spark_client.cluster_download(cluster_id, remote_path, local_path, host=True)

        # write run output to debug/ directory
        with open(os.path.join(os.path.dirname(local_path), "debug-output.txt"), "w", encoding="UTF-8") as f:
            [f.write(line + "\n") for node_output in run_output for line in node_output.output]
    else:
        output = spark_client.cluster_download(cluster_id, remote_path, host=True)

    return output


def _build_diagnostic_ssh_command():
    return "sudo rm -rf /tmp/debug.zip; " "sudo apt-get install -y python3-pip; " "sudo -H pip3 install --upgrade pip; " "sudo -H pip3 install docker; " "sudo python3 /tmp/debug.py"
