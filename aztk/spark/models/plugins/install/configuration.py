import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile

dir_path = os.path.dirname(os.path.realpath(__file__))


def InstallPlugin(name, command, packages=None):
    return PluginConfiguration(
        name=name,
        target_role=PluginTargetRole.All,
        execute="install.sh",
        files=[PluginFile("install.sh", os.path.join(dir_path, "install.sh"))],
        args=packages,
        env=dict(COMMAND=command),
    )
