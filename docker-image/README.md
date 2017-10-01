# Docker Image Gallery
Azure Distributed Data Engineering Toolkit uses Docker containers to run Spark. 

Please refer to the docs for details [how to select a docker-repo at cluster creation time](../docs/12-docker-image.md).

### Supported Base Images
We support several base images:
- [Docker Hub] jiata/aztk:<image-version>-spark2.2.0-python3.5.4
- [Docker Hub] jiata/aztk:<image-version>-spark2.1.0-python3.5.4
- [Docker Hub] jiata/aztk:<image-version>-spark1.6.3-python3.5.4
- [Docker Hub] jiata/aztk:<image-version>-spark2.1.0-python2.7.13
- [Docker Hub] jiata/aztk:<image-version>-spark1.6.3-python2.7.13

NOTE: Replace **<image-version>** with the version of the image you wish to use. For example: **jiata/aztk:0.1.0-spark2.2.0-python3.5.4**

### Gallery of 3rd Party Images
Since this toolkit uses Docker containers to run Spark, users can bring their own images. Here's a list of 3rd party images:
- *coming soon*

(See below for a how-to guide on building your own images for the Azure Distributed Data Engineering Toolkit)

# How to use my own Docker Image
This section is for users who want to build their own docker images.

## Base Docker Images to build with
By default, the Azure Distributed Data Engineering Toolkit uses **Spark2.2.0-Python3.5.4** as its base image. However, you can build from any of the following supported base images:

- Spark2.2.0 and Hadoop2.7 and Python3.5.4
- Spark2.1.0 and Hadoop2.7 and Python3.5.4
- Spark2.1.0 and Hadoop2.7 and Python2.7.13
- Spark1.6.3 and Hadoop2.6 and Python3.5.4
- Spark1.6.3 and Hadoop2.6 and Python2.7.13

All the base images above are built on a vanilla ubuntu16.04-LTS image and comes pre-baked with Jupyter Notebook and a connection to Azure Blob Storage (WASB).

Currently, the images are hosted on [Docker Hub (jiata/aztk)](https://hub.docker.com/r/jiata/aztk).

If you have requests to add to the list of supported base images, please file a new Github issue.

## Building Your Own Docker Image
Azure Distributed Data Engineering Toolkit supports custom Docker images. To guarantee that your Spark deployment works, you can either build your own Docker image on top or beneath one of our supported base images _OR_ you can modify this supported Dockerfile and build your own image.

### Building on top 
You can choose to build on top of one of our base images by using the **FROM** keyword in your Dockerfile:
```python
# Your custom Dockerfile

FROM jiata/aztk:<aztk-image-version>-spark2.2.0-python3.5.4
...

```

### Building beneath 
You can alternatively build beneath one of our base images by pulling down one of base images' Dockerfile and setting the **FROM** keyword to pull from your Docker image's location:
```python
# The Dockerfile from one of supported base image
# Change the FROM statement to point to your hosted image repo

FROM my_username/my_repo:latest
...
```

NOTE: Currently, we do not supported private Docker repos.

## About the Dockerfile
The Dockerfile is used to build the Docker images used by this toolkit. 

You can modify this Dockerfile to build your own image. If you plan to do so, please continue reading the below sections.

### Specifying Spark and Python Version
This Dockerfile takes in a few variables at build time that allow you to specify your desired Spark and Python versions: **PYTHON_VERSION** and **SPARK_VERSION_KEY**.

```sh
# For example, if I want to use Python 2.7.13 with Spark 1.6.3 I would build the image as follows:
docker build \
    --build-arg PYTHON_VERSION=2.7.13 \
    --build-arg SPARK_VERSION_KEY=spark-1.6.3-bin-hadoop2.6 \
    -t <my_image_tag> .
```

**SPARK_VERSION_KEY** is used to locate which version of Spark to download. These are the values that have been tested:
- spark-1.6.3-bin-hadoop2.6
- spark-2.1.0-bin-hadoop2.7
- spark-2.2.0-bin-hadoop2.7

For a full list of supported keys, please see this [page](https://d3kbcqa49mib13.cloudfront.net)

NOTE: Do not include the '.tgz' suffix as part of the Spark version key.

**PYTHON_VERSION** is used to set the version of Python for your cluster. These are the values that have been tested:
- 3.5.4
- 2.7.13

NOTE: Most version of Python will work. However, when selecting your Python version, please make sure that the it is compatible with your selected version of Spark. Today, it is also a requirement that your selected verion of Python can run Jupyter Notebook.

### Required Environment Variables
When layering your own Docker image, make sure your image does not intefere with the environment variables set in this Dockerfile, otherwise it may not work.

If you want to use your own version of Spark, please make sure that the following environment variables are set. 

``` sh
# An example of required environment variables
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV PYSPARK_PYTHON python
ENV USER_PYTHON_VERSION $PYTHON_VERSION
ENV PATH $SPARK_HOME/bin:$PATH
```

If you are using your own version of Spark, make that it is symlinked by "/home/spark-current". **$SPARK_HOME**, must also point to "/home/spark-current".


