import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile

dir_path = os.path.dirname(os.path.realpath(__file__))


def NvBLASPlugin():
    return PluginConfiguration(
        name="nvblas",
        ports=[],
        target_role=PluginTargetRole.All,
        execute="nvblas.sh",
        files=[PluginFile("nvblas.sh", os.path.join(dir_path, "nvblas.sh"))],
    )
