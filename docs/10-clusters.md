# Clusters
In the Azure Distributed Data Engineering Toolkit, a cluster is primarily designed to run Spark jobs. This document describes how to create a cluster to use for Spark jobs. Alternatively for getting started and debugging you can also use the cluster in _interactive mode_ which will allow you to log into the master node and interact with the cluster from there.

## Creating a Cluster
Creating a Spark cluster only takes a few simple steps after which you will be able to SSH into the master node of the cluster and interact with Spark. You will be able to view the Spark Web UI, Spark Jobs UI, submit Spark jobs (with *spark-submit*), and even interact with Spark in a Jupyter notebook.

For the advanced user, please note that the default cluster settings are preconfigured in the *.aztk/cluster.yaml* file that is generated when you run `aztk spark init`. More information on cluster config [here.](./13-configuration.html)

### Commands
Create a Spark cluster:

```sh
aztk spark cluster create --id <your_cluster_id> --vm-size <vm_size_name> --size <number_of_nodes>
```

For example, to create a cluster of 4 *Standard_A2* nodes called 'spark' you can run:
```sh
aztk spark cluster create --id spark --vm-size standard_a2 --size 4
```

You can find more information on VM sizes [here.](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/sizes) Please note that you must use the official SKU name when setting your VM size - they usually come in the form: "standard_d2_v2".

_Note: The cluster id (`--id`) can only contain alphanumeric characters including hyphens and underscores, and cannot contain more than 64 characters. Each cluster **must** have a unique cluster id._

