# Docker Image Gallery
Azure Distributed Data Engineering Toolkit uses Docker containers to run Spark. 

Please refer to the docs for details on [how to select a docker-repo at cluster creation time](../docs/12-docker-image.md).

### Supported Images
We support 3 primary docker image types, each geared towards specific user types:

Docker Image | Image Type | User Language(s) | What's Included? 
:-- | :-- | :-- | :-- 
[jiata/aztk-vanilla](https://hub.docker.com/r/jiata/aztk-vanilla/) | Vanilla | Java, Scala |  `Spark`
[jiata/aztk-python](https://hub.docker.com/r/jiata/aztk-python/) | Pyspark | Python | `Anaconda`</br>`Jupyter Notebooks` 
[jiata/aztk-r](https://hub.docker.com/r/jiata/aztk-r/) | SparklyR | R | `MRO or CRAN`</br>`RStudio Server`</br>`R Client` 

#### Matrix of supported container images:

Docker Repo (hosted on Docker Hub) | Spark Version | Python Version | R Version
:-- | :-- | :-- | :--
jiata/aztk-vanilla:0.1.0-spark2.2.0 | v2.2.0 | -- | --
jiata/aztk-vanilla:0.1.0-spark2.1.0 | v2.1.0 | -- | --
jiata/aztk-vanilla:0.1.0-spark1.6.3 | v1.6.3 | -- | --
jiata/aztk-python:0.1.0-spark2.2.0-anaconda3-5.0.0 | v2.2.0 | v3.6.2 | --
jiata/aztk-python:0.1.0-spark2.1.0-anaconda3-5.0.0 | v2.1.0 | v3.6.2 | --
jiata/aztk-python:0.1.0-spark1.6.3-anaconda3-5.0.0 | v1.6.3 | v3.6.2 | --
jiata/aztk-r:0.1.0-spark2.2.0-r3.4.1 | v2.2.0 | -- | v3.4.1
jiata/aztk-r:0.1.0-spark2.1.0-r3.4.1 | v2.1.0 | -- | v3.4.1
jiata/aztk-r:0.1.0-spark1.6.3-r3.4.1 | v1.6.3 | -- | v3.4.1

If you have requests to add to the list of supported base images, please file a new Github issue.

NOTE: Spark clusters that use the PySpark and SparklyR images take longer to provision because these Docker images are significantly larger than the Vanilla Spark image. 

### Gallery of 3rd Party Images
Since this toolkit uses Docker containers to run Spark, users can bring their own images. Here's a list of 3rd party images:
- *coming soon*

(See below for a how-to guide on building your own images for the Azure Distributed Data Engineering Toolkit)

# How do I use my own Docker Image?
This section is for users who want to build their own docker images.

By default, the Azure Distributed Data Engineering Toolkit uses our vanilla image with **Spark2.2.0**. However, you can build from any of our supported images above (see the matrix of supported container images).

All of our base images (Vanilla, PySpark and SparklyR) are built on a vanilla ubuntu16.04-LTS image.

## Building Your Own Docker Image
Azure Distributed Data Engineering Toolkit supports custom Docker images. To guarantee that your Spark deployment works, you can either build your own Docker image on top or beneath one of our supported base images _OR_ you can modify one of the supported Dockerfiles and build your own image.

### Building on top 
You can choose to build on top of one of our base images by using the **FROM** keyword in your Dockerfile:
```python
# Your custom Dockerfile

FROM jiata/aztk-vanilla:<aztk-vanilla-image-version>-spark2.2.0
...

```

### Building beneath 
You can alternatively build beneath one of our base images by using one of the Dockerfiles and setting the **FROM** keyword to pull from your Docker image's location:
```python
# One of the Dockerfiles that AZTK supports
# Change the FROM statement to point to your hosted image repo

FROM my_username/my_repo:latest
...
```

NOTE: See [here](https://github.com/Azure/aztk/blob/master/docs/12-docker-image.md#using-a-custom-docker-image-that-is-privately-hosted) to learn more about using privately hosted Docker Images.

## About the Dockerfiles
The Dockerfiles in this directory are used to build the Docker images used by this toolkit. 

You can modify these Dockerfiles to build your own image. If you plan to do so, please continue reading the below sections.

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

NOTE: Most version of Python will work. However, when selecting your Python version, please make sure that the it is compatible with your selected version of Spark.

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


