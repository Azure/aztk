"""
    Code that handle spark configuration
"""
import time
import os
from typing import List
import azure.batch.batch_service_client as batch
import azure.batch.models as batchmodels
from core import config

batch_client = config.batch_client


def get_pool() -> batchmodels.CloudPool:
    return batch_client.pool.get(config.pool_id)


def list_nodes() -> List[batchmodels.ComputeNode]:
    """
        List all the nodes in the pool.
    """
    # TODO use continuation token & verify against current/target dedicated of pool
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
            print("Waiting for pool to be steady. It is currently %s" % pool.allocation_state)
            time.sleep(5)  # Sleep for 10 seconds before trying again


def setup_connection():
    """
        This setup spark config with which nodes are slaves and which are master
    """
    wait_for_pool_ready()
    print("Pool is now steady. Setting up master")

    spark_home = "/dsvm/tools/spark/current"
    spark_conf_folder = os.path.join(spark_home, "conf")

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

def start_spark(webui_port, jupyter_port):
    return [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',

        # get master node ip
        'export MASTER_NODE=$(cat $SPARK_HOME/conf/master)',

        # kick off start-all spark command (which starts web ui)
        '($SPARK_HOME/sbin/start-all.sh --webui-port ' + str(webui_port) + ' &)',

        # jupyter setup: remove auth
        '/anaconda/envs/py35/bin/jupyter notebook --generate-config',
        'echo >> $HOME/.jupyter/jupyter_notebook_config.py',
        'echo c.NotebookApp.token=\\\"\\\" >> $HOME/.jupyter/jupyter_notebook_config.py',
        'echo c.NotebookApp.password=\\\"\\\" >> $HOME/.jupyter/jupyter_notebook_config.py',

        # create jupyter kernal for pyspark
        'rm -rf /usr/local/share/jupyter/kernels/*',
        'mkdir /usr/local/share/jupyter/kernels/pyspark',
        'touch /usr/local/share/jupyter/kernels/pyspark/kernel.json',
        'echo { ' +
        '\\\"display_name\\\": \\\"PySpark\\\", ' +
        '\\\"language\\\": \\\"python\\\", ' +
        '\\\"argv\\\": [ ' +
        '\\\"/usr/bin/python3\\\", ' +
        '\\\"-m\\\", ' +
        '\\\"ipykernel\\\", ' +
        '\\\"-f\\\", ' +
        '\\\"{connection_file}\\\" ' +
        '], ' +
        '\\\"env\\\": { ' +
        '\\\"SPARK_HOME\\\": \\\"/dsvm/tools/spark/current\\\", ' +
        '\\\"PYSPARK_PYTHON\\\": \\\"/usr/bin/python3\\\", ' +
        '\\\"PYSPARK_SUBMIT_ARGS\\\": ' +
        '\\\"--master spark://${MASTER_NODE%:*}:7077 ' +
        # '--executor-memory 6400M ' +
        # '--driver-memory 6400M ' +
        'pyspark-shell\\\" ' +
        '}' +
        '} >> /usr/local/share/jupyter/kernels/pyspark/kernel.json',

        # start jupyter notebook
        '(PYSPARK_DRIVER_PYTHON=/anaconda/envs/py35/bin/jupyter ' +
        'PYSPARK_DRIVER_PYTHON_OPTS="notebook --no-browser --port=' + str(jupyter_port) + '" ' +
        'pyspark &)'  # +
        #     '--master spark://${MASTER_NODE%:*}:7077 '  +
        #     '--executor-memory 6400M ' +
        #     '--driver-memory 6400M &)'
    ]
