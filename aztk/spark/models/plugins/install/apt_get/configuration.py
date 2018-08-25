import os
from aztk.spark.models.plugins.install import InstallPlugin

dir_path = os.path.dirname(os.path.realpath(__file__))


def AptGetPlugin(packages=None):
    return InstallPlugin(name="apt-get", command="apt-get update && apt-get install -y", packages=packages)
