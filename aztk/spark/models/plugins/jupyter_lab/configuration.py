import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTarget, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile
from aztk.utils import constants

dir_path = os.path.dirname(os.path.realpath(__file__))

class JupyterLabPlugin(PluginConfiguration):
    def __init__(self):
        super().__init__(
            name="jupyterlab",
            ports=[
                PluginPort(
                    internal=8889,
                    public=True,
                ),
            ],
            target=PluginTarget.SparkContainer,
            target_role=PluginTargetRole.Master,
            execute="jupyter_lab.sh",
            files=[
                PluginFile("jupyter_lab.sh", os.path.join(dir_path, "jupyter_lab.sh")),
            ],
        )
