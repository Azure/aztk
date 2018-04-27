import os

from aztk.error import InvalidModelError
from aztk.internal import ConfigurationBase
from aztk.models import PluginConfiguration
from aztk.models.plugins import PluginFile, PluginTarget, PluginTargetRole

from .plugin_manager import plugin_manager


class PluginReference(ConfigurationBase):
    """
    Contains the configuration to use a plugin

    Args:
        name (str): Name of the plugin(Must be the name of one of the provided plugins if no script provided)
        script (str): Path to a custom script to run as the plugin
        target_role (PluginTarget): Target for the plugin. Default to SparkContainer.
                                    This can only be used if providing a script
        target_role (PluginTargetRole): Target role default to All nodes. This can only be used if providing a script
        args: (dict): If using name this is the arguments to pass to the plugin
    """
    def __init__(self,
                 name: str = None,
                 script: str = None,
                 target: PluginTarget = None,
                 target_role: PluginTargetRole = None,
                 args: dict = None):
        super().__init__()
        self.name = name
        self.script = script
        self.target = target
        self.target_role = target_role
        self.args = args or dict()

    @classmethod
    def _from_dict(cls, args: dict):
        if "target" in args:
            args["target"] = PluginTarget(args["target"])
        if "target_role" in args:
            args["target_role"] = PluginTargetRole(args["target_role"])

        return super()._from_dict(args)

    def get_plugin(self) -> PluginConfiguration:
        self.validate()

        if self.script:
            return self._plugin_from_script()

        return plugin_manager.get_plugin(self.name, self.args)

    def validate(self) -> bool:
        if not self.name and not self.script:
            raise InvalidModelError("Plugin must either specify a name of an existing plugin or the path to a script.")

        if self.script and not os.path.isfile(self.script):
            raise InvalidModelError("Plugin script file doesn't exists: '{0}'".format(self.script))

    def _plugin_from_script(self):
        script_filename = os.path.basename(self.script)
        name = self.name or os.path.splitext(script_filename)[0]
        return PluginConfiguration(
            name=name,
            execute=script_filename,
            target=self.target,
            target_role=self.target_role or PluginConfiguration,
            files=[
                PluginFile(script_filename, self.script),
            ],
        )
