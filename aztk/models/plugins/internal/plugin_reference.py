from aztk.error import InvalidPluginConfigurationError, InvalidModelError
from aztk.internal import ConfigurationBase
from aztk.models import PluginConfiguration
from .plugin_manager import plugin_manager

class PluginReference(ConfigurationBase):
    """
    Contains the configuration to use a plugin
    """
    def __init__(self, name, args: dict = None):
        super().__init__()
        self.name = name
        self.args = args or dict()

    def get_plugin(self) -> PluginConfiguration:
        return plugin_manager.get_plugin(self.name, self.args)

    def validate(self) -> bool:
        if not self.name:
            raise InvalidModelError("Plugin is missing a name")

