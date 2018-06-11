import aztk.error as error
from aztk.core.models import Model, fields
from aztk.utils import deprecated,deprecate, helpers

from .custom_script import CustomScript
from .file_share import FileShare
from .plugins import PluginConfiguration
from .toolkit import Toolkit
from .user_configuration import UserConfiguration
from .scheduling_target import SchedulingTarget

class ClusterConfiguration(Model):
    """
    Cluster configuration model

    Args:
        cluster_id (str): Id of the Aztk cluster
        toolkit (aztk.models.Toolkit): Toolkit to be used for this cluster
        size (int): Number of dedicated nodes for this cluster
        size_low_priority (int): Number of low priority nodes for this cluster
        vm_size (int): Azure Vm size to be used for each node
        subnet_id (str): Full resource id of the subnet to be used(Required for mixed mode clusters)
        plugins (List[aztk.models.plugins.PluginConfiguration]): List of plugins to be used
        file_shares (List[aztk.models.FileShare]): List of File shares to be used
        user_configuration (aztk.models.UserConfiguration): Configuration of the user to
            be created on the master node to ssh into.
    """

    cluster_id = fields.String()
    toolkit = fields.Model(Toolkit)
    size = fields.Integer(default=0)
    size_low_priority = fields.Integer(default=0)
    vm_size = fields.String()

    subnet_id = fields.String(default=None)
    plugins = fields.List(PluginConfiguration)
    custom_scripts = fields.List(CustomScript)
    file_shares = fields.List(FileShare)
    user_configuration = fields.Model(UserConfiguration, default=None)
    scheduling_target = fields.Enum(SchedulingTarget, default=None)

    def __init__(self, *args, **kwargs):
        if 'vm_count' in kwargs:
            deprecate("0.9.0", "vm_count is deprecated for ClusterConfiguration.", "Please use size instead.")
            kwargs['size'] = kwargs.pop('vm_count')

        if 'vm_low_pri_count' in kwargs:
            deprecate("vm_low_pri_count is deprecated for ClusterConfiguration.", "Please use size_low_priority instead.")
            kwargs['size_low_priority'] = kwargs.pop('vm_low_pri_count')

        super().__init__(*args, **kwargs)

    @property
    @deprecated("0.9.0")
    def vm_count(self):
        return self.size

    @vm_count.setter
    @deprecated("0.9.0")
    def vm_count(self, value):
        self.size = value

    @property
    @deprecated("0.9.0")
    def vm_low_pri_count(self):
        return self.size_low_priority

    @vm_low_pri_count.setter
    @deprecated("0.9.0")
    def vm_low_pri_count(self, value):
        self.size_low_priority = value

    def mixed_mode(self) -> bool:
        """
        Return:
            if the pool is using mixed mode(Both dedicated and low priority nodes)
        """
        return self.size > 0 and self.size_low_priority > 0


    def gpu_enabled(self):
        return helpers.is_gpu_enabled(self.vm_size)

    def get_docker_repo(self):
        return self.toolkit.get_docker_repo(self.gpu_enabled())

    def __validate__(self) -> bool:
        if self.size == 0 and self.size_low_priority == 0:
            raise error.InvalidModelError(
                "Please supply a valid (greater than 0) size or size_low_priority value either in the cluster.yaml configuration file or with a parameter (--size or --size-low-pri)"
            )

        if self.vm_size is None:
            raise error.InvalidModelError(
                "Please supply a vm_size in either the cluster.yaml configuration file or with a parameter (--vm-size)"
            )

        if self.mixed_mode() and not self.subnet_id:
            raise error.InvalidModelError(
                "You must configure a VNET to use AZTK in mixed mode (dedicated and low priority nodes). Set the VNET's subnet_id in your cluster.yaml."
            )

        if self.custom_scripts:
            deprecate("0.9.0", "Custom scripts are DEPRECATED.", "Use plugins instead. See https://aztk.readthedocs.io/en/v0.7.0/15-plugins.html.")

        if self.scheduling_target == SchedulingTarget.Dedicated and self.size == 0:
            raise error.InvalidModelError("Scheduling target cannot be Dedicated if dedicated vm size is 0")