By default, you cannot create clusters of more than 20 cores in total. Visit [this page](https://docs.microsoft.com/en-us/azure/batch/batch-quota-limit#view-batch-quotas) to request a core quota increase.

#### Low priority nodes
You can create your cluster with [low-priority](https://docs.microsoft.com/en-us/azure/batch/batch-low-pri-vms) VMs at an 80% discount by using `--size-low-pri` instead of `--size`. Note that these are great for experimental use, but can be taken away at any time. We recommend against this option when doing long running jobs or for critical workloads.

#### Mixed Mode
You can create clusters with a mixed of [low-priority](https://docs.microsoft.com/en-us/azure/batch/batch-low-pri-vms) and dedicated VMs to reach the optimal balance of price and availability. In Mixed Mode, your cluster will have both dedicated instances and low priority instances. To minimize the potential impact on your Spark workloads, the Spark master node will always be provisioned on one of the dedicated nodes while each of the low priority nodes will be Spark workers.

Please note, to use Mixed Mode clusters, you need to authenticate using Azure Active Directory (AAD) by configuring the Service Principal in `.aztk/secrets.yaml`. You also need to create a [Virtual Network \(VNET\)](https://azure.microsoft.com/en-us/services/virtual-network/), and provide the resource ID to a Subnet within the VNET in your ./aztk/cluster.yaml` configuration file.

#### Setting your Spark and/or Python versions
By default, the Azure Distributed Data Engineering Toolkit will use **Spark v2.2.0** and **Python v3.5.4**. However, you can set your Spark and/or Python versions by [configuring the base Docker image used by this package](./12-docker-image.html).

### Listing clusters
You can list all clusters currently running in your account by running

```sh
aztk spark cluster list
```

### Viewing a cluster
To view details about a particular cluster run:

```sh
aztk spark cluster get --id <your_cluster_id>
```

Note that the cluster is not fully usable until a master node has been selected and it's state is `idle`.

For example here cluster 'spark' has 2 nodes and node `tvm-257509324_2-20170820t200959z` is the master and ready to run a job.

```sh
Cluster         spark
------------------------------------------
State:          active
Node Size:      standard_a2
Nodes:          2
| Dedicated:    2
| Low priority: 0

Nodes                               | State           | IP:Port              | Master
------------------------------------|-----------------|----------------------|--------
tvm-257509324_1-20170820t200959z    | idle            | 40.83.254.90:50001   |
tvm-257509324_2-20170820t200959z    | idle            | 40.83.254.90:50000   | *
```

### Deleting a cluster
To delete a cluster run:

```sh
aztk spark cluster delete --id <your_cluster_id>
```
Deleting a cluster also permanently deletes any data or logs associated with that cluster. If you wish to persist this data, use the `--keep-logs` flag.

To delete all clusters:
```sh
aztk spark cluster delete --id $(aztk spark cluster list -q)
```

Skip delete confirmation by using the `--force` flag.

__You are charged for the cluster as long as the nodes are provisioned in your account.__ Make sure to delete any clusters you are not using to avoid unwanted costs.

### Run a command on all nodes in the cluster
To run a command on all nodes in the cluster, run:
```sh
aztk spark cluster run --id <your_cluster_id> "<command>"
```

The command is executed through an SSH tunnel.

### Run a command on a specific node in the cluster
To run a command on all nodes in the cluster, run:
```sh
aztk spark cluster run --id <your_cluster_id> --node-id <your_node_id> "<command>"
```
This command is executed through a SSH tunnel.
To get the id of nodes in your cluster, run `aztk spark cluster get --id <your_cluster_id>`.

### Copy a file to all nodes in the cluster
To securely copy a file to all nodes, run:
```sh
aztk spark cluster copy --id <your_cluster_id> --source-path </path/to/local/file> --dest-path </path/on/node>
```

The file will be securely copied to each node using SFTP.

### Interactive Mode

All other interaction with the cluster is done via SSH and SSH tunneling. If you didn't create a user during cluster create (`aztk spark cluster create`), the first step is to add a user to each node in the cluster.

Make sure that the *.aztk/secrets.yaml* file has your SSH key (or path to the SSH key), and it will automatically use it to make the SSH connection.

```sh
aztk spark cluster add-user --id spark --username admin
```

Alternatively, you can add the SSH key as a parameter when running the `add-user` command.
```sh
aztk spark cluster add-user --id spark --username admin --ssh-key <your_key_OR_path_to_key>
```

You can also use a __password__ to create your user:
```sh
aztk spark cluster add-user --id spark --username admin --password <my_password>
```

_Using a SSH key is the recommended method._

### SSH and Port Forwarding
After a user has been created, SSH into the Spark container on the master node with:

```sh
aztk spark cluster ssh --id spark --username admin
```

If you would like to ssh into the host instead of the Spark container on it, run:

```sh
aztk spark cluster ssh --id spark --username admin --host
```

If you ssh into the host and wish to access the running Docker Spark environment, you can run the following:
```sh
sudo docker exec -it spark /bin/bash
```

Now that you're in, you can change directory to your familiar `$SPARK_HOME`
```sh
cd $SPARK_HOME
```

To view the SSH command being called, pass the `--no-connect` flag:
```
aztk spark cluster ssh --id spark --no-connect
```

Note that an SSH tunnel and shell will be opened with the default SSH client if one is present. Otherwise, a pure python SSH tunnel is created to forward the necessary ports. The pure python SSH tunnel will not open a shell.


### Debugging your Spark Cluster

If your cluster is in an unknown or unusable state, you can debug by running:

```sh
aztk spark cluster debug --id <cluster-id> --output </path/to/output/directory/>
```

The debug utility will pull logs from all nodes in the cluster. The utility will check for:
- free diskspace
- docker image status
- docker container status
- docker container logs
- docker container process status
- aztk code & version
- spark component logs (master, worker, shuffle service, history server, etc) from $SPARK_HOME/logs
- spark application logs from $SPARK_HOME/work

__Please be careful sharing the output of the `debug` command as secrets and application code are present in the output.__

Pass the `--brief` flag to only download the most essential logs from each node:
```sh
aztk spark cluster debug --id <cluster-id> --output </path/to/output/directory/> --brief
```
This command will retrieve:
- stdout file from the node's startup
- stderr file from the node's startup
- the docker log for the spark container


### Interact with your Spark cluster
By default, the `aztk spark cluster ssh` command port forwards the Spark Web UI to *localhost:8080*, Spark Jobs UI to *localhost:4040*, and Spark History Server to your *localhost:18080*. This can be [configured in *.aztk/ssh.yaml*](../docs/13-configuration.html#sshyaml).

## Next Steps
- [Run a Spark job](20-spark-submit.html)
- [Configure the Spark cluster using custom plugins](51-define-plugin.html)
- [Bring your own Docker image or choose between a variety of our supported base images to manage your Spark and Python versions](12-docker-image.html)
