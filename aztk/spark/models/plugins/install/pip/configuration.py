import os
from aztk.spark.models.plugins.install import InstallPlugin

dir_path = os.path.dirname(os.path.realpath(__file__))


def PipPlugin(packages=None):
    return InstallPlugin(name="pip", command="pip install", packages=packages)
