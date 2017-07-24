import os

"""
    Name of the executable
"""
CLI_EXE = 'azb'

SPARK_MASTER_UI_PORT = 8082
SPARK_WEBUI_PORT = 4040
SPARK_JUPYTER_PORT = 7777

"""
    Root path of this repository
"""
ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

"""
    Path to the configuration file
"""
CONFIG_PATH = os.path.join(ROOT_PATH, 'configuration.cfg')

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
