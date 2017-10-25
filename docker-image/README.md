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
The Dockerfiles in this directory are used to build the Docker images used by this toolkit. Please reference the individual Dockerfiles for more information on them:
- [Vanilla](./vanilla)
- [Python](./python)
- TODO: R


