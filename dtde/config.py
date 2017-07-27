import os
from . import constants

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

global_config = None


def load_config(path: str=constants.DEFAULT_CONFIG_PATH):
    """
        Loads the config file at the root of the repository(configuration.cfg)
    """
    global global_config
    if not os.path.isfile(path):
        raise Exception(
            "Configuration file doesn't exists at {0}".format(path))

    global_config = configparser.ConfigParser()
    global_config.read(path)


def get() -> configparser.ConfigParser:
    if not global_config:
        load_config()

    return global_config
