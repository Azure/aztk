import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTarget, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile

dir_path = os.path.dirname(os.path.realpath(__file__))


class ResourceMonitorPlugin(PluginConfiguration):
    def __init__(self):
        super().__init__(
            name="resource_monitor",
            ports=[PluginPort(internal=8890, public=True)],
            target=PluginTarget.Host,
            target_role=PluginTargetRole.All,
            execute="start_monitor.sh",
            files=[
                PluginFile("start_monitor.sh", os.path.join(dir_path, "start_monitor.sh")),
                PluginFile("etc/telegraf.conf", os.path.join(dir_path, "telegraf.conf")),
                PluginFile("docker-compose.yml", os.path.join(dir_path, "docker-compose.yml")),
            ],
        )
