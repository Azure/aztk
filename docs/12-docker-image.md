# Docker
Azure Distributed Data Engineering Toolkit runs Spark on Docker.

Supported Azure Distributed Data Engineering Toolkit images are hosted publicly on [Docker Hub](https://hub.docker.com/r/aztk/spark/).

By default, the `aztk/spark:v0.1.0-spark2.3.0-base` image will be used.

To select an image other than the default, you can set your Docker image at cluster creation time with the optional **--docker-repo** parameter:

```sh
aztk spark cluster create ... --docker-repo <name_of_docker_image_repo>
```

To customize Docker configuration, you can pass command line options to the `docker run` command with the optional **--docker-run-options** parameter:

```sh
aztk spark cluster create ... "--docker-run-options=<command_line_options_for_docker_run>"
```

For example, if I wanted to use Spark v2.2.0 and start my container in privileged mode and with a kernel memory limit of 100MB,
I could run the following cluster create command:
```sh
aztk spark cluster create ... --docker-repo aztk/base:spark2.2.0 "--docker-run-options=--privileged --kernel-memory 100m"
```

## Using a custom Docker Image
You can build your own Docker image on top or beneath one of our supported base images _OR_ you can modify the [supported Dockerfiles](https://github.com/Azure/aztk/tree/v0.10.2/docker-image) and build your own image that way.

Once you have your Docker image built and hosted publicly, you can then use the **--docker-repo** parameter in your **aztk spark cluster create** command to point to it.

## Using a custom Docker Image that is Privately Hosted

To use a private docker image you will need to provide a docker username and password that have access to the repository you want to use.

In `.aztk/secrets.yaml` setup your docker config
```yaml
docker:
    username: <myusername>
    password: <mypassword>
```

If your private repository is not on docker hub (Azure container registry for example) you can provide the endpoint here too
```yaml
docker:
    username: <myusername>
    password: <mypassword>
    endpoint: <https://my-custom-docker-endpoint.com>
```

### Building Your Own Docker Image
Building your own Docker Image provides more customization over your cluster's environment. For some, this may look like installing specific, and even private, libraries that their Spark jobs require. For others, it may just be setting up a version of Spark, Python or R that fits their particular needs.

The Azure Distributed Data Engineering Toolkit supports custom Docker images. To guarantee that your Spark deployment works, we recommend that you build on top of one of our supported images.

To build your own image, can either build _on top_ or _beneath_ one of our supported images _OR_ you can just modify one of the supported Dockerfiles to build your own.

### Building on top 
You can build on top of our images by referencing the __aztk/spark__ image in the **FROM** keyword of your Dockerfile:
```sh
# Your custom Dockerfile

FROM aztk/spark:v0.1.0-spark2.3.0-base
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

## Custom Docker Image Requirements
If you are building your own custom image and __not__ building on top of a supported image, the following requirements are necessary.

Please make sure that the following environment variables are set: 
- AZTK_DOCKER_IMAGE_VERSION
- JAVA_HOME
- SPARK_HOME

You also need to make sure that __PATH__ is correctly configured with $SPARK_HOME
- PATH=$SPARK_HOME/bin:$PATH

By default, these are set as follows:
``` sh
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV PATH $SPARK_HOME/bin:$PATH
```

If you are using your own version of Spark, make that it is symlinked by "/home/spark-current". **$SPARK_HOME**, must also point to "/home/spark-current".

## Hosting your Docker Image
By default, aztk assumes that your Docker images are publicly hosted on Docker Hub. However, we also support hosting your images privately.

See [here](12-docker-image.html#using-a-custom-docker-image-that-is-privately-hosted) to learn more about using privately hosted Docker Images.
