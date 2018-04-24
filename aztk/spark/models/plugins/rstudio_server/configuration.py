import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile
from aztk.utils import constants
dir_path = os.path.dirname(os.path.realpath(__file__))


class RStudioServerPlugin(PluginConfiguration):
    def __init__(self, version="1.1.383"):
        super().__init__(
            name="rstudio_server",
            ports=[
                PluginPort(
                    internal=8787,
                    public=True,
                ),
            ],
            target_role=PluginTargetRole.Master,
            execute="rstudio_server.sh",
            files=[
                PluginFile("rstudio_server.sh", os.path.join(dir_path, "rstudio_server.sh")),
            ],
            env=dict(RSTUDIO_SERVER_VERSION=version),
        )
