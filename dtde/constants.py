import os

_MASTER_UI_PORT = 8082
_WEBUI_PORT = 4040
_JUPYTER_PORT = 7777

ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_PATH = os.path.join(ROOT_PATH, 'configuration.cfg') 

MASTER_NODE_METADATA_KEY = "_spark_master_node"
