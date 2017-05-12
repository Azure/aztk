# Redbull
Run Spark Standalone on Azure Batch

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

First, create your cluster:
```
./bin/spark-cluster-create \
    --cluster-id <my-cluster-id> \
    --cluster-size <number of nodes> \
    --cluster-vm-size <vm-size> \
    --wait/--no-wait (optional)
```

When your cluster is ready, create a user for your cluster:
```
./bin/spark-cluster-create-user \
    --cluster-id <my-cluster-id> \
    --username <username> \
    --password <password>
```

Now you can submit jobs to run against the cluster:
```
./bin/spark-app-submit \
    --cluster-id <my-cluster-id> \
    --app-id <my-application> \
    --file <my-spark-job>
```

To view the spark UI, open up an ssh tunnel with the "webui" option and a local port to map to:
```
./bin/spark-cluster-ssh \ 
    --cluster-id <my-cluster-id> \
    --webui <local-port>
```

Optionally, you can also open up a jupyter notebook with the "jupyter" option to work in:
```
./bin/spark-cluster-ssh \ 
    --cluster-id <my-cluster-id> \
    --webui <local-port> \
    --jupyter <local-port>
```

You can also see your clusters from the CLI:
```
./bin/spark-cluster-list
```

Finally, you can get the state of any specified cluster:
```
./bin/spark-cluster-get \
    --cluster-id <my-cluster-id>
```
