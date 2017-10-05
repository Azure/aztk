# Custom scripts
Custom scripts allow for additional cluster setup steps when the cluster is being provisioned. This is useful
if you want to install additional software, and if you need to modify the default cluster configuration for things such as modifying spark.conf, adding jars or downloading any files you need in the cluster.

You can specify the location of custom scripts on your local machine in `.aztk/cluster.yaml`. If you do not have a `.aztk/` directory in you current working directory, run `aztk spark init` or see [Getting Started](./00-getting-started). Note that the path can be absolute or relative to your current working directory.

The custom scripts can be configured to run on the Spark master only, the Spark workers only, or all nodes in the cluster (Please note that by default, the Spark master node is also a Spark worker). For example, the following custom-script configuration will run 3 custom scripts in the order they are provided:

```yaml
custom-scripts:
    - script: ./custom-scripts/simple.sh
      runOn: all-nodes
    - script: ./custom-scripts/master-only.sh
      runOn: master
    - script: ./custom-scripts/worker-only.sh
      runOn: worker
```

The first script, simple.sh, will run on all nodes and will be executed first. The next script, master-only.sh will run only on nodes that are Spark masters and after simple.sh. The next script, worker-only.sh, will run last and only on nodes that are Spark workers.

Directories may also be provided in the custom-scripts section of `.aztk/cluster.yaml`. 

```yaml
custom-scripts:
    - script: /custom-scripts/
      runOn: all-nodes
```

The above configuration takes the absolute path `/custom-scripts/` and uploads every file within it. These files will all be executed, although order of exection is not guarenteed. If your custom scripts have dependencies, specify the order by providing the full path to the file as seen in the first example.


## Scripting considerations



- The default OS is Ubuntu 16.04.
- The scripts run on the specified nodes in the cluster _after_ Spark has been installed.
- The scripts execute in the order provided
- If a script directory is provided, order of execution is not guarenteed
- The environment variable $SPARK_HOME points to the root Spark directory.
- The environment variable $IS\_MASTER identifies if this is the node running the master role. The node running the master role _also_ runs a worker role on it.
- The Spark cluster is set up using Standalone Mode
