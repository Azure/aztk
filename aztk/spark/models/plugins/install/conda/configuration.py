import os
from aztk.spark.models.plugins.install import InstallPlugin

dir_path = os.path.dirname(os.path.realpath(__file__))


def CondaPlugin(packages=None):
    return InstallPlugin(name="conda", command="conda install -y", packages=packages)
