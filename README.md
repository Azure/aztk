# Azure Distributed Data Engineering Toolkit (AZTK)
Azure Distributed Data Engineering Toolkit (AZTK) is a python CLI application for provisioning on-demand Spark on Docker clusters in Azure. It's a cheap and easy way to get up and running with a Spark cluster, and a great tool for Spark users who want to experiment and start testing at scale.

This toolkit is built on top of Azure Batch but does not require any Azure Batch knowledge to use.

## Notable Features
- Spark cluster provision time of 5 minutes on average
- Spark clusters run in Docker containers
- Run Spark on a GPU enabled cluster
- Users can bring their own Docker image
- Ability to use low-priority VMs for an 80% discount
- Mixed Mode clusters that use both low-priority and dedicated VMs
- Built in support for Azure Blob Storage and Azure Data Lake connection
- [Tailored pythonic experience with PySpark, Jupyter, and Anaconda](https://github.com/Azure/aztk/wiki/PySpark-on-Azure-with-AZTK)
- [Tailored R experience with SparklyR, RStudio-Server, and Tidyverse](https://github.com/Azure/aztk/wiki/SparklyR-on-Azure-with-AZTK)
- Ability to run _spark submit_ directly from your local machine's CLI

## Setup

1. Install `aztk` with pip:
```bash
    pip install aztk
```
2. Initialize the project in a directory. This will automatically create a *.aztk* folder with config files in your working directory:
```bash
    aztk spark init
```
3. Login or register for an [Azure Account](https://azure.microsoft.com), navigate to [Azure Cloud Shell](https://shell.azure.com), and run:
```sh
wget -q https://raw.githubusercontent.com/Azure/aztk/v0.8.1/account_setup.sh -O account_setup.sh &&
chmod 755 account_setup.sh &&
/bin/bash account_setup.sh
```

4. Follow the on screen prompts to create the necessary Azure resources and copy the output into your `.aztk/secrets.yaml` file. For more information see [Getting Started Scripts](./01-Getting-Started-Script).


## Quickstart Guide

The core experience of this package is centered around a few commands.

```sh
# create your cluster
aztk spark cluster create
aztk spark cluster add-user
```
```sh
# monitor and manage your clusters
aztk spark cluster get
aztk spark cluster list
aztk spark cluster delete
```
```sh
# login and submit applications to your cluster
aztk spark cluster ssh
aztk spark cluster submit
```

### 1. Create and setup your cluster

First, create your cluster:
```bash
aztk spark cluster create --id my_cluster --size 5 --vm-size standard_d2_v2
```
- See our available VM sizes [here.](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/sizes) 
- The `--vm-size` argument must be the official SKU name which usually come in the form: "standard_d2_v2"
- You can create [low-priority VMs](https://docs.microsoft.com/en-us/azure/batch/batch-low-pri-vms) at an 80% discount by using `--size-low-pri` instead of `--size`
- By default, AZTK runs Spark 2.2.0 on an Ubuntu16.04 Docker image. More info [here](/docker-image)
- By default, AZTK will create a user (with the username **spark**) for your cluster
- The cluster id (`--id`) can only contain alphanumeric characters including hyphens and underscores, and cannot contain more than 64 characters.
- By default, you cannot create clusters of more than 20 cores in total. Visit [this page](https://docs.microsoft.com/en-us/azure/batch/batch-quota-limit#view-batch-quotas) to request a core quota increase.

More information regarding using a cluster can be found in the [cluster documentation](./docs/10-clusters.md)

### 2. Check on your cluster status
To check your cluster status, use the `get` command:
```bash
aztk spark cluster get --id my_cluster
```

### 3. Submit a Spark job

When your cluster is ready, you can submit jobs from your local machine to run against the cluster. The output of the spark-submit will be streamed to your local console. Run this command from the cloned AZTK repo:
```bash
// submit a java application
aztk spark cluster submit \
    --id my_cluster \
    --name my_java_job \
    --class org.apache.spark.examples.SparkPi \
    --executor-memory 20G \
    path\to\examples.jar 1000
    
// submit a python application
aztk spark cluster submit \
    --id my_cluster \
    --name my_python_job \
    --executor-memory 20G \
    path\to\pi.py 1000
```
- The `aztk spark cluster submit` command takes the same parameters as the standard [`spark-submit` command](https://spark.apache.org/docs/latest/submitting-applications.html), except instead of specifying `--master`, AZTK requires that you specify your cluster `--id` and a unique job `--name`
- The job name, `--name`, argument must be at least 3 characters long
    - It can only contain alphanumeric characters including hyphens but excluding underscores
    - It cannot contain uppercase letters
- Each job you submit **must** have a unique name
- Use the `--no-wait` option for your command to return immediately

Learn more about the spark submit command [here](./docs/20-spark-submit.md)

### 4. Log in and Interact with your Spark Cluster
Most users will want to work interactively with their Spark clusters. With the `aztk spark cluster ssh` command, you can SSH into the cluster's master node. This command also helps you port-forward your Spark Web UI and Spark Jobs UI to your local machine:
```bash
aztk spark cluster ssh --id my_cluster --user spark
```
By default, we port forward the Spark Web UI to *localhost:8080*, Spark Jobs UI to *localhost:4040*, and the Spark History Server to *localhost:18080*.

You can configure these settings in the *.aztk/ssh.yaml* file.

NOTE: When working interactively, you may want to use tools like Jupyter or RStudio-Server. To do so, you need to setup your cluster with the appropriate docker image and plugin. See [Plugins](./docs/15-plugins.md) for more information.

### 5. Manage and Monitor your Spark Cluster

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
- [I want to use a different version of Spark](./docs/12-docker-image.md)
- [How do I SSH into my Spark cluster's master node?](./docs/10-clusters.md#ssh-and-port-forwarding)
- [How do I interact with my Spark cluster using a password instead of an SSH-key?](./docs/10-clusters.md#interactive-mode)
- [How do I change my cluster default settings?](./docs/13-configuration.md)
- [How do I modify my *spark-env.sh*, *spark-defaults.conf* or *core-site.xml* files?](./docs/13-configuration.md)
- [How do I use GPUs with AZTK](./docs/60-gpu.md)
- [I'm a python user and want to use PySpark, Jupyter, Anaconda packages, and have a Pythonic experience.](https://github.com/Azure/aztk/wiki/PySpark-on-Azure-with-AZTK)
- [I'm a R user and want to use SparklyR, RStudio, Tidyverse packages, and have an R experience.](https://github.com/Azure/aztk/wiki/SparklyR-on-Azure-with-AZTK)

## Next Steps
You can find more documentation [here](./docs)
