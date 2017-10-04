# Clusters
In the Azure Distributed Data Engineering Toolkit, a cluster is primarily designed to run Spark jobs. This document describes how to create a cluster to use for Spark jobs. Alternitavely for getting started and debugging you can also use the cluster in _interactive mode_ which will allow you to log into the master node, use Jupyter and view the Spark UI.

## Creating a Cluster
Creating a Spark cluster only takes a few simple steps after which you will be able to SSH into the master node of the cluster and interact with Spark. You will be able to view the Spark Web UI, Spark Jobs UI, submit Spark jobs (with *spark-submit*), and even interact with Spark in a Jupyter notebook.

For the advanced user, please note that the default cluster settings are preconfigured in the *.aztk/cluster.yaml* file that is generated when you run `aztk spark init`. More information on cluster config [here.](../13-configuration.md)

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

NOTE: The cluster id (`--id`) can only contain alphanumeric characters including hyphens and underscores, and cannot contain more than 64 characters. Each cluster **must** have a unique cluster id.

#### Low priority nodes
You can create your cluster with [low-priority](https://docs.microsoft.com/en-us/azure/batch/batch-low-pri-vms) VMs at an 80% discount by using `--size-low-pri` instead of `--size`. Note that these are great for experimental use, but can be taken away at any time. We recommend against this option when doing long running jobs or for critical workloads.

#### Setting your Spark and/or Python versions
By default, the Azure Distributed Data Engineering Toolkit will use **Spark v2.2.0** and **Python v3.5.4**. However, you can set your Spark and/or Python versions by [configuring the base Docker image used by this package](./12-docker-image.md).

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

For example here cluster 'spark' has 2 nodes and node `tvm-257509324_2-20170820t200959z` is the mastesr and ready to run a job.

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

__You are charged for the cluster as long as the nodes are provisioned in your account.__ Make sure to delete any clusters you are not using to avoid unwanted costs.

### Interactive Mode
All interaction to the cluster is done via SSH and SSH tunneling. If you didn't create a user during cluster create (`aztk spark cluster create`), the first step is to enable to add a user to the master node.

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

### Interact with your Spark cluster
By default, the `aztk spark cluster ssh` command port forwards the Spark Web UI to *localhost:8080*, Spark Jobs UI to *localhost:4040*, and Jupyter to your *locahost:8888*. This can be [configured in *.aztb/ssh.yaml*](../docs/13-configuration.md##sshyaml).

### Jupyter
Once the appropriate ports have been forwarded, simply navigate to the local ports for viewing. In this case, if you used port 8888 (the default) for Jupyter then navigate to [http://localhost:8888.](http://localhost:8888)

__The notebooks will only be persisted to the local cluster.__ Once the cluster is deleted, all notebooks will be deleted with them. We recommend saving the notebooks elsewhere if you do not want them deleted.

## Next Steps
- [Run a Spark job](./20-spark-submit.md)
- [Configure the Spark cluster using custom commands](./11-custom-scripts.md)
- [Bring your own Docker image or choose between a variety of our supported base images to manage your Spark and Python versions](./12-docker-image.md)
