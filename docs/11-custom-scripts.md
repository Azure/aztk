# Custom scripts
Custom scripts allow for additional cluster setup steps when the cluster is being provisioned. This is useful
when you want to modify the default cluster configuration for things such as modifying spark.conf, adding jars
or downloading any files you need in the cluster.

## Scripting considerations

- The default OS is Ubuntu 16.04.
- The script run on every node in the cluster _after_ Spark has been installed and is running.
- The environment variable $SPARK_HOME points to the root Spark directory.
- The environment variable $IS\_MASTER identifies if this is the node running the master role. The node running the master role _also_ runs a worker role on it.
- The Spark cluster is set up using Standalone Mode
