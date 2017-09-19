import os

"""
    Name of the executable
"""
CLI_EXE = 'azb'

DEFAULT_DOCKER_REPO = "jiata/thunderbolt:0.1.0-spark2.2.0-python3.5.4"
DOCKER_SPARK_CONTAINER_NAME = "spark"

# DOCKER
DOCKER_SPARK_MASTER_UI_PORT = 8080
DOCKER_SPARK_WORKER_UI_PORT = 8081
DOCKER_SPARK_JUPYTER_PORT = 8888
DOCKER_SPARK_WEB_UI_PORT = 4040
DOCKER_SPARK_HOME = "/home/spark-current"

"""
    Root path of this repository
"""
ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

"""
    Path to the secrets file
"""
DEFAULT_SECRETS_PATH = os.path.join(os.getcwd(), '.thunderbolt/secrets.yaml')
"""
    Paths to the cluster configuration files
"""
DEFAULT_CLUSTER_CONFIG_PATH = os.path.join(os.getcwd(), '.thunderbolt/cluster.yaml')
DEFAULT_SPARK_CONF_SOURCE = os.path.join(os.getcwd(), '.thunderbolt')
DEFAULT_SPARK_CONF_DEST = os.path.join(os.getcwd(), 'node_scripts/conf')

"""
    Key of the metadata entry for the pool that is used to store the master node id
"""
MASTER_NODE_METADATA_KEY = "_spark_master_node"

"""
    Timeout in seconds to wait for the master to be ready
    Value: 20 minutes
"""
WAIT_FOR_MASTER_TIMEOUT = 60 * 20


AZB_SOFTWARE_METADATA_KEY = "_azb_software"

TASK_WORKING_DIR = "wd"
SPARK_SUBMIT_LOGS_FILE = "output.log"
