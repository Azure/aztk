# Vanilla

This Dockerfile is used to build the Vanilla Spark Docker image used by this toolkit. This is the Docker image type that is selected by AZTK by default.

You can modify this Dockerfile to build your own image. 

## How to build this image
This Dockerfile takes in a single variable at build time that allows you to specify your desired Spark version: **SPARK_VERSION_KEY**.

By default, this image will also be installed with python v3.5.4 as it is a requirement for this toolkit.

```sh
# For example, if I want to use Spark 1.6.3 I would build the image as follows:
docker build \
    --build-arg SPARK_VERSION_KEY=spark-1.6.3-bin-hadoop2.6 \
    -t <my_image_tag> .
```

**SPARK_VERSION_KEY** is used to locate which version of Spark to download. These are the values that have been tested:
- spark-1.6.3-bin-hadoop2.6
- spark-2.1.0-bin-hadoop2.7
- spark-2.2.0-bin-hadoop2.7

For a full list of supported keys, please see this [page](https://d3kbcqa49mib13.cloudfront.net)

NOTE: Do not include the '.tgz' suffix as part of the Spark version key.


## Required Environment Variables
When layering your own Docker image, make sure your image does not intefere with the environment variables set in this Dockerfile, otherwise it may not work.

If you want to modify this Dockerfile, please make sure that the following environment variables are set: 

``` sh
# Required environment variables
ENV JAVA_HOME 
ENV SPARK_HOME 
ENV PYSPARK_PYTHON 
```

If you are using your own version of Spark, make that it is symlinked by "/home/spark-current". **$SPARK_HOME**, must also point to "/home/spark-current".
