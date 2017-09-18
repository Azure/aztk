import os
from shutil import copyfile, rmtree
from . import constants
from dtde import log
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

global_config = None

def load_spark_config():
    """
        Copies the spark-defautls.conf and spark-env.sh in the .thunderbolt/ diretory
    """
    if not os.path.exists(constants.DEFAULT_SPARK_CONF_DEST):
        os.mkdir(constants.DEFAULT_SPARK_CONF_DEST)

    try:
        copyfile(
                os.path.join(constants.DEFAULT_SPARK_CONF_SOURCE, 'spark-defaults.conf'),
                os.path.join(constants.DEFAULT_SPARK_CONF_DEST, 'spark-defaults.conf'))
        log.info("Loaded spark-defaults.conf")
    except Exception as e:
        print(e)
    try:
        copyfile(
                os.path.join(constants.DEFAULT_SPARK_CONF_SOURCE, 'spark-env.sh'),
                os.path.join(constants.DEFAULT_SPARK_CONF_DEST, 'spark-env.sh'))
        log.info("Loaded spark-env.sh")
    except Exception as e:
        print(e)


def cleanup_spark_config():
    """
        Removes copied remaining spark config files after they have been uploaded
    """
    if os.path.exists(constants.DEFAULT_SPARK_CONF_DEST):
        rmtree(constants.DEFAULT_SPARK_CONF_DEST)


def load_config(path: str=constants.DEFAULT_CONFIG_PATH):
    """
        Loads the config file at the root of the repository(secrets.cfg)
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
