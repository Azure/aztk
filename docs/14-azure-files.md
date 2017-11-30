# Azure Files

The ability to load a file share on the cluster is really useful when you want to be able to share data across all the nodes, and/or want that data to be persisted longer than the lifetime of the cluster. [Azure Files](https://docs.microsoft.com/azure/storage/files/storage-files-introduction) provides a very easy way to mount a share into the cluster and have it accessible to all nodes. This is useful in cases where you have small data sets you want to process (less than 1GB) or have notebooks that you want to re-use between clusters.

Mounting an Azure Files share in the cluster only required updating the cluster.yaml file at `.aztk/cluster.yaml`. For example, the following configuration will load two files shares into the cluster, one with my notebooks and one will a small data set that I have previously uploaded to Azure Files.

```yaml
azure_files:
    - storage_account_name: STORAGE_ACCOUNT_NAME
      storage_account_key: STORAGE_ACCOUNT_KEY
      # Name of the file share in Azure Files
      file_share_path: data
      # Mount point on the node in the cluster
      mount_path: /mnt/data
    - storage_account_name: STORAGE_ACCOUNT_NAME
      storage_account_key: STORAGE_ACCOUNT_KEY
      # Name of the file share in Azure Files
      file_share_path: notebooks
      # Mount point on the node in the cluster
      mount_path: /mnt/notebooks
```

From the cluster I can now access both of these file shares directly simply by navigating to /mnt/data or /mnt/notebooks respectively.
