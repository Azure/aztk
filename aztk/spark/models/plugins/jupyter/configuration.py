import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile

dir_path = os.path.dirname(os.path.realpath(__file__))


def JupyterPlugin():
    return PluginConfiguration(
        name="jupyter",
        ports=[PluginPort(internal=8888, public=True)],
        target_role=PluginTargetRole.All,
        execute="jupyter.sh",
        files=[PluginFile("jupyter.sh", os.path.join(dir_path, "jupyter.sh"))],
    )
