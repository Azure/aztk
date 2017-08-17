# Spark 2.2.0 with a built in WASB connector
This docker image downloads and configures the azure-storage and hadoop-azure jars so that spark can interact directly with Azure Storage.

## Build Instructions
docker build -t <image-tag> \
    --build-arg STORAGE_ACCOUNT_NAME=<your-storage-account-name> \
    --build-arg STORAGE_ACCOUNT_KEY=<your-storage-account-key> \
    .

