import argparse
import os
import typing
from distutils.dir_util import copy_tree

from aztk.utils import constants
from aztk_cli import log


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--global",
        dest="global_flag",
        action="store_true",
        help="Create a .aztk/ folder in your home directory for global configurations.",
    )
    software_parser = parser.add_mutually_exclusive_group()
    software_parser.add_argument("--miniconda", action="store_true", required=False)
    software_parser.add_argument("--anaconda", action="store_true", required=False)
    software_parser.add_argument("--r", "--R", action="store_true", required=False)
    software_parser.add_argument("--java", action="store_true", required=False)
    software_parser.add_argument("--scala", action="store_true", required=False)


def execute(args: typing.NamedTuple):
    # software_specific init
    if args.miniconda:
        environment = "miniconda"
    elif args.anaconda:
        environment = "anaconda"
    elif args.r:
        environment = "r"
    else:
        environment = ""

    if args.global_flag:
        create_directory(constants.GLOBAL_INIT_DIRECTORY_DEST, environment)
    else:
        create_directory(constants.LOCAL_INIT_DIRECTORY_DEST, environment)


def create_directory(dest_path: str, environment: str):
    config_src_path = constants.INIT_DIRECTORY_SOURCE
    config_dest_path = dest_path

    if os.path.isdir(config_dest_path):
        log.warning("This directory has already been initialized.")
        return

    copy_tree(config_src_path, config_dest_path, update=1)

    secrets_template_path = os.path.join(dest_path, "secrets.yaml.template")
    secrets_path = os.path.join(dest_path, "secrets.yaml")

    if os.path.isfile(secrets_path):
        os.remove(secrets_template_path)

    if os.path.isfile(secrets_template_path) and not os.path.isfile(secrets_path):
        os.rename(secrets_template_path, secrets_path)

    cluster_path = os.path.join(dest_path, "cluster.yaml")

    if os.path.isfile(cluster_path):
        with open(cluster_path, "r", encoding="UTF-8") as stream:
            cluster_yaml = stream.read()
        cluster_yaml = cluster_yaml.replace("{environment}", "{}\n".format(environment))
        with open(cluster_path, "w", encoding="UTF-8") as file:
            file.write(cluster_yaml)
