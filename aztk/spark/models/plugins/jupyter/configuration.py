import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTargetType
from aztk.models.plugins.plugin_file import PluginFile
from aztk.utils import constants

dir_path = os.path.dirname(os.path.realpath(__file__))

class JupyterPlugin(PluginConfiguration):
    def __init__(self):
        super().__init__(
            name="jupyter",
            ports=[
                PluginPort(
                    internal=8888,
                    public=True,
                ),
            ],
            target_type=PluginTargetType.All,
            execute="jupyter.sh",
            files=[
                PluginFile("jupyter.sh", os.path.join(dir_path, "jupyter.sh")),
            ],
        )
