import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile
from aztk.spark.models.plugins.install import InstallPlugin
from aztk.utils import constants

dir_path = os.path.dirname(os.path.realpath(__file__))

def PipPlugin(packages=None):
    return InstallPlugin(
        name="pip",
        command="pip install",
        packages=packages
    )
