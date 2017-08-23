# Cloud storage
Cloud stoarge for spark enables you to have a persisted storage system backed by a cloud provider. Spark supports this by placing the appropriate storage jars and updating the core-site.xml file accordingly.

## Azure Storage Blobs (WASB)
The default cloud storage system for Spark on Batch is Azure Storage Blobs (a.k.a. WASB). The WASB jars are automatically placed in the spark cluster and the permissions are pulled from you secrests file.

Reading and writing to and from Azure blobs is easily achieved by using the wasb syntax. For example, reading a csv file using pyspark would be:

```python
# read csv data into data
dataframe = spark.read.csv('wasbs://MY_CONTAINER@MY_STORAGE_ACCOUNt.blob.core.windows.net/MY_INPUT_DATA.csv')

# print off the first 5 rows
dataframe.show(5)

# write the csv back to storage
dataframe.write.csv('wasbs://MY_CONTAINER@MY_STORAGE_ACCOUNt.blob.core.windows.net/MY_DATA.csv')
```
