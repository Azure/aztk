# redbull
Run Spark on Azure Batch

## Develop

1. Create a virtual environment (either virtualenv or with conda)
2. Use setuptools:
    ```
    python3 setup.py develop
    ```
3. Create a file called configuration.cfg in the root directory with the following body and fill out the fields
    ```
    [Batch]
    batchaccountname=
    batchaccountkey=
    batchserviceurl=

    [Storage]
    storageaccountname=
    storageaccountkey=
    storageaccountsuffix=core.windows.net
    ```