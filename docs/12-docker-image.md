# Docker
Azure Thunderbolt runs Spark on Docker. 

Azure Thunderbolt images are hosted publicly on [Docker Hub](https://hub.docker.com/r/jiata/thunderbolt/tags).

## Versioning with Docker 
The default base image that Azure Thunderbolt uses is a Docker image with **Spark v2.2.0** and **Python v2.7.13**. 

However, Azure Thunderbolt supports several base images that you can toggle between:
- Spark v2.2.0 and Python v3.5.4 (default)
- Spark v2.1.0 and Python v3.5.4
- Spark v2.1.0 and Python v2.7.13
- Spark v1.6.3 and Python v3.5.4
- Spark v1.6.3 and Python v2.7.13

*Today, these supported base images are hosted on Docker Hub under the repo ["jiata/thunderbolt:<tag>"](https://hub.docker.com/r/jiata/thunderbolt/tags).*

To select an image other than the default, you can set your Docker image at cluster creation time with the optional **--docker-repo** parameter:

```sh
azb spark cluster create ... --docker-repo <name_of_docker_image_repo>
```

For example, if I am using the Thunderbolt image version 0.1.0, and wanted to use Spark v1.6.3 with Python v2.7.13, I could run the following cluster create command:
```sh
azb spark cluster create ... --docker-repo jiata/thunderbolt:0.1.0-spark1.6.3-python3.5.4
```

## Using a custom Docker Image
What if I wanted to use my own Docker image? _What if I want to use Spark v2.0.1 with Python v3.6.2?_

You can build your own Docker image on top or beneath one of our supported base images _OR_ you can modify the [Azure Thunderbolt supported Dockerfile](../docker-image) and build your own image that way. 

Please refer to ['../docker-image'](../docker-image) for more information on building your own image.

Once you have your Docker image built and hosted publicly, you can then use the **--docker-repo** parameter in your **azb spark cluster create** command to point to it.

## Using a custom Docker Image that is Privately Hosted

_Coming soon_
