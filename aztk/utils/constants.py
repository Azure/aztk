import os
"""
    DOCKER
"""
DOCKER_IMAGE_VERSION = "0.1.0"
DEFAULT_DOCKER_REPO = "aztk/spark:v0.1.0-spark2.3.0-base"
DEFAULT_DOCKER_REPO_GPU = "aztk/spark:v0.1.0-spark2.3.0-gpu"
DEFAULT_SPARK_PYTHON_DOCKER_REPO = "aztk/spark:v0.1.0-spark2.3.0-miniconda-base"
DEFAULT_SPARK_R_BASE_DOCKER_REPO = "aztk/spark:v0.1.0-spark2.3.0-r-base"
DOCKER_SPARK_CONTAINER_NAME = "spark"

# DOCKER SPARK
DOCKER_SPARK_WEB_UI_PORT = 8080
DOCKER_SPARK_WORKER_UI_PORT = 8081
DOCKER_SPARK_JOB_UI_PORT = 4040
DOCKER_SPARK_JOB_UI_HISTORY_PORT = 18080
DOCKER_SPARK_HOME = "/home/spark-current"
"""
    Root path of this repository
"""
ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
"""
    User home directory path
"""
HOME_DIRECTORY_PATH = os.path.expanduser("~")
"""
    Path to the secrets file
"""
DEFAULT_SECRETS_PATH = os.path.join(os.getcwd(), ".aztk/secrets.yaml")
"""
    Paths to the cluster configuration files
"""
GLOBAL_CONFIG_PATH = os.path.join(HOME_DIRECTORY_PATH, ".aztk")
DEFAULT_SSH_CONFIG_PATH = os.path.join(os.getcwd(), ".aztk/ssh.yaml")
DEFAULT_CLUSTER_CONFIG_PATH = os.path.join(os.getcwd(), ".aztk/cluster.yaml")
DEFAULT_SPARK_CONF_SOURCE = os.path.join(os.getcwd(), ".aztk")
DEFAULT_SPARK_CONF_DEST = os.path.join(ROOT_PATH, "node_scripts", "conf")
DEFAULT_SPARK_JARS_SOURCE = os.path.join(os.getcwd(), ".aztk", "jars")
DEFAULT_SPARK_JARS_DEST = os.path.join(ROOT_PATH, "node_scripts", "jars")
DEFAULT_SPARK_JOB_CONFIG = os.path.join(os.getcwd(), ".aztk", "job.yaml")
GLOBAL_SPARK_JOB_CONFIG = os.path.join(HOME_DIRECTORY_PATH, ".aztk", "job.yaml")
"""
    Source and destination paths for spark init
"""
INIT_DIRECTORY_SOURCE = os.path.join(ROOT_PATH, "aztk_cli", "config")
LOCAL_INIT_DIRECTORY_DEST = os.path.join(os.getcwd(), ".aztk")
GLOBAL_INIT_DIRECTORY_DEST = os.path.join(HOME_DIRECTORY_PATH, ".aztk")
"""
    Key of the metadata entry for the pool that is used to store the master node id
"""
MASTER_NODE_METADATA_KEY = "_spark_master_node"
"""
    Timeout in seconds to wait for the master to be ready
    Value: 20 minutes
"""
WAIT_FOR_MASTER_TIMEOUT = 60 * 20

AZTK_SOFTWARE_METADATA_KEY = "_aztk_software"

AZTK_MODE_METADATA_KEY = "_aztk_mode"
AZTK_CLUSTER_MODE_METADATA = "cluster"
AZTK_JOB_MODE_METADATA = "job"

AZTK_CLUSTER_CONFIG_METADATA_KEY = "_aztk_cluster_config"

TASK_WORKING_DIR = "wd"
SPARK_SUBMIT_LOGS_FILE = "output.log"
