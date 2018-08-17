import argparse
import typing

from aztk.models import TOOLKIT_MAP, Toolkit
from aztk_cli import log


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("toolkit_software", nargs="?")
    parser.add_argument("version", nargs="?")
    parser.add_argument("environment", nargs="?")
    parser.add_argument("--gpu", action="store_true")


def execute(args: typing.NamedTuple):
    if not args.toolkit_software:
        return print_available_softwares()

    if not validate_software(args.toolkit_software):
        return None

    if not args.version:
        return print_available_software_version(args.toolkit_software)
    if not args.environment:
        print_available_environments(args.toolkit_software)

    toolkit = Toolkit(software=args.toolkit_software, version=args.version, environment=args.environment)

    toolkit.validate()
    log.info("Docker image picked for this toolkit: %s", toolkit.get_docker_repo(args.gpu))
    return None


def print_available_softwares():
    log.info("Available toolkits: ")
    for toolkit in TOOLKIT_MAP:
        log.info("  - %s", toolkit)


def validate_software(software: str):
    if software not in TOOLKIT_MAP:
        log.error("Software '%s' is not supported.", software)
        print_available_softwares()
        return False
    return True


def print_available_software_version(software: str):
    toolkit_def = TOOLKIT_MAP.get(software)
    log.info("Available version for %s: ", software)
    for version in toolkit_def.versions:
        log.info("  - %s", version)


def print_available_environments(software: str):
    toolkit_def = TOOLKIT_MAP.get(software)

    log.info("Available environment for %s: ", software)
    for env in toolkit_def.environments:
        log.info("  - %s", env)
