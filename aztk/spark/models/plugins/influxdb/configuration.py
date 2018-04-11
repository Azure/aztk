import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTarget, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile
from aztk.utils import constants

dir_path = os.path.dirname(os.path.realpath(__file__))

class InfluxDBPlugin(PluginConfiguration):
    def __init__(self):
        super().__init__(
            name="influxdb",
            ports=[
                PluginPort(
                    internal=8083,
                    public=True,
                ),
                PluginPort(
                    internal=8086,
                    public=True,
                ),
                PluginPort(
                    internal=8090,
                    public=True,
                ),
            ],
            target=PluginTarget.Host,
            target_role=PluginTargetRole.All,
            execute="start_influxdb.sh",
            files=[
                PluginFile("start_influxdb.sh", os.path.join(dir_path, "start_influxdb.sh")),
                PluginFile("example.env", os.path.join(dir_path, "example.env")),
            ],
        )
