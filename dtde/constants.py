import os

"""
    Name of the executable
"""
CLI_EXE = 'azb'

# DOCKER_REPO_NAME = "jiata/spark:latest"
DOCKER_REPO_NAME = "jiata/spark-2.2.0:latest"
DOCKER_SPARK_CONTAINER_NAME = "spark"

# DOCKER
DOCKER_SPARK_MASTER_UI_PORT = 8080
DOCKER_SPARK_WORKER_UI_PORT = 8081
DOCKER_SPARK_JUPYTER_PORT = 8888
DOCKER_SPARK_WEB_UI_PORT = 4040
DOCKER_SPARK_HOME = "/home/spark-2.2.0-bin-hadoop2.7"

# DSVM
DSVM_SPARK_MASTER_UI_PORT = 8082
DSVM_SPARK_WORKER_UI_PORT = 8083
DSVM_SPARK_JUPYTER_PORT = 7777
DSVM_SPARK_WEB_UI_PORT = 4040
DSVM_SPARK_HOME = "/dsvm/tools/spark/current"

"""
    Root path of this repository
"""
ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

"""
    Path to the configuration file
"""
DEFAULT_CONFIG_PATH = os.path.join(os.getcwd(), 'configuration.cfg')

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
