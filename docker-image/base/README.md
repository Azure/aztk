# Base AZTK Docker image

This Dockerfile is used to build the __aztk-base__ image used by this toolkit. This Dockerfile produces the Docker image that is selected by AZTK by default.

You can modify this Dockerfile to build your own image. 

## How to build this image
This Dockerfile takes in a single variable at build time that allows you to specify your desired Spark version: **SPARK_VERSION_KEY**.

By default, this image will also be installed with python v3.5.4 as a requirement for this toolkit.

```sh
# For example, if I want to use Spark 1.6.3 I would build the image as follows:
docker build \
    --build-arg SPARK_VERSION_KEY=spark-1.6.3-bin-hadoop2.6 \
    -t <my_image_tag> .
```

**SPARK_VERSION_KEY** is used to locate which version of Spark to download. These are the values that have been tested and known to work:
- spark-1.6.3-bin-hadoop2.6
- spark-2.1.0-bin-hadoop2.7
- spark-2.2.0-bin-hadoop2.7

For a full list of supported keys, please see this [page](https://d3kbcqa49mib13.cloudfront.net)

NOTE: Do not include the '.tgz' suffix as part of the Spark version key.
