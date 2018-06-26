# Getting Started Script

The provided account setup script creates and configures all of the required Azure resources.

The script will create and configure the following resources:
- Resource group
- Storage account
- Batch account
- Azure Active Directory application and service principal
<!-- - Virtual network with a configured subnet -->

The script outputs all of the necessary information to use `aztk`, just copy the output into the `.aztk/secrets.yaml` file created when running `aztk spark init`.

## Usage
Copy and paste the following into an [Azure Cloud Shell](https://shell.azure.com):
```sh
wget -q https://raw.githubusercontent.com/Azure/aztk/v0.7.2/account_setup.sh &&
chmod 755 account_setup.sh &&
/bin/bash account_setup.sh
```
A series of prompts will appear, and you can set the values you desire for each field. Default values appear in brackets `[]` and will be used if no value is provided.
```
Azure Region [westus]:
Resource Group Name [aztk]:
Storage Account Name [aztkstorage]:
Batch Account Name [aztkbatch]:
Active Directory Application Name [aztkapplication]:
Active Directory Application Credential Name [aztk]:
```

Once the script has finished running you will see the following output:

```
service_principal:
    tenant_id: <AAD Diretory ID>
    client_id: <AAD App Application ID>
    credential: <AAD App Password>
    batch_account_resource_id: </batch/account/resource/id>
    storage_account_resource_id: </storage/account/resource/id>
```

Copy the entire `service_principal` section in your `.aztk/secrets.yaml`. If you do not have a `secrets.yaml` file, you can create one in your current working directory by running `aztk spark init`.

Now you are ready to create your first `aztk` cluster. See [Creating a Cluster](./10-clusters.html#creating-a-cluster).
