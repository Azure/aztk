# Configuration Files
This section refers to the files in the directory *.aztk* that are generated from the `aztk spark init` command.

## *cluster.yaml*

The core settings for a cluster are configured in the *cluster.yaml* file. Once you have set your desired values in *.aztk/cluster.yaml*, you can create a cluster using `aztk spark cluster create`.

This is the default cluster configuration:

```yaml
# id: <id of the cluster to be created>
id: spark_cluster

# Toolkit configuration [Required] You can use `aztk toolkit` command to find which toolkits are available
toolkit:
  software: spark
  version: 2.2
  # environment: python
  # Optional version for the environment
  # environment_version:

  # Optional docker repository(To bring your custom docker image. Just specify the Toolkit software, version and environment if using default images)
  # docker_repo: <name of docker image repo (for more information, see https://github.com/Azure/aztk/blob/master/docs/12-docker-image.md)>

  # Optional command line options to pass to `docker run`
  # docker_run_options: <additional command line options to pass to `docker run` (for more information, see https://github.com/Azure/aztk/blob/master/docs/12-docker-image.md)>

# vm_size: <vm-size, see available options here: https://azure.microsoft.com/pricing/details/batch//>
vm_size: standard_a2

# size: <number of dedicated nodes in the cluster, not that clusters must contain all dedicated or all low priority nodes>
size: 2

# size_low_priority: <number of low priority nodes in the cluster, mutually exclusive with size setting>

# username: <username for the linux user to be created> (optional)
username: spark

# Enable plugins
plugins:
  # - name: spark_ui_proxy
  # - name: jupyterlab
  # - name: jupyter
  # - name: hdfs
  # - name: rstudio_server

# Allow master node to also be a worker <true/false> (Default: true)
# worker_on_master: true


# wait: <true/false>
wait: true
```
<!--- this goes about wait: true
# Where do you want to run the driver <dedicated/master/any> (Default: dedicated if at least one dedicated node or any otherwise)
# scheduling_target: dedicated
-->

Running `aztk spark cluster create` will create a cluster of 4 **Standard\_A2** nodes called 'spark\_cluster' with a linux user named 'spark'. This is equivalent to running the command

```sh
aztk spark cluster create --id spark --vm-size standard_a2 --size 4 --username spark --wait
```

NOTE: This assumes that your SSH-key is configured in the *.aztk/secrets.yaml* file.

## *ssh.yaml*

This is the default ssh cluster configuration:
```yaml
# username: <name of the user account to ssh into>
username: spark

# job_ui_port: <local port where the job ui is forwarded to>
job_ui_port: 4040

# job_history_ui_port: <local port where the job history ui is forwarded to>
job_history_ui_port: 18080

# web_ui_port: <local port where the spark master web ui is forwarded to>
web_ui_port: 8080

# jupyter_port: <local port which where jupyter is forwarded to>
jupyter_port: 8888

# name_node_ui_port: <local port which where Name Node UI is forwarded to>
name_node_ui_port: 50070

# rstudio_server_port: <local port which where rstudio server is forwarded to>
rstudio_server_port: 8787

# connect: <true/false, connect to spark master or print connection string (--no-connect)>
connect: true
```

Running the command `aztk spark cluster ssh --id <cluster_id>` will ssh into the master node of the Spark cluster. It will also forward the Spark Job UI to localhost:4040, the Spark master's web UI to localhost:8080, and Jupyter to localhost:8888.

Note that all of the settings in ssh.yaml will be overridden by parameters passed on the command line.

## Spark Configuration

The repository comes with default Spark configuration files which provision your Spark cluster just the same as you would locally. After running `aztk spark init` to initialize your working environment, you can view and edit these files at `.aztk/spark-defaults.conf`, `.aztk/spark-env.sh` and `.aztk/core-site.xml`. Please note that you can bring your own Spark configuration files by copying your `spark-defaults.conf`, `spark-env.sh` and `core-site.xml` into your `.aztk/` directory.

If using `aztk` job submission, please note that both `spark.shuffle.service.enabled` and `spark.dynamicAllocation.enabled` must be set to true so that the number of executors registered with an application can scale as nodes in the job's cluster come online.

The following settings available in `spark-defaults.conf` and `spark-env.sh` are not supported:

`spark-env.sh`:
- SPARK\_LOCAL\_IP
- SPARK\_PUBLIC\_DNS
- SPARK\_MASTER\_HOST
- SPARK\_MASTER\_PORT
- SPARK\_WORKER\_PORT
- SPARK\_MASTER\_WEBUI\_PORT
- Any options related to YARN client mode or Mesos

`spark-defaults.conf`:
- spark.master

### History Server
If you want to use Spark's history server, please set the following values in your `.aztk/spark-defaults.conf` file:
```
spark.eventLog.enabled          true
spark.eventLog.dir              <path>
spark.history.fs.logDirectory   <path>
 ```

Please note that the path for `spark.eventLog.dir` and `spark.history.fs.logDirectory` should most likely match so that the history server reads the logs that each Spark job writes. Also note that while the paths can be local (`file:/`), it is recommended that the paths be accessible by every node in the cluster so that the history server, which runs on the Spark master node, has access to all application logs. HDFS, WASB, ADL, or any other Hadoop API compliant storage system may be used.

If using WASB, ADL or other cloud storage services, be sure to set your keys in `.aztk/core-site.xml`. For more information, see the [Cloud Storage](./30-cloud-storage.html) documentation.


## Configuring Spark Storage

The Spark cluster can be configured to use different cloud supported storage offerings (such as Azure Storage Blobs, Azure Data Lake Storage, or any other supported Spark file system). More information can be found in the [Cloud Storage](./30-cloud-storage.html) documentation.

## Placing JARS

Additional JAR files can be added to the cluster by simply adding them to the *.aztk/jars* directory. These JARS will automatically be added to Spark's default JAR directory. In the case of a naming conflict, the file in *.aztk/jars* will **overwrite** the file in the cluster. Typically new JARS must be registered with Spark. To do this, either run the Spark Submit command with a path to the JARS

```sh
aztk spark cluster submit --id <my_cluster_id> --jars $SPARK_HOME/jars/my_jar_file_1.jar <my_application> <my_parameters>
```

Or update the *.aztk/spark-default.conf* file as shown below to have it registered for all Spark applications.

```sh
spark.jars $spark_home/jars/my_jar_file_1.jar,$spark_home/jars/my_jar_file_2.jar
````

Note: _This tool automatically registers several JARS for default cloud storage in the spark-default.conf file. If you want to modify this file, simply append any additional JARS to the end of this list_.


## Next Steps
- [Add plugins](./15-plugins.html)
- [Set up your Cloud Storage](./30-cloud-storage.html)
