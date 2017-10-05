# Configuration Files
This section refers to the files in the directory *.aztk* that are generated from the `aztk spark init` command.

## *cluster.yaml*

The core settings for a cluster are configured in the *cluster.yaml* file. Once you have set your desired values in *.aztk/cluster.yaml*, you can create a cluster using `aztk spark cluster create`. 

This is the default cluster configuration:

```yaml
# id: <id of the cluster to be created>
id: spark_cluster

# vm_size: <vm-size, see available options here: https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/>
vm_size: standard_a2

# size: <number of dedicated nodes in the cluster, not that clusters must contain all dedicated or all low priority nodes>
size: 2

# size_low_pri: <number of low priority nodes in the cluster, mutually exclusive with size setting>

# username: <username for the linux user to be created> (optional)
username: spark

# docker_repo: <name of docker image repo (for more information, see https://github.com/Azure/aztk/blob/master/docs/12-docker-image.md)>
docker_repo: jiata/aztk:0.1.0-spark2.2.0-python3.5.4

# custom_script: <path to custom script to run on each node> (optional)

# wait: <true/false>
wait: true
```

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

# web_ui_port: <local port where the spark master web ui is forwarded to>
web_ui_port: 8080

# jupyter_port: <local port which where jupyter is forwarded to>
jupyter_port: 8088
```

Running the command `aztk spark cluster ssh --id <cluster_id>` will ssh into the master node of the Spark cluster. It will also forward the Spark Job UI to localhost:4040, the Spark master's web UI to localhost:8080, and Jupyter to localhost:8888.

Note that all of the settings in ssh.yaml will be overrided by parameters passed on the command line.

## Spark Configuration

The repository comes with default Spark configuration files which provision your Spark cluster just the same as you would locally. After running `aztk spark init` to initialize your working environment, you can view and edit these files at `.aztk/spark-defaults.conf` and `.aztk/spark-env.sh`. Please note that you can bring your own Spark configuration files by copying your `spark-defaults.conf` and `spark-env.sh` into your `.aztk/` direcotry.

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

Also note that this toolkit pre-loads wasb jars, so loading them elsewhere is not necessary.
