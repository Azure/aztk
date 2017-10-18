import os 
import argparse
import typing
from distutils.dir_util import copy_tree
import aztk.constants as constants


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--global', dest='global_flag', action='store_true',
                        help="Create a .aztk/ folder in your home directory for global configurations.")

def execute(args: typing.NamedTuple):
    if args.global_flag:
        create_directory(constants.GLOBAL_INIT_DIRECTORY_DEST)
    else:
        create_directory(constants.LOCAL_INIT_DIRECTORY_DEST)
    
def create_directory(dest_path: str):
    config_src_path = constants.INIT_DIRECTORY_SOURCE
    config_dest_path = dest_path

    copy_tree(config_src_path, config_dest_path, update=1)

    secrets_template_path = os.path.join(dest_path, 'secrets.yaml.template')
    secrets_path = os.path.join(dest_path, 'secrets.yaml')

    if os.path.isfile(secrets_path):
        os.remove(secrets_template_path)

    if os.path.isfile(secrets_template_path) and not os.path.isfile(secrets_path):
        os.rename(secrets_template_path, secrets_path)
