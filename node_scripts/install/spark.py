"""
    Code that handle spark configuration
"""
import time
import os
from subprocess import call, Popen
from typing import List
import azure.batch.models as batchmodels
from core import config
import shutil
import json

batch_client = config.batch_client
spark_home = "/dsvm/tools/spark/current"
spark_conf_folder = os.path.join(spark_home, "conf")


def get_pool() -> batchmodels.CloudPool:
    return batch_client.pool.get(config.pool_id)


def list_nodes() -> List[batchmodels.ComputeNode]:
    """
        List all the nodes in the pool.
    """
    # TODO use continuation token & verify against current/target dedicated of
    # pool
    return batch_client.compute_node.list(config.pool_id)


def wait_for_pool_ready() -> batchmodels.CloudPool:
    """
        Wait for the pool to have allocated all the nodes
    """
    while True:
        pool = get_pool()
        if pool.allocation_state == batchmodels.AllocationState.steady:
            return pool
        else:
            print("Waiting for pool to be steady. It is currently %s" %
                  pool.allocation_state)
            time.sleep(5)  # Sleep for 10 seconds before trying again


def setup_connection():
    """
        This setup spark config with which nodes are slaves and which are master
    """
    wait_for_pool_ready()
    print("Pool is now steady. Setting up master")

    nodes = list_nodes()

    master_file = open(os.path.join(spark_conf_folder, "master"), 'w')
    slaves_file = open(os.path.join(spark_conf_folder, "slaves"), 'w')

    for node in nodes:
        if node.id == config.node_id:
            print("Adding node %s as a master" % node.id)
            master_file.write("%s\n" % node.ip_address)
        else:
            print("Adding node %s as a slave" % node.id)
            slaves_file.write("%s\n" % node.ip_address)

    master_file.close()
    slaves_file.close()


def generate_jupyter_config():
    return dict(
        display_name="PySpark",
        language="python",
        argv=[
            "/usr/bin/python3",
            "-m",
            "ipykernel",
            "-f",
            "",
        ],
        env=dict(
            SPARK_HOME="/dsvm/tools/spark/current",
            PYSPARK_PYTHON="/usr/bin/python3",
            PYSPARK_SUBMIT_ARGS="--master spark://${MASTER_NODE%:*}:7077 pyspark-shell",
        )
    )


def setup_jupyter():
    print("Setting up jupyter.")
    call(["/anaconda/envs/py35/bin/jupyter", "notebook", "--generate-config"])
    with open("test.txt", "a") as config_file:
        config_file.write('\n')
        config_file.write('c.NotebookApp.token=""\n')
        config_file.write('c.NotebookApp.password=""\n')
    shutil.rmtree('/usr/local/share/jupyter/kernels')
    os.makedirs('/usr/local/share/jupyter/kernels/pyspark', exist_ok=True)

    with open('/usr/local/share/jupyter/kernels/pyspark/kernel.json', 'w') as outfile:
        data = generate_jupyter_config()
        json.dump(data, outfile)


def start_jupyter():
    jupyter_port = config.jupyter_port
    
    my_env = os.environ.copy()
    my_env["PYSPARK_DRIVER_PYTHON"] = "/anaconda/envs/py35/bin/jupyter"
    my_env["PYSPARK_DRIVER_PYTHON_OPTS"] = "notebook --no-browser --port='%s'" % jupyter_port

    # call("pyspark", "&", env=my_env)
    Popen(["pyspark"], close_fds=True)


def start_spark():
    webui_port = config.webui_port

    exe = os.path.join(spark_home, "sbin", "start-all.sh")
    call([exe, "--webui-port", str(webui_port), "&"])

    setup_jupyter()
    start_jupyter()
