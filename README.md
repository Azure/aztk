# Distributed Tools for Data Engineering (DTDE)
A suite of distributed tools to help engineers scale their work into Azure.

# Spark on DTDE

## Setup
1. Clone the repo
2. Use pip to install required packages:
```bash
    pip install -r requirements.txt
```
3. Use setuptools:
```bash
    pip install -e .
```
4. Rename 'secrets.cfg.template' to 'secrets.cfg' and fill in the fields for your Batch account and Storage account. These fields can be found in the Azure portal, and in the [Getting Started](./docs/00-getting-started.md) docs.

   To complete this step, you will need an Azure account that has a Batch account and Storage account:
    - To create an Azure account: https://azure.microsoft.com/free/
    - To create a Batch account: https://docs.microsoft.com/en-us/azure/batch/batch-account-create-portal
    - To create a Storage account: https://docs.microsoft.com/en-us/azure/storage/storage-create-storage-account



## Getting Started

The entire experience of this package is centered around a few commands.

### Create and setup your cluster

First, create your cluster:
```bash
azb spark cluster create \
    --id <my-cluster-id> \
    --size <number of nodes> \
    --vm-size <vm-size> \
    --custom-script <path to custom bash script to run on each node> (optional) \
    --wait/--no-wait (optional)
```

You can also create your cluster with [low-priority](https://docs.microsoft.com/en-us/azure/batch/batch-low-pri-vms) VMs at an 80% discount by using **--size-low-pri** instead of **--size**:
```
azb spark cluster create \
    --id <my-cluster-id> \
    --size-low-pri <number of low-pri nodes> \
    --vm-size <vm-size>
```

By default, this package runs Spark in docker from an ubuntu16.04 base image on a ubuntu16.04 VM. More info on this image can be found in the **docker-images** folder in this repo.

You can also add a user directly in this command using the same inputs as the `add-user` command described bellow.

#### Add a user to your cluster to connect
When your cluster is ready, create a user for your cluster (if you didn't already do so when creating your cluster):
```bash
# **Recommended usage**
# Add a user with a ssh public key. It will use the value specified in the secrets.cfg (Either path to the file or the actual key)
azb spark cluster add-user \
    --id <my-cluster-id> \
    --username <username>

# You can also explicity specify the ssh public key(Path or actual key)
azb spark cluster add-user \
    --id <my-cluster-id> \
    --username <username> \
    --ssh-key ~/.ssh/id_rsa.pub

# **Not recommended**
# You can also just specify a password
azb spark cluster add-user \
    --id <my-cluster-id> \
    --username <username> \
    --password <password>

```

NOTE: The cluster id (--id) can only contain alphanumeric characters including hyphens and underscores, and cannot contain more than 64 characters.

More information regarding using a cluster can be found in the [cluster documentation](./documentation/10%20-%20Clusters.md)


### Submit a Spark job

Now you can submit jobs to run against the cluster:
```
azb spark app submit \
    --id <my-cluster-id> \
    --name <my-job-name> \
    [options] \
    <app jar | python file> \
    [app arguments]
```
NOTE: The job name (--name) must be atleast 3 characters long, can only contain alphanumeric characters including hyphens but excluding underscores, and cannot contain uppercase letters.

The output of spark-submit will be streamed to the console. Use the `--no-wait` option to return immediately.

### Read the output of your spark job.

If you decided not to tail the log when submiting the job or want to read it again you can use this command.

```bash
azb spark app logs \
    --id <my-cluster-id> \
    -- name <my-job-name>
    [--tail] # If you want it to tail the log if the task is still runing
```
More information regarding using a cluster can be found in the [spark submit documentation](./documentation/20%20-%20Spark%20Submit.md)

### Connect your cluster to Azure Blob Storage (WASB connection)

Pre-built into this package is native support for connecting your spark cluster to Azure Blob Storage. To do so, make sure that the storage fields in your **secrets.cfg** file are properly filled out. 

Even if you are just testing and have no need to connect with Azure Blob Storage, you still need to correctly fill out the storage fields in your **secrets.cfg** folder as it is a requirement for this package.

Once you have correctly filled out the **secrets.cfg** with your storage credentials, you will be able to access said storage account from your Spark job. 

Please note: If you want to access another Azure Blob Storage account, you will need to recreate your cluster with an updated **secrets.cfg** file with the appropriate storage credentials.

Here's an example of how you may access your data in Blob Storage:

``` python
df = spark.read.csv("wasbs://<STORAGE_CONTAINER_NAME>@<STORAGE_ACCOUNT_NAME>.blob.core.windows.net/<BLOB_NAME>")
```

### Manage your Spark cluster

You can also see your clusters from the CLI:
```
azb spark cluster list
```

And get the state of any specified cluster:
```
azb spark cluster get --id <my-cluster-id>
```

Finally, you can delete any specified cluster:
```
azb spark cluster delete --id <my-cluster-id>
```

### Examples

Please see the samples folder for a curated list of samples from Spark-2.2.0.

## Next Steps
You can find more documentation [here](./documentation)
