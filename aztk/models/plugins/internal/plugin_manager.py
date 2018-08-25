import inspect
from aztk.error import InvalidPluginReferenceError
from aztk.spark.models import plugins


class PluginArgument:
    def __init__(self, name: str, required: bool, default=None):
        self.name = name
        self.required = required
        self.default = default


class PluginManager:
    # Indexing of all the predefined plugins
    plugins = dict(
        jupyter=plugins.JupyterPlugin,
        jupyterlab=plugins.JupyterLabPlugin,
        resource_monitor=plugins.ResourceMonitorPlugin,
        rstudio_server=plugins.RStudioServerPlugin,
        hdfs=plugins.HDFSPlugin,
        simple=plugins.SimplePlugin,
        spark_ui_proxy=plugins.SparkUIProxyPlugin,
        tensorflow_on_spark=plugins.TensorflowOnSparkPlugin,
        openblas=plugins.OpenBLASPlugin,
        nvblas=plugins.NvBLASPlugin,
        apt_get=plugins.AptGetPlugin,
        pip_install=plugins.PipPlugin,
        conda_install=plugins.CondaPlugin,
    )

    def __init__(self):
        self.loaded = False

    def has_plugin(self, name: str):
        return name in self.plugins

    def get_plugin(self, name: str, args: dict = None):
        args = args or dict()
        if not self.has_plugin(name):
            raise InvalidPluginReferenceError("Cannot find a plugin with name '{0}'".format(name))
        plugin_cls = self.plugins[name]
        self._validate_args(plugin_cls, args)

        return plugin_cls(**args)

    def get_args_for(self, cls):
        signature = inspect.signature(cls)
        args = dict()
        for key, param in signature.parameters.items():
            if param.kind == param.POSITIONAL_OR_KEYWORD or param.kind == param.KEYWORD_ONLY:
                args[key] = PluginArgument(
                    key, default=param.default, required=param.default is inspect.Parameter.empty)

        return args

    def _validate_args(self, plugin_cls, args: dict):
        """
        Validate the given args are valid for the plugin
        """
        plugin_args = self.get_args_for(plugin_cls)

        self._validate_no_extra_args(plugin_cls, plugin_args, args)

        for arg in plugin_args.values():
            if args.get(arg.name) is None:
                if arg.required:
                    message = "Missing a required argument {0} for plugin {1}".format(arg.name, plugin_cls.__name__)
                    raise InvalidPluginReferenceError(message)
                args[arg.name] = arg.default

    def _validate_no_extra_args(self, plugin_cls, plugin_args: dict, args: dict):
        for name in args:
            if not name in plugin_args:
                message = "Plugin {0} doesn't have an argument called '{1}'".format(plugin_cls.__name__, name)
                raise InvalidPluginReferenceError(message)


plugin_manager = PluginManager()
