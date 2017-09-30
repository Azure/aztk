# Cloud storage
Cloud stoarge for spark enables you to have a persisted storage system backed by a cloud provider. Spark supports this by placing the appropriate storage jars and updating the core-site.xml file accordingly.

## Azure Storage Blobs (WASB)

Pre-built into this package is native support for connecting your Spark cluster to Azure Blob Storage (aka WASB). The required WASB jars are automatically placed in the spark cluster and the permissions are pulled from you secrests file.

To connect to your Azure Storage account, make sure that the storage fields in your *.aztk/secrets.yaml* file are properly filled out.

[Even if you are just testing and have no need to connect with Azure Blob Storage, you still need to correctly fill out the storage fields in your *.aztk/secrets.yaml* file as it is a requirement for this package.]

Once you have correctly filled out the *.aztk/secrets.yaml* with your storage credentials, you will be able to access said storage account from your Spark job.

Please note: If you want to access another Azure Blob Storage account, you will need to recreate your cluster with an updated *.aztk/secrets.yaml* file with the appropriate storage credentials.

Reading and writing to and from Azure blobs is easily achieved by using the `wasb` syntax. For example, reading a csv file using Pyspark would be:

```python
# read csv data into data
dataframe = spark.read.csv('wasbs://MY_CONTAINER@MY_STORAGE_ACCOUNt.blob.core.windows.net/MY_INPUT_DATA.csv')

# print off the first 5 rows
dataframe.show(5)

# write the csv back to storage
dataframe.write.csv('wasbs://MY_CONTAINER@MY_STORAGE_ACCOUNt.blob.core.windows.net/MY_DATA.csv')
```
