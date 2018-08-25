import os
from aztk.models.plugins.plugin_configuration import PluginConfiguration, PluginTargetRole
from aztk.models.plugins.plugin_file import PluginFile

dir_path = os.path.dirname(os.path.realpath(__file__))


def TensorflowOnSparkPlugin():
    return PluginConfiguration(
        name="tensorflow_on_spark",
        target_role=PluginTargetRole.Master,
        execute="tensorflow_on_spark.sh",
        files=[PluginFile("tensorflow_on_spark.sh", os.path.join(dir_path, "tensorflow_on_spark.sh"))],
    )
