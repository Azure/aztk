import os
import pytest
from aztk.models.plugins import PluginConfiguration
from aztk.models.plugins.internal import PluginManager
from aztk.error import InvalidPluginReferenceError

dir_path = os.path.dirname(os.path.realpath(__file__))
fake_plugin_dir = os.path.join(dir_path, "fake_plugins")


def RequiredArgPlugin(req_arg):
    return PluginConfiguration(name="required-arg")


def test_missing_plugin():
    plugin_manager = PluginManager()
    message = "Cannot find a plugin with name .*"
    with pytest.raises(InvalidPluginReferenceError, match=message):
        plugin_manager.get_plugin("non-existing-plugin")


def test_extra_args_plugin():
    plugin_manager = PluginManager()
    message = "Plugin JupyterPlugin doesn't have an argument called 'invalid'"
    with pytest.raises(InvalidPluginReferenceError, match=message):
        plugin_manager.get_plugin("jupyter", args=dict(invalid="foo"))


def test_missing_required_arg():
    plugin_manager = PluginManager()
    plugin_manager.plugins["required-arg"] = RequiredArgPlugin
    message = "Missing a required argument req_arg for plugin RequiredArgPlugin"
    with pytest.raises(InvalidPluginReferenceError, match=message):
        plugin_manager.get_plugin("required-arg")
