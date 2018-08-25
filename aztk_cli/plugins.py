import argparse
import typing

from aztk.models.plugins.internal import plugin_manager
from aztk_cli import log


def setup_parser(_: argparse.ArgumentParser):
    pass


def execute(args: typing.NamedTuple):
    plugins = plugin_manager.plugins
    log.info("------------------------------------------------------")
    log.info("                   Plugins (%i available)", len(plugins))
    log.info("------------------------------------------------------")
    for name, plugin in plugins.items():
        log.info("- %s", name)
        args = plugin_manager.get_args_for(plugin)
        if args:
            log.info("    Arguments:")
            for arg in args.values():
                log.info("      - %s", arg_str(arg))
        else:
            log.info("    Arguments: None")
        log.info("")


def arg_str(arg):
    required = "Required" if arg.required else "Optional(Default: {0})".format(arg.default)
    return "{0}: {1}".format(arg.name, required)
