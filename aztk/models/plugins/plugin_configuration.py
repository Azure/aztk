from enum import Enum

from aztk.core.models import Model, fields

from .plugin_file import PluginFile


class PluginTarget(Enum):
    """
    Where this plugin should run
    """

    SparkContainer = "spark-container"
    Host = "host"


class PluginTargetRole(Enum):
    Master = "master"
    Worker = "worker"
    All = "all-nodes"


class PluginPort(Model):
    """
        Definition for a port that should be opened on node
        :param internal: Port on the node
        :param public: [Optional] Port available to the user. If none won't open any port to the user
        :param name: [Optional] name to differentiate ports if you have multiple
    """

    internal = fields.Integer()
    public = fields.Field(default=None)
    name = fields.Integer()

    @property
    def expose_publicly(self):
        return bool(self.public)

    @property
    def public_port(self):
        if self.expose_publicly:
            if self.public is True:
                return self.internal
            return self.public
        return None


class PluginConfiguration(Model):
    """
    Plugin manifest that should be returned in the main.py of your plugin

    Args
        name: Name of the plugin. Used to reference the plugin
        runOn: Where the plugin should run
        execute: Path to the file to execute(This must match the target of one of the files)
        files: List of files to upload
        args: List of arguments to pass to the executing script
        env: Dict of environment variables to pass to the script
    """

    name = fields.String()
    files = fields.List(PluginFile)
    execute = fields.String()
    args = fields.List(default=[])
    env = fields.List(default=[])
    target = fields.Enum(PluginTarget, default=PluginTarget.SparkContainer)
    target_role = fields.Enum(PluginTargetRole, default=PluginTargetRole.Master)
    ports = fields.List(PluginPort, default=[])

    def has_arg(self, name: str):
        for x in self.args:
            if x.name == name:
                return True
        return False
