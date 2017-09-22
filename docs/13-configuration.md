# Configuration Files

## Cluster Configuration

The core settings for a cluster are configured in the cluster.yaml file. Once you have set your desired values in cluster.yaml, you can create a cluster using `azb spark cluster create`. 

For example, with the default cluster configuration:

```yaml
id: my_spark_cluster
vm_size: standard_a2
size: 2
username: spark
wait: true
```

Running `azb spark cluster create` will create a cluster of 4 Standard\_A2 nodes called 'my\_spark\_cluster' with a linux user named 'spark'. This is equivalent to running the command

```sh
azb spark cluster create --id spark --vm-szie standard_a2 --size 4 --username spark --wait
```

## Secrets Configuration

A template file for necessary secrets is given in config/secrets.yaml.template. After running `azb spark init`, this file will be copied to a .thunderbolt/ directory in your current working directory. Copy or rename the file to .thunderbolt/secrets.yaml and fill in the proper values for your Batch and Storage accounts. See [Getting Started] (./00-getting-started.md) for more information.   

## SSH Configuration

The SSH connection settings can be configured in the ssh.yaml file. Once you have set your desired values in ssh.yaml, you can connect to the master of your cluster using the command `azb spark cluster ssh`. 

For example, with the default ssh cluster configuration:
```yaml
# ssh configuration

# username: <name of the user account to ssh into>
username: spark

# job_ui_port: <local port where the job ui is forwarded to>
job_ui_port: 4040

# web_ui_port: <local port where the spark master web ui is forwarded to>
web_ui_port: 8080

# jupyter_port: <local port which where jupyter is forwarded to>
jupyter_port: 8088
```

Running the command `azb spark cluster ssh --id <cluster_id>` will attempt to ssh into the cluster which has the id specified with the username 'spark'. It will forward the Spark Job UI to localhost:4040, the Spark master's web UI to localhost:8080 and Jupyter to localhost:8088.

Note that all of the settings in ssh.yaml will be overrided by parameters passed on the command line.
