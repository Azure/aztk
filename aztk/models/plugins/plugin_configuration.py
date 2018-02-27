import inspect
from typing import List, Union
from enum import Enum
from .plugin_file import PluginFile
from aztk.internal import ConfigurationBase

class PluginPort:
    """
        Definition for a port that should be opened on node
        :param internal: Port on the node
        :param public: [Optional] Port available to the user. If none won't open any port to the user
        :param name: [Optional] name to differentiate ports if you have multiple
    """

    def __init__(self, internal: int, public: Union[int, bool] = False, name=None):

        self.internal = internal
        self.expose_publicly = bool(public)
        self.public_port = None
        if self.expose_publicly:
            if public is True:
                self.public_port = internal
            else:
                self.public_port = public

        self.name = name


class PluginRunTarget(Enum):
    Master = "master"
    Worker = "worker"
    All = "all-nodes"



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
                 run_on: PluginRunTarget = PluginRunTarget.Master):
        self.name = name
        # self.docker_image = docker_image
        self.run_on = run_on
        self.ports = ports or []
        self.files = files or []
        self.args = args or []
        self.env = env or dict()
        self.execute = execute

    def has_arg(self, name: str):
        for x in self.args:
            if x.name == name:
                return True
        else:
            return False

    def validate(self):
        self._validate_required([
            "name",
            "execute",
        ])
