import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile

dir_path = os.path.dirname(os.path.realpath(__file__))


def JupyterLabPlugin():
    return PluginConfiguration(
        name="jupyterlab",
        ports=[PluginPort(internal=8889, public=True)],
        target_role=PluginTargetRole.All,
        execute="jupyter_lab.sh",
        files=[PluginFile("jupyter_lab.sh", os.path.join(dir_path, "jupyter_lab.sh"))],
    )
