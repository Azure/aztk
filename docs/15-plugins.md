# Plugins

## Supported Plugins
AZTK ships with a library of default plugins that enable auxillary services to use with your Spark cluster.

Currently the following plugins are supported:

- JupyterLab
- Jupyter
- HDFS
- RStudioServer
- Spark UI Proxy

### Enable a plugin using the CLI
If you are uing the `aztk` CLI and wish to enable a supported plugin, you need to update you `.aztk/cluster.yaml` configuration file.

Add or uncomment the `plugins` section and set the plugins you desire to enable as follows:
```yaml
plugins:
    - name: jupyterlab
    - name: jupyter
    - name: hdfs
    - name: spark_ui_proxy
    - name: rsutio_server
      version: "1.1.383"
```

### Enable a plugin using the SDK
If you are uing the `aztk` SDK and wish to enable a supported plugin, you need to import the necessary plugins from the `aztk.spark.models.plugin` module and add them to your ClusterConfiguration object's plugin list:
```python
from aztk.spark.models.plugins import RStudioServerPlugin, HDFSPlugin
cluster_config = ClusterConfiguration(
  ...# Other config,
  plugins=[
    JupyterPlugin(),
    RStudioServerPlugin(version="1.1.383"),
    HDFSPlugin(),
  ]
)
```
