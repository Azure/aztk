# Cloud storage
Cloud storage for spark enables you to have a persisted storage system backed by a cloud provider. Spark supports this by placing the appropriate storage jars and updating the core-site.xml file accordingly.

## Azure Storage Blobs (WASB)

Pre-built into this package is native support for connecting your Spark cluster to Azure Blob Storage (aka WASB). The required WASB jars are automatically placed in the Spark cluster and the permissions are pulled from your core-site.xml file under *.aztk/core-site.xml*.

To connect to your Azure Storage account, make sure that the storage fields in your *.aztk/core-site.xml* file are properly filled out. This tool already has the the basic template for using WASB filled out in the *.aztk/core-site.xml* file. Simply uncomment the in the "Azure Storage Blobs (WASB)" section and fill out the properties for MY\_STORAGE\_ACCOUNT\_NAME, MY\_STORAGE\_ACCOUNT\_SUFFIX and MY\_STORAGE\_ACCOUNT\_KEY.

Once you have correctly filled out the *.aztk/core-site.xml* with your storage credentials, you will be able to access your storage accounts from your Spark job.

Reading and writing to and from Azure blobs is easily achieved by using the `wasb` syntax. For example, reading a csv file using Pyspark would be:

```python
# read csv data into data
dataframe = spark.read.csv('wasbs://MY_CONTAINER@MY_STORAGE_ACCOUNt.blob.core.windows.net/MY_INPUT_DATA.csv')

# print off the first 5 rows
dataframe.show(5)

# write the csv back to storage
dataframe.write.csv('wasbs://MY_CONTAINER@MY_STORAGE_ACCOUNt.blob.core.windows.net/MY_OUTPUT_DATA.csv')
```

## Azure Data Lake (ADL)

Pre-built into this package is native support for connecting your Spark cluster to Azure Data Lake (aka ADL). The required ADL jars are automatically placed in the Spark cluster and the permissions are pulled from your core-site.xml file under *.aztk/core-site.xml*.

To connect to your Azure Storage account, make sure that the storage fields in your *.aztk/core-site.xml* file are properly filled out. This tool already has the the basic template for using ADL filled out in the *.aztk/core-site.xml* file. Simply uncomment the in the "ADL (Azure Data Lake) Configuration" section and fill out the properties for MY\_AAD\_TENANT\_ID, MY\_AAD\_CLIENT\_ID and MY\_AAD\_CREDENTIAL.

Once you have correctly filled out the *.aztk/core-site.xml* with your Azure Data Lake credentials, you will be able to access your ADL storage repositories from your Spark job.

Reading and writing to and from Azure Data Lake Storage is easily achieved by using the `adl` syntax. For example, reading a csv file using Pyspark would be:

```python
# read csv data into data
dataframe = spark.read.csv('adl://MY_ADL_STORAGE_ACCOUNT.azuredatalakestore.net/MY_INPUT_DATA.csv')

# print off the first 5 rows
dataframe.show(5)

# write the csv back to storage
dataframe.write.csv('adl://MY_ADL_STORAGE_ACCOUNT.azuredatalakestore.net/MY_OUTPUT_DATA.csv')
```

Note: _The implementation of the ADL connector is designed to always access ADLS through a secure channel, so there is no adls file system scheme name. You will always use adl. For more information please take a look at https://docs.microsoft.com/en-us/azure/hdinsight/hdinsight-hadoop-use-data-lake-store._

Note: In order to use ADL you must first create an AAD application and give it permissions to your ADL Storage account. There is a good tutorial on how to create the require AAD security objects to use ADL [here](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal). Not shown in this tutorial is that as a last step, you will need to give permissions the application you created permissions to your ADL Storage account.

## Additional file system connectors

You can quickly add support for additional data repositories by adding the necessary JARS to your cluster, configuring the spark-defaults.conf and core-site.xml file  accordingly.

### Adding Jars

To add jar files to the cluster, simply add them to your local *.aztk/jars* directory. These will automatically get loaded into your cluster and placed under $SPARK_HOME/jars

### Registering Jars

To register the jars, update the *.aztk/spark-defaults.conf* file and add the path to the jar file(s) to the spark.jars property
```sh
spark.jars $spark_home/jars/my_jar_file_1.jar,$spark_home/jars/my_jar_file_2.jar
```

### Configuring the file system

Configuring the file system requires an update to the *aztk/core-site.xml* file. Each file system is unique and requires different setup in the core-site.xml. In .aztk/core-site.xml, we have preloaded templates to add WASB and ADL.
