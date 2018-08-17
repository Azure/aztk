import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginTarget, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile

dir_path = os.path.dirname(os.path.realpath(__file__))


class SimplePlugin(PluginConfiguration):
    def __init__(self):
        super().__init__(
            name="simple",
            target_role=PluginTargetRole.All,
            target=PluginTarget.Host,
            execute="simple.sh",
            files=[PluginFile("simple.sh", os.path.join(dir_path, "simple.sh"))],
        )
