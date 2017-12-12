# R
This Dockerfile is used to build the __aztk-r__ Docker image used by this toolkit. This image uses CRAN R3.4.1, RStudio-Server v1.1.383, SparklyR and comes packaged with Tidyverse.

You can modify these Dockerfiles to build your own image. However, in mose cases, building on top of the __aztk-base__ image is recommended.

NOTE: If you plan to use RStudio-Server, hosted on the Spark cluster's master node, with your Spark cluster, we recommend using this image. 

## How to build this image
This Dockerfile takes in a variable at build time that allow you to specify your desired R version: **R_VERSION** 

By default, we set **R_VERSION=3.4.1**.

For example, if I wanted to use R v3.4.0 with Spark v2.1.0, I would select the appropriate Dockerfile and build the image as follows:
```sh
# spark2.1.0/Dockerfile
docker build \
    --build-arg R_VERSION=3.4.0 \
    -t <my_image_tag> .
```

**R_VERSION** is used to set the version of R for your cluster. 

NOTE: Most versions of R will work. However, when selecting your R version, please make sure that the it is compatible with your selected version of Spark.
