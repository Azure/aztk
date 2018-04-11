import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTarget, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile
from aztk.utils import constants

dir_path = os.path.dirname(os.path.realpath(__file__))

class GrafanaPlugin(PluginConfiguration):
    def __init__(self):
        super().__init__(
            name="grafana",
            ports=[
                PluginPort(
                    internal=3000,
                    public=True,
                ),
            ],
            target=PluginTarget.Host,
            target_role=PluginTargetRole.All,
            execute="start_grafana.sh",
            files=[
                PluginFile("start_grafana.sh", os.path.join(dir_path, "start_grafana.sh")),
                PluginFile("example.env", os.path.join(dir_path, "example.env")),
            ],
        )
