# Docker
Azure Distributed Data Engineering Toolkit runs Spark on Docker.

Supported Azure Distributed Data Engineering Toolkit images are hosted publicly on [Docker Hub](https://hub.docker.com/r/jiata/aztk/tags).

## Versioning with Docker
The default base image that this package uses is a Docker image with **Spark v2.2.0** and **Python v2.7.13**.

However, the Azure Distributed Data Engineering Toolkit supports several base images that you can toggle between:
- Spark v2.2.0 and Python v3.5.4 (default)
- Spark v2.1.0 and Python v3.5.4
- Spark v2.1.0 and Python v2.7.13
- Spark v1.6.3 and Python v3.5.4
- Spark v1.6.3 and Python v2.7.13

*Today, these supported base images are hosted on Docker Hub under the repo ["jiata/aztk:<tag>"](https://hub.docker.com/r/jiata/aztk/tags).*

To select an image other than the default, you can set your Docker image at cluster creation time with the optional **--docker-repo** parameter:

```sh
aztk spark cluster create ... --docker-repo <name_of_docker_image_repo>
```

For example, if I am using the image version 0.1.0, and wanted to use Spark v1.6.3 with Python v2.7.13, I could run the following cluster create command:
```sh
aztk spark cluster create ... --docker-repo jiata/aztk:0.1.0-spark1.6.3-python3.5.4
```

## Using a custom Docker Image
What if I wanted to use my own Docker image? _What if I want to use Spark v2.0.1 with Python v3.6.2?_

You can build your own Docker image on top or beneath one of our supported base images _OR_ you can modify the [supported Dockerfile](../docker-image) and build your own image that way.

Please refer to ['../docker-image'](../docker-image) for more information on building your own image.

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
