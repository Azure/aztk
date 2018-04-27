from enum import Enum
from typing import List, Union
from aztk.internal import ConfigurationBase
from aztk.error import InvalidPluginConfigurationError
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


class PluginPort:
    """
        Definition for a port that should be opened on node
        :param internal: Port on the node
        :param public: [Optional] Port available to the user. If none won't open any port to the user
        :param name: [Optional] name to differentiate ports if you have multiple
    """

    def __init__(self, internal: int, public: Union[int, bool]=False, name=None):
        self.internal = internal
        self.expose_publicly = bool(public)
        self.public_port = None
        if self.expose_publicly:
            if public is True:
                self.public_port = internal
            else:
                self.public_port = public

        self.name = name




class PluginConfiguration(ConfigurationBase):
    """
    Plugin manifest that should be returned in the main.py of your plugin
    :param name: Name of the plugin. Used to reference the plugin
    :param runOn: Where the plugin should run
    :param files: List of files to upload
    :param args:
    :param env:
    """

    def __init__(self,
                 name: str,
                 ports: List[PluginPort] = None,
                 files: List[PluginFile] = None,
                 execute: str = None,
                 args=None,
                 env=None,
                 target_role: PluginTargetRole = None,
                 target: PluginTarget = None):
        self.name = name
        # self.docker_image = docker_image
        self.target = target or PluginTarget.SparkContainer
        self.target_role = target_role or PluginTargetRole.Master
        self.ports = ports or []
        self.files = files or []
        self.args = args or []
        self.env = env or dict()
        self.execute = execute

    def has_arg(self, name: str):
        for x in self.args:
            if x.name == name:
                return True
        return False

    def validate(self):
        self._validate_required([
            "name",
            "execute",
        ])

        if not isinstance(self.target, PluginTarget):
            raise InvalidPluginConfigurationError(
                "Target must be of type Plugin target but was {0}".format(self.target))

        if not isinstance(self.target_role, PluginTargetRole):
            raise InvalidPluginConfigurationError(
                "Target role must be of type Plugin target role but was {0}".format(self.target))
