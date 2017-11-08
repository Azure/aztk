# Docker
Azure Distributed Data Engineering Toolkit runs Spark on Docker.

Supported Azure Distributed Data Engineering Toolkit images are hosted publicly on [Docker Hub](https://hub.docker.com/r/jiata/aztk-base/tags).

## Versioning with Docker
The default image that this package uses is a the __aztk-base__ Docker image that comes with **Spark v2.2.0**.

You can use several versions of the __aztk-base__ image:
- Spark 2.2.0 - jiata/aztk-base:0.1.0-spark2.2.0 (default)
- Spark 2.1.0 - jiata/aztk-base:0.1.0-spark2.1.0
- Spark 1.6.3 - jiata/aztk-base:0.1.0-spark1.6.3

We also provide two other image types tailored for the Python and R users: __aztk-r__ and __aztk-python__. You can choose between the following:
- Anaconda3-5.0.0 (Python 3.6.2) / Spark 2.2.0 - jiata/aztk-python:0.1.0-spark2.2.0-python3.6.2
- Anaconda3-5.0.0 (Python 3.6.2) / Spark 2.1.0 - jiata/aztk-python:0.1.0-spark2.1.0-python3.6.2
- Anaconda3-5.0.0 (Python 3.6.2) / Spark 1.6.3 - jiata/aztk-python:0.1.0-spark1.6.3-python3.6.2
- [coming soon] R 3.4.0 / Spark v2.2.0 - jiata/aztk-r:0.1.0-spark2.2.0-r3.4.1
- [coming soon] R 3.4.0 / Spark v2.1.0 - jiata/aztk-r:0.1.0-spark2.1.0-r3.4.1
- [coming soon] R 3.4.0 / Spark v1.6.3 - jiata/aztk-r:0.1.0-spark1.6.3-r3.4.1

*Today, these supported images are hosted on Docker Hub under the repo ["jiata/aztk-base/r/python:<tag>"](https://hub.docker.com/r/jiata).*

To select an image other than the default, you can set your Docker image at cluster creation time with the optional **--docker-repo** parameter:

```sh
aztk spark cluster create ... --docker-repo <name_of_docker_image_repo>
```

For example, if I am using the image version 0.1.0, and wanted to use Spark v1.6.3, I could run the following cluster create command:
```sh
aztk spark cluster create ... --docker-repo jiata/aztk-base:0.1.0-spark1.6.3
```

## Using a custom Docker Image
What if I wanted to use my own Docker image?

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
