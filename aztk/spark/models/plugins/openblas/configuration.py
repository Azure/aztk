import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile

dir_path = os.path.dirname(os.path.realpath(__file__))


def OpenBLASPlugin():
    return PluginConfiguration(
        name="openblas",
        ports=[],
        target_role=PluginTargetRole.All,
        execute="openblas.sh",
        files=[PluginFile("openblas.sh", os.path.join(dir_path, "openblas.sh"))],
    )
