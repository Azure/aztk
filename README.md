# Azure Distributed Data Engineering Toolkit
Azure Distributed Data Engineering Toolkit is a python CLI application for provisioning on-demand Spark on Docker clusters in Azure. It's a cheap and easy way to get up and running with a Spark cluster, and a great tool for Spark users who want to experiment and start testing at scale. 

This toolkit is built on top of Azure Batch but does not require any Azure Batch knowledge to use. 

Currently, this toolkit is designed to run batch Spark jobs that require additional on-demand compute. Eventually we plan to support other distributed data engineering frameworks in a similar vein. Please let us know which frameworks you'd like for us to support in the future. 

## Notable Features
- Spark cluster provision time of 5 minutes on average
- Spark clusters run in Docker containers
- Users can bring their own Docker image
- Ability to use low-priority VMs for an 80% discount
- Built in support for Azure Blob Storage connection
- Built in Jupyter notebook for interactive experience
- Ability to run _spark submit_ directly from your local machine's CLI

## Setup
1. Clone the repo
```bash
    git clone -b stable https://www.github.com/azure/aztk
    
    # You can also clone directly from master to get the latest bits
    git clone https://www.github.com/azure/aztk
```
2. Use pip to install required packages (requires python 3.5+ and pip 9.0.1+)
```bash
    pip install -r requirements.txt
```
3. Use setuptools:
```bash
    pip install -e .
```
4. Initialize the project in a directory [This will automatically create a *.aztk* folder with config files in your working directory]:
```bash
    aztk spark init
```
5. Fill in the fields for your Batch account and Storage account in your *.aztk/secrets.yaml* file. (We'd also recommend that you enter SSH key info in this file)

   This package is built on top of two core Azure services, [Azure Batch](https://azure.microsoft.com/en-us/services/batch/) and [Azure Storage](https://azure.microsoft.com/en-us/services/storage/). Create those resources via the portal (see [Getting Started](./docs/00-getting-started.md)).

## Quickstart Guide

The core experience of this package is centered around a few commands.

```sh
# create your cluster
aztk spark cluster create
```
```sh
# monitor and manage your clusters
aztk spark cluster get
aztk spark cluster list
aztk spark cluster delete
```
```sh
# login and submit jobs to your cluster
aztk spark cluster ssh
aztk spark cluster submit
```

### Create and setup your cluster

First, create your cluster:
```bash
aztk spark cluster create \
    --id <my_cluster_id> \
    --size <number_of_nodes> \
    --vm-size <vm_size>
```
You can find more information on VM sizes [here.](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/sizes) Please note that you must use the official SKU name when setting your VM size - they usually come in the form: "standard_d2_v2". 

You can also create your cluster with [low-priority](https://docs.microsoft.com/en-us/azure/batch/batch-low-pri-vms) VMs at an 80% discount by using `--size-low-pri` instead of `--size` (we have to set `--size 0` as we currently do not support mixed low-priority and dedicated VMs):
```
aztk spark cluster create \
    --id <my_cluster_id> \
    --size 0 \
    --size-low-pri <number_of_low-pri_nodes> \
    --vm-size <vm_size>
```

By default, this package runs Spark 2.2.0 with Python 3.5 on an Ubuntu16.04 Docker image. More info on this image can be found in the [docker-images](/docker-image) folder in this repo.

NOTE: The cluster id (`--id`) can only contain alphanumeric characters including hyphens and underscores, and cannot contain more than 64 characters.

More information regarding using a cluster can be found in the [cluster documentation](./docs/10-clusters.md)

### Check on your cluster status
To check your cluster status, use the `get` command:
```bash
aztk spark cluster get --id <my_cluster_id>
```

### Submit a Spark job

When your cluster is up, you can submit jobs to run against the cluster:
```bash
aztk spark cluster submit \
    --id <my_cluste_id> \
    --name <my_job_name> \
    [options] \
    <app jar | python file> \
    [app arguments]
```
NOTE: The job name (`--name`) must be atleast 3 characters long, can only contain alphanumeric characters including hyphens but excluding underscores, and cannot contain uppercase letters. Each job you submit **must** have a unique name.

The output of spark-submit will be streamed to the console. Use the `--no-wait` option to return immediately. More information regarding monitoring your job can be found in the [spark submit documentation.](./docs/20-spark-submit.md)

To start testing this package, you can start by trying out a Spark job from the [./examples](./examples) folder. The examples are a curated list of samples from Spark-2.2.0.

### Log in and Interact with your Spark Cluster
Most users will want to work interactively with their Spark clusters. With the `aztk spark cluster ssh` command, you can SSH into the cluster's master node. This command also helps you port-forward your Spark Web UI and Spark Jobs UI to your local machine:
```bash
aztk spark cluster ssh --id <my_cluster_id>
```
By default, we port forward the Spark Web UI to *localhost:8080*, Spark Jobs UI to *localhost:4040*, and Jupyter to *localhost:8888*.

You can configure these settings in the *.aztk/ssh.yaml* file.

### Manage your Spark cluster

You can also see your clusters from the CLI:
```
aztk spark cluster list
```

And get the state of any specified cluster:
```
aztk spark cluster get --id <my_cluster_id>
```

Finally, you can delete any specified cluster:
```
aztk spark cluster delete --id <my_cluster_id>
```

## FAQs
- [How do I connect to Azure Storage (WASB)?](./docs/30-cloud-storage.md)
- [I want to use a different version of Spark / Python](./docs/12-docker-image.md)
- [How do I SSH into my Spark cluster's master node?](./docs/10-clusters.md#ssh-and-port-forwarding)
- [How do I interact with my Spark cluster using a password instead of an SSH-key?](./docs/10-clusters.md#interactive-mode)
- [How do I change my cluster default settings?](./docs/13-configuration.md)
- [How do I modify my *spark-env.sh* or *spark-defaults.conf* files?](./docs/13-configuration.md)

## Next Steps
You can find more documentation [here](./docs)
