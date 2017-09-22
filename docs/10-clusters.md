# Clusters
A Cluster in Thunderbolt is primarily designed to run Spark jobs. This document describes how to create a cluster
to use for spark job submissions. Alternitavely for getting started and debugging you can also use the cluster
in _interactive mode_ which will allow you to log into the master node, use Jupyter and view the Spark UI.

## Creating a Cluster
Create a spark cluster only takes a few simple steps after which you will be
able to log into the master node of the cluster an interact with Spark in a
Jupyter notebook, view the Spark UI on you local machine or submit a job.

### Commands
Create a cluster:

```sh
azb spark cluster create --id <your_cluster_id> --vm-size <vm_size_name> --size <number_of_nodes>
```

For example, to create a cluster of 4 Standard_A2 nodes called 'spark' you can run:
```sh
azb spark cluster create --id spark --vm-size standard_a2 --size 4
```

You can find more information on VM sizes [here](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/sizes)

NOTE: The cluster id (--id) can only contain alphanumeric characters including hyphens and underscores, and cannot contain more than 64 characters.

#### Low priority nodes
You can create your cluster with [low-priority](https://docs.microsoft.com/en-us/azure/batch/batch-low-pri-vms) VMs at an 80% discount by using **--size-low-pri** instead of **--size**. Note that these are great for experimental use, but can be taken away at any time. We recommend against this option when doing long running jobs or for critical workloads.

#### Setting your Spark and/or Python versions
By default, Azure Thunderbolt will use **Spark v2.2.0** and **Python v3.5.4**. However, you can set your Spark and/or Python versions by [configuring the Docker image that is used by Azure Thunderbolt](./12-docker-image.md).

### Listing clusters
You can list all clusters currently running in your account by running

```sh
azb spark cluster list
```

### Viewing a cluster
To view details about a particular cluster run:

```sh
azb spark cluster get --id <your_cluster_id>
```

Note that the cluster is not fully usable until a master node has been selected and it's state is 'idle'.

For example here cluster 'spark' has 2 nodes and node tvm-257509324_2-20170820t200959z is the mastesr and ready to run a job.

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
azb spark cluster delete --id <your_cluster_id>
```

__You are charged for the cluster as long as the nodes are provisioned in your account.__ Make sure to delete any clusters you are not using to avoid unwanted costs.

### Interactive Mode
All interaction to the cluster is done via SSH and SSH tunneling. The first step to enable this is to add
a user to the master node.

Using a __SSH key__
```sh
azb spark cluster add-user --id spark --username admin --ssh-key <your_key_OR_path_to_key>
```

Alternatively, updating the secrets.yaml with a the SSH key or path to the SSH will allow the tool to automatically
pick it up.

```sh
azb spark cluster add-user --id spark --username admin
```

Using a __password__
```sh
azb spark cluster add-user --id spark --username admin --password my_password
```

_Using passwords is discouraged over using a SSH key._

### SSH and Port Forwarding
After a user has been created, SSH into the master node with:

```sh
azb spark cluster ssh --id spark --username admin
```

For interactive use with the cluster, port forwarding of certain ports is required to enable viewing the Spark Master UI,
Spark Jobs UI and the Jupyter notebook in the cluster:

```sh
azb spark cluster ssh --id spark --username admin --masterui 8080 --webui 4040 --jupyter 8888
```

You can also forward any other ports the same way you would do with ssh

```sh
# This will forward the remote port 5678 to the local port 1234
azb spark cluster ssh --id spark --username admin -L 1234:localhost:5678

# You can use this option multiple time to forward multiple ports
azb spark cluster ssh --id spark --username admin -L 1234:localhost:5678  -L 1235:localhost:5679
```

### Interact with your Spark cluster

### Jupyter
Once the appropriate ports have been forwarded, simply navigate to the local ports for viewing. In
this case, if you used port 8888 for Jupyter then navigate to [http://localhost:8888.](http://localhost:8888)

__The notebooks will only be persisted to the local cluster.__ Once the cluster is deleted, all notebooks
will be deleted with them. We recommend saving off the notebooks elsewhere if you do not want them
deleted.

## Next Steps
- [Run a Spark job](./20-spark-submit.md)
- [Configure the Spark cluster using custom commands](./11-custom-scripts.md)
- [Bring your own Docker image or choose between a variety of our supported base images to manage your Spark and Python versions](./12-docker-image.md)
