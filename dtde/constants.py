import os

_MASTER_UI_PORT = 8082
_WEBUI_PORT = 4040
_JUPYTER_PORT = 7777

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
