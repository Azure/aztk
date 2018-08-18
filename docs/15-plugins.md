# Plugins

Plugins can either be one of the `aztk` [supported plugins](#supported-plugins) or the path to a [local file](#custom-script-plugin).

## Supported Plugins
AZTK ships with a library of default plugins that enable auxiliary services to use with your Spark cluster.

Currently the following plugins are supported:

- JupyterLab
- Jupyter
- HDFS
- RStudioServer
- TensorflowOnSpark
- OpenBLAS
- mvBLAS

### Enable a plugin using the CLI
If you are using the `aztk` CLI and wish to enable a supported plugin, you need to update you `.aztk/cluster.yaml` configuration file.

Add or uncomment the `plugins` section and set the plugins you desire to enable as follows:
```yaml
plugins:
    - name: jupyterlab
    - name: jupyter
    - name: hdfs
    - name: spark_ui_proxy
    - name: rsutio_server
      args:
        version: "1.1.383"
```

### Enable a plugin using the SDK
If you are using the `aztk` SDK and wish to enable a supported plugin, you need to import the necessary plugins from the `aztk.spark.models.plugin` module and add them to your ClusterConfiguration object's plugin list:
```python
from aztk.spark.models.plugins import RStudioServerPlugin, HDFSPlugin
cluster_config = ClusterConfiguration(
  ...# Other config,
  plugins=[
    JupyterPlugin(),
    HDFSPlugin(),
  ]
)
```


## Custom script plugin

This allows you to run your custom code on the cluster
### Run a custom script plugin with the CLI

#### Example
```yaml
plugins:
    - script: path/to/my/script.sh
    - name: friendly-name
      script: path/to/my-other/script.sh
      target: host
      target_role: all-nodes
```

#### Options

* `script`: **Required** Path to the script you want to run
* `name`: **Optional** Friendly name. By default will be the name of the script file
* `target`: **Optional** Target on where to run the plugin(Default: `spark-container`). Can be `spark-container` or `host`
* `target_role`: **Optional** What should be the role of the node where this script run(Default: `master`). Can be `master`, `worker` or `all-nodes`
