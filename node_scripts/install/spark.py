"""
    Code that handle spark configuration
"""
import time
import azure.batch.batch_service_client as batch
import azure.batch.models as batchmodels
from core import config

batch_client = config.batch_client


def get_pool() -> batchmodels.CloudPool:
    return batch_client.pool.get(config.pool_id)


def list_nodes() -> List[batchmodels.ComputeNode]:
    return batch_client.compute_node.list(config.pool_id)


def wait_for_pool_ready() -> batchmodels.CloudPool:
    while True:
        pool = get_pool()
        if pool.state == batchmodels.AllocationState.steady
            return pool
        else:
            print("Waiting for pool to be steady.")
            time.sleep(5)  # Sleep for 10 seconds before trying again


def connect_node(batch_client: batch.BatchServiceClient):
    pool = wait_for_pool_ready()
    print("Pool is now steady. Setting up master")

    spark_home = "/dsvm/tools/spark/current"
    spark_conf_folder = os.path.join(spark_home, "conf")

    nodes = list_nodes()

    for node in nodes:
        
    return [
        # set SPARK_HOME environment vars
        'export PATH=$PATH:$SPARK_HOME/bin',

        # copy a 'slaves' file from the slaves.template in $SPARK_HOME/conf
        'cp $SPARK_HOME/conf/slaves.template $SPARK_HOME/conf/slaves'

        # delete existing content & create a new line in the slaves file
        'echo > $SPARK_HOME/conf/slaves',

        # make empty 'master' file in $SPARK/conf
        'cp $SPARK_HOME/conf/slaves $SPARK_HOME/conf/master',

        # add batch pool ips to newly created slaves files
        'IFS="," read -r -a workerips <<< $AZ_BATCH_HOST_LIST',
        'for index in "${!workerips[@]}"',
        'do echo "${workerips[index]}"',
        'if [ "${AZ_BATCH_MASTER_NODE%:*}" = "${workerips[index]}" ]',
        'then echo "${workerips[index]}" >> $SPARK_HOME/conf/master',
        'else echo "${workerips[index]}" >> $SPARK_HOME/conf/slaves',
        'fi',
        'done'
    ]


def start_cmd(webui_port, jupyter_port):
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
