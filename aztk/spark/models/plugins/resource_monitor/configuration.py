import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTarget, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile
from aztk.utils import constants

dir_path = os.path.dirname(os.path.realpath(__file__))

class ResourceMonitorPlugin(PluginConfiguration):
    def __init__(self):
        super().__init__(
            name="resource_monitor",
            ports=[
                PluginPort(
                    internal=3000,
                    public=True,
                ),
                PluginPort(
                    internal=8083,
                    public=True,
                ),
                PluginPort(
                    internal=8086,
                    public=True,
                ),
            ],
            target=PluginTarget.Host,
            target_role=PluginTargetRole.All,
            execute="start_monitor.sh",
            files=[
                PluginFile("start_monitor.sh", os.path.join(dir_path, "start_monitor.sh")),
                PluginFile(".env", os.path.join(dir_path, ".env")),
                PluginFile("docker-compose.yml", os.path.join(dir_path, "docker-compose.yml")),
                PluginFile("nodestats.py", os.path.join(dir_path, "nodestats.py")),
                PluginFile("requrements.txt", os.path.join(dir_path, "requrements.txt")),
                PluginFile("resource_monitor_dashboard.json",
                    os.path.join(dir_path, "resource_monitor_dashboard.json")),
            ],
        )
