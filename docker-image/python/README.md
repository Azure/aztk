# Python
This Dockerfile is used to build the Python flavored Spark Docker image used by this toolkit. This image uses Anaconda, providing access to a wide range of popular python packages.

You can modify this Dockerfile to build your own image. However, in mose cases, building on top of the Vanilla image is recommended.

NOTE: If you plan to use Jupyter Notebooks with your Spark cluster, we recommend using this image as Jupyter Notebook comes pre-installed with Anaconda. 

## How to build this image
This Dockerfile takes in two variables at build time that allow you to specify your desired Spark and Anaconda versions: **ANACONDA_VERSION** and **SPARK_VERSION_KEY**.

By default, we set **ANACONDA_VERSION=anaconda3-5.0.0** and **SPARK_VERSION_KEY=spark-2.2.0-bin-hadoop2.7**.

```sh
# For example, if I want to use Anaconda3 v5.0.0 with Spark v2.1.0 I would build the image as follows:
docker build \
    --build-arg ANACONDA_VERSION=anaconda3-5.0.0 \
    --build-arg SPARK_VERSION_KEY=spark-2.1.0-bin-hadoop2.7 \
    -t <my_image_tag> .
```

**SPARK_VERSION_KEY** is used to locate which version of Spark to download. These are the values that have been tested:
- spark-1.6.3-bin-hadoop2.6
- spark-2.1.0-bin-hadoop2.7
- spark-2.2.0-bin-hadoop2.7

For a full list of supported keys, please see this [page](https://d3kbcqa49mib13.cloudfront.net)

NOTE: Do not include the '.tgz' suffix as part of the Spark version key.

**ANACONDA_VERSION** is used to set the version of Anaconda for your cluster. When selecting your desired version of Anaconda, please verify that the version of Python is greater than v3.4 as this is a requirement for AZTK.

NOTE: Most version of Python will work. However, when selecting your Python version, please make sure that the it is compatible with your selected version of Spark. 


## Required Environment Variables
When layering your own Docker image, make sure your image does not intefere with the environment variables set in this Dockerfile, otherwise it may not work.

If you want to modify this Dockerfile, please make sure that the following environment variables are set: 

``` sh
# Required environment variables
ENV JAVA_HOME 
ENV SPARK_HOME 
ENV PYSPARK_PYTHON 
ENV USER_PYTHON_VERSION
```

If you are using your own version of Spark, make that it is symlinked by "/home/spark-current". **$SPARK_HOME**, must also point to "/home/spark-current".
