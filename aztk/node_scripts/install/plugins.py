import json
import os
import subprocess

import yaml

from aztk.models.plugins import PluginTarget, PluginTargetRole

log_folder = os.path.join(os.environ["AZTK_WORKING_DIR"], "logs", "plugins")


def _read_manifest_file(path=None):
    if not os.path.isfile(path):
        print("Plugins manifest file doesn't exist at {0}".format(path))
    else:
        with open(path, "r", encoding="UTF-8") as stream:
            try:
                return yaml.load(stream)
            except json.JSONDecodeError as err:
                print("Error in plugins manifest: {0}".format(err))


def setup_plugins(target: PluginTarget, is_master: bool = False, is_worker: bool = False):

    plugins_dir = _plugins_dir()
    plugins_manifest = _read_manifest_file(os.path.join(plugins_dir, "plugins-manifest.yaml"))

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    if plugins_manifest is not None:
        _setup_plugins(plugins_manifest, target, is_master, is_worker)


def _plugins_dir():
    return os.path.join(os.environ["AZTK_WORKING_DIR"], "plugins")


def _run_on_this_node(plugin_obj, target: PluginTarget, is_master, is_worker):

    print("Loading plugin {} in {} on {}".format(plugin_obj["execute"], plugin_obj["target"],
                                                 plugin_obj["target_role"]))

    if plugin_obj["target"] != target.value:
        print(
            "Ignoring ",
            plugin_obj["execute"],
            "as target is for ",
            plugin_obj["target"],
            "but is currently running in ",
            target.value,
        )
        return False

    if plugin_obj["target_role"] == PluginTargetRole.Master.value and is_master is True:
        return True
    if plugin_obj["target_role"] == PluginTargetRole.Worker.value and is_worker is True:
        return True
    if plugin_obj["target_role"] == PluginTargetRole.All.value:
        return True

    print(
        "Ignoring plugin",
        plugin_obj["execute"],
        "as target role is ",
        plugin_obj["target_role"],
        "and node is master: ",
        is_master,
        is_worker,
    )

    return False


def _setup_plugins(plugins_manifest, target: PluginTarget, is_master, is_worker):
    plugins_dir = _plugins_dir()

    for plugin in plugins_manifest:
        if _run_on_this_node(plugin, target, is_master, is_worker):
            path = os.path.join(plugins_dir, plugin["execute"])
            _run_script(plugin.get("name"), path, plugin.get("args"), plugin.get("env"))


def _run_script(name: str, script_path: str = None, args: dict = None, env: dict = None):
    if not os.path.isfile(script_path):
        print("Cannot run plugin script: {0} file does not exist".format(script_path))
        return
    file_stat = os.stat(script_path)
    os.chmod(script_path, file_stat.st_mode | 0o777)
    print("------------------------------------------------------------------")
    print("Running plugin script:", script_path)

    my_env = os.environ.copy()
    if env:
        for [key, value] in env.items():
            my_env[key] = value

    if args is None:
        args = []

    out_file = open(os.path.join(log_folder, "{0}.txt".format(name)), "w", encoding="UTF-8")
    try:
        subprocess.call([script_path] + args, env=my_env, stdout=out_file, stderr=out_file)
        print("Finished running")
        print("------------------------------------------------------------------")
    except Exception as e:
        print(e)
