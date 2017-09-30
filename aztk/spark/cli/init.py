import os 
import argparse
import typing
from distutils.dir_util import copy_tree
import aztk.constants as constants


def setup_parser(parser: argparse.ArgumentParser):
    pass

def execute(args: typing.NamedTuple):
    config_src_path = constants.INIT_DIRECTORY_SOURCE
    config_dest_path = constants.INIT_DIRECTORY_DEST

    copy_tree(config_src_path, config_dest_path, update=1)

    secrets_template_path = os.path.join(constants.INIT_DIRECTORY_DEST, 'secrets.yaml.template')
    secrets_path = os.path.join(constants.INIT_DIRECTORY_DEST, 'secrets.yaml')

    if os.path.isfile(secrets_path):
        os.remove(secrets_template_path)

    if os.path.isfile(secrets_template_path) and not os.path.isfile(secrets_path):
        os.rename(secrets_template_path, secrets_path)
