# Azure Batch with Spark Documentation
Spark on Azure Batch in a project that enables submission of single or batch spark jobs to the cloud. Azure Batch
will elastically scale and manage the compute resources required to run the jobs, and spin them down when no longer
needed.

## Getting Started
The minimum requirements to get started with Spark on Azure Batch are:
- An Azure account
- An Azure Batch account
- An Azure Storage account

### Setting up your accounts
1. Log into Azure
If you do not already have an Azure account, go to [https://azure.microsoft.com/](https://azure.microsoft.com/) to get
started for free today.

Once you have one, simply log in and go to the [Azure Portal](https://portal.azure.com) to start creating the resources you'll need to get going.


2. Create a Storage account

- Click the '+' button at the top left of the screen and search for 'Storage'. Select 'Storage account - blob, file, table, queue' and click 'Create'

![](./misc/Storage_1.png)

- Fill in the form and create the Storage account.

![](./misc/Storage_2.png)

3. Create a Batch account

- Click the '+' button at the top left of the screen and search for 'Compute'. Select 'Batch' and click 'Create'

![](./misc/Batch_1.png)

- Fill in the form and create the Batch account.

![](./misc/Batch_2.png)

4. Save your account credentials into the secrets.cfg file

- Copy the secrets.cfg.template file to secrests.cfg

Windows
```sh
copy secrets.cfg.template secrets.cfg
```

Linux and Mac OS
```sh
cp secrets.cfg.template secrets.cfg
```

- Go to the accounts in the Azure portal and copy pase the account names, keys and other information needed into the
secrets file.

#### Storage account

For the Storage account, copy the name and one of the two keys:

![](./misc/Storage_secrets.png)

#### Batch account

For the Batch account, copy the name, the url and one of the two keys:

![](./misc/Batch_secrets.png)


## Next Steps
- [Create a cluster](./10-clusters.md)
- [Run a Spark job](./20-spark-submit.md)
