from . import constants
import os

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

global_config = None

def load_config():
    """
        Loads the config file at the root of the repository(configuration.cfg)
    """
    global global_config
    if not os.path.isfile(constants.CONFIG_PATH):
        raise Exception("Configuration file doesn't exists at {0}".format(constants.CONFIG_PATH))

    global_config = configparser.ConfigParser()
    global_config.read(constants.CONFIG_PATH)

def get() -> configparser.ConfigParser:
    if not global_config:
        load_config()

    return global_config
