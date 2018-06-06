import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile
from aztk.spark.models.plugins.install import InstallPlugin
from aztk.utils import constants

dir_path = os.path.dirname(os.path.realpath(__file__))

def CondaPlugin(packages=None):
    return InstallPlugin(
        name="conda",
        command="conda install -y",
        packages=packages
    )
