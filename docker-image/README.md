# Docker Image Gallery
Azure Distributed Data Engineering Toolkit uses Docker containers to run Spark. 

Please refer to the docs for details on [how to select a docker-repo at cluster creation time](../docs/12-docker-image.md).

## Supported Images
By default, this toolkit will use the base Spark image, __aztk/base__. This image contains the bare mininum to get Spark up and running in standalone mode.

On top of that, we also provide additional flavors of Spark images, one geared towards the Python user (PySpark), and the other, geared towards the R user (SparklyR or SparkR).

Docker Image | Image Type | User Language(s) | What's Included? 
:-- | :-- | :-- | :-- 
[aztk/base](https://hub.docker.com/r/aztk/base/) | Base | Java, Scala |  `Spark`
[aztk/python](https://hub.docker.com/r/aztk/python/) | Pyspark | Python | `Anaconda`</br>`Jupyter Notebooks` </br> `PySpark`
[aztk/r-base](https://hub.docker.com/r/aztk/r-base/) | SparklyR | R | `CRAN`</br>`RStudio Server`</br>`SparklyR and SparkR`

__aztk/gpu__, __aztk/python__ and __aztk/r-base__ images are built on top of the __aztk/base__ image.

All the AZTK images are hosted on Docker Hub under [aztk](https://hub.docker.com/r/aztk).

### Matrix of Supported Container Images:

Docker Repo (hosted on Docker Hub) | Spark Version | Python Version | R Version | CUDA Version | cudNN Version
:-- | :-- | :-- | :-- | :-- | :-- 
aztk/base:spark2.2.0 __(default)__ | v2.2.0 | -- | -- | -- | -- 
aztk/base:spark2.1.0 | v2.1.0 | -- | -- | -- | -- 
aztk/base:spark1.6.3 | v1.6.3 | -- | -- | -- | -- 
aztk/gpu:spark2.2.0 | v2.2.0 | -- | -- | 8.0 | 6.0
aztk/gpu:spark2.1.0 | v2.1.0 | -- | -- | 8.0 | 6.0
aztk/gpu:spark1.6.3 | v1.6.3 | -- | -- | 8.0 | 6.0
aztk/python:spark2.2.0-python3.6.2-base | v2.2.0 | v3.6.2 | -- | -- | -- | -- 
aztk/python:spark2.1.0-python3.6.2-base | v2.1.0 | v3.6.2 | -- | -- | -- | -- 
aztk/python:spark1.6.3-python3.6.2-base | v1.6.3 | v3.6.2 | -- | -- | -- | -- 
aztk/python:spark2.2.0-python3.6.2-gpu | v2.2.0 | v3.6.2 | -- | 8.0 | 6.0 
aztk/python:spark2.1.0-python3.6.2-gpu | v2.1.0 | v3.6.2 | -- | 8.0 | 6.0 
aztk/python:spark1.6.3-python3.6.2-gpu | v1.6.3 | v3.6.2 | -- | 8.0 | 6.0 
aztk/r-base:spark2.2.0-r3.4.1-base | v2.2.0 | -- | v3.4.1 | -- | --
aztk/r-base:spark2.1.0-r3.4.1-base | v2.1.0 | -- | v3.4.1 | -- | --
aztk/r-base:spark1.6.3-r3.4.1-base | v1.6.3 | -- | v3.4.1 | -- | --

If you have requests to add to the list of supported images, please file a Github issue.

NOTE: Spark clusters that use the __aztk/gpu__, __aztk/python__ or __aztk/r-base__ images take longer to provision because these Docker images are significantly larger than the __aztk/base__ image. 

### Gallery of 3rd Party Images
Since this toolkit uses Docker containers to run Spark, users can bring their own images. Here's a list of 3rd party images:
- *coming soon*

(See below for a how-to guide on building your own images for the Azure Distributed Data Engineering Toolkit)

# How do I use my own Docker Image?
Building your own Docker Image to use with this toolkit has many advantages for users who want more customization over their environment. For some, this may look like installing specific, and even private, libraries that their Spark jobs require. For others, it may just be setting up a version of Spark, Python or R that fits their particular needs.

This section is for users who want to build their own docker images.

## Building Your Own Docker Image
The Azure Distributed Data Engineering Toolkit supports custom Docker images. To guarantee that your Spark deployment works, we recommend that you build on top of one of our __aztk/base__ images. You can also build on top of our __aztk/python__ or __aztk/r-base__ images, but note that they are also built on top of the __aztk_base__ image.

To build your own image, can either build _on top_ or _beneath_ one of our supported images _OR_ you can just modify one of the supported Dockerfiles to build your own.

### Building on top 
You can build on top of our images by referencing the __aztk/base__ image in the **FROM** keyword of your Dockerfile:
```sh
# Your custom Dockerfile

FROM aztk/base:spark2.2.0
...

```

### Building beneath 
To build beneath one of our images, modify one of our Dockerfiles so that the **FROM** keyword pulls from your Docker image's location (as opposed to the default which is a base Ubuntu image):
```sh
# One of the Dockerfiles that AZTK supports
# Change the FROM statement to point to your hosted image repo

FROM my_username/my_repo:latest
...
```

Please note that for this method to work, your Docker image must have been built on Ubuntu.

## Required Environment Variables
When layering your own Docker image, make sure your image does not intefere with the environment variables set in the __aztk_base__ Dockerfile, otherwise it may not work on AZTK.

Please make sure that the following environment variables are set: 
- AZTK_PYTHON_VERSION
- JAVA_HOME
- SPARK_HOME

You also need to make sure that __PATH__ is correctly configured with $SPARK_HOME
- PATH=$SPARK_HOME/bin:$PATH

By default, these are set as follows:
``` sh
ENV AZTK_PYTHON_VERSION 3.5.4
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV PATH $SPARK_HOME/bin:$PATH
```

If you are using your own version of Spark, make that it is symlinked by "/home/spark-current". **$SPARK_HOME**, must also point to "/home/spark-current".

## Hosting your Docker Image
By default, this toolkit assumes that your Docker images are publicly hosted on Docker Hub. However, we also support hosting your images privately.

See [here](https://github.com/Azure/aztk/blob/master/docs/12-docker-image.md#using-a-custom-docker-image-that-is-privately-hosted) to learn more about using privately hosted Docker Images.

## Learn More 
The Dockerfiles in this directory are used to build the Docker images used by this toolkit. Please reference the individual directories for more information on each Dockerfile:
- [Base](./base)
- [Python](./python)
- [R](./r)


