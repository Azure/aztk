import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginPort, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile

dir_path = os.path.dirname(os.path.realpath(__file__))


class HDFSPlugin(PluginConfiguration):
    def __init__(self):
        super().__init__(
            name="hdfs",
            ports=[
                PluginPort(name="File system metadata operations", internal=8020),
                PluginPort(name="File system metadata operations(Backup)", internal=9000),
                PluginPort(name="Datanode data transfer", internal=50010),
                PluginPort(name="Datanode IPC metadata operations", internal=50020),
                PluginPort(name="Namenode", internal=50070, public=True),
                PluginPort(name="Datanodes", internal=50075, public=True),
            ],
            target_role=PluginTargetRole.All,
            execute="hdfs.sh",
            files=[PluginFile("hdfs.sh", os.path.join(dir_path, "hdfs.sh"))],
        )
