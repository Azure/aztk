# Distributed Tools for Data Engineering (DTDE)
A suite of distributed tools to help engineers scale their work into Azure.

# Spark on DTDE

## Setup  
1. Clone the repo
2. Use pip to install required packages:
    ```
    pip3 install -r requirements.txt
    ```
3. Use setuptools:
    ```
    python3 setup.py install
    ```
4. Rename 'configuration.cfg.template' to 'configuration.cfg' and fill in the fields for your Batch account and Storage account. These fields can be found in the Azure portal. 

   To complete this step, you will need an Azure account that has a Batch account and Storage account:
    - To create an Azure account: https://azure.microsoft.com/free/
    - To create a Batch account: https://docs.microsoft.com/en-us/azure/batch/batch-account-create-portal
    - To create a Storage account: https://docs.microsoft.com/en-us/azure/storage/storage-create-storage-account

## Getting Started

The entire experience of this package is centered around a few commands in the bin folder.

### Create and setup your cluster

First, create your cluster:
```
./bin/spark-cluster-create \
    --id <my-cluster-id> \
    --size <number of nodes> \
    --vm-size <vm-size> \
    --custom-script <path to custom bash script to run on each node> (optional) \
    --wait/--no-wait (optional)
```

You can also create your cluster with [low-priority](https://docs.microsoft.com/en-us/azure/batch/batch-low-pri-vms) VMs at an 80% discount by using **--size-low-pri** instead of **--size**:
```
./bin/spark-cluster-create \
    --id <my-cluster-id> \
    --size-low-pri <number of low-pri nodes>
    --vm-size <vm-size>
```

When your cluster is ready, create a user for your cluster:
```
./bin/spark-cluster-create-user \
    --id <my-cluster-id> \
    --username <username> \
    --password <password>
```

### Submit a Spark job

Now you can submit jobs to run against the cluster:
```
./bin/spark-submit \
    --id <my-cluster-id> \
    --name <my-job-name> \
    [options] 
    <app jar | python file> 
    [app arguments]
```

### Interact with your Spark cluster

To view the spark UI, open up an ssh tunnel with the "masterui" option and a local port to map to:
```
./bin/spark-cluster-ssh \ 
    --id <my-cluster-id> \
    --masterui <local-port> \
    --username <user-name>
```

Optionally, you can also open up a jupyter notebook with the "jupyter" option to work in:
```
./bin/spark-cluster-ssh \ 
    --id <my-cluster-id> \
    --jupyter <local-port>
```

### Manage your Spark cluster

You can also see your clusters from the CLI:
```
./bin/spark-cluster-list
```

And get the state of any specified cluster:
```
./bin/spark-cluster-get --id <my-cluster-id>
```

Finally, you can delete any specified cluster:
```
./bin/spark-cluster-delete --id <my-cluster-id>
```
